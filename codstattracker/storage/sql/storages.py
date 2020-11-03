from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Iterable,
    Optional,
    Sequence,
    TypeVar,
    cast,
)

from sqlalchemy.engine import Engine
from sqlalchemy.exc import DisconnectionError

from codstattracker.api.models import (
    Game,
    MatchStats,
    PlayerID,
    PlayerMatch,
    WeaponStats,
)
from codstattracker.base_model import TrackableEntity
from codstattracker.storage.exceptions import StorageIOError
from codstattracker.storage.interfaces import LoadStorage as _LoadStorage
from codstattracker.storage.interfaces import SaveStorage as _SaveStorage
from codstattracker.storage.sql.ext import Session
from codstattracker.storage.sql.models import (
    PlayerMatchLogModel,
    PlayerMatchModel,
    PlayerModel,
    WeaponStatsModel,
)

SC = TypeVar('SC')
C = TypeVar('C', bound=Callable)


class StorageContext(Generic[SC]):
    def __init__(
        self, client: Engine, storage_factory: Callable[[Session], SC]
    ):
        self._engine = client
        self._storage_cls = storage_factory

    @contextmanager
    def __call__(self) -> Generator[SC, None, None]:
        session = Session(self._engine)
        try:
            yield self._storage_cls(session)
            session.commit()
        except KeyboardInterrupt:
            raise
        finally:
            session.close()


def _reraise_disconnection_error(func: C) -> C:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DisconnectionError:
            raise StorageIOError

    return cast(C, wrapper)


class LoadStorage(_LoadStorage):
    def __init__(self, session: Session):
        self._session = session

    @_reraise_disconnection_error
    def load_last_matches(
        self,
        game: Game,
        player_id: PlayerID,
        from_: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Sequence[PlayerMatch]:
        query = self._session.query(PlayerMatchModel).filter(
            PlayerMatchModel.game == game, PlayerMatchModel.player == player_id
        )
        if from_:
            query = query.filter(PlayerMatchModel.start >= from_)
        if until:
            query = query.filter(PlayerMatchModel.start <= until)

        return query.order_by(PlayerMatchModel.start).all()


class SaveStorage(_SaveStorage):
    def __init__(self, session: Session, save_matches_logs: bool = False):
        self._session = session
        self._save_matches_logs = save_matches_logs

    def _model_to_db(
        self, match: PlayerMatch, player: PlayerModel
    ) -> PlayerMatchModel:
        def inner(
            game: Game,
            stats: MatchStats,
            weapon_stats: Sequence[WeaponStats],
            **match_kwargs: Any,
        ) -> PlayerMatchModel:
            return PlayerMatchModel(
                game=game,
                player=player,
                weapon_stats=[
                    WeaponStatsModel(**stat.as_dict_flat())
                    for stat in weapon_stats
                ],
                **match_kwargs,
                **stats.as_dict_flat(MatchStats),
            )

        return inner(**match.as_dict_flat(PlayerMatch))

    @staticmethod
    def _create_matches_logs(
        matches: Sequence[PlayerMatch],
    ) -> Iterable[PlayerMatchLogModel]:
        for match in matches:
            if not isinstance(match, TrackableEntity):
                continue
            source, meta = match.get_entity_info()
            yield PlayerMatchLogModel(
                match_id=match.id, source=source, meta=meta
            )

    @_reraise_disconnection_error
    def save_match_series(
        self,
        player_id: PlayerID,
        match_series: Sequence[PlayerMatch],
    ) -> None:
        player = self._session.upsert(PlayerModel, **player_id.as_dict_flat())

        matches_exists_ids = set(
            match_id
            for match_id, in self._session.query(PlayerMatchModel.id)
            .filter(
                PlayerMatchModel.id.in_(match.id for match in match_series)
            )
            .all()
        )
        matches_to_add = [
            self._model_to_db(match, player)
            for match in match_series
            if match.id not in matches_exists_ids
        ]
        if not matches_to_add:
            return

        self._session.add_all(matches_to_add)
        if self._save_matches_logs:
            # sqlalchemy unit of work can't order inserts when model
            # relations are not explicit
            self._session.flush()
            self._session.add_all(self._create_matches_logs(match_series))

        self._session.flush()
