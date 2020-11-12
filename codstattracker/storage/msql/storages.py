from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Optional,
    Sequence,
    Type,
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
from codstattracker.storage.exceptions import StorageIOError
from codstattracker.storage.interfaces import LoadStorage as _LoadStorage
from codstattracker.storage.interfaces import SaveStorage as _SaveStorage
from codstattracker.storage.msql.ext import Session
from codstattracker.storage.msql.models import (
    GameModel,
    PlayerMatchModel,
    PlayerModel,
    WeaponStatsModel,
)

SC = TypeVar('SC', _LoadStorage, _SaveStorage)
C = TypeVar('C', bound=Callable)


class StorageContext(Generic[SC]):
    def __init__(self, client: Engine, storage_cls: Type[SC]):
        self._engine = client
        self._storage_cls = storage_cls

    @contextmanager
    def __call__(self) -> Generator[SC, None, None]:
        session = Session(self._engine)
        try:
            yield self._storage_cls(session)
            if issubclass(self._storage_cls, SaveStorage):
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
    def __init__(self, session: Session):
        self._session = session

    def _model_to_db(
        self, match: PlayerMatch, player: PlayerModel
    ) -> PlayerMatchModel:
        def inner(
            game: Game,
            stats: MatchStats,
            weapon_stats: Sequence[WeaponStats],
            **match_kwargs: Any,
        ) -> PlayerMatchModel:
            game = self._session.upsert(GameModel, **game.as_dict_flat())

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

    @_reraise_disconnection_error
    def save_match_series(
        self,
        player_id: PlayerID,
        match_series: Sequence[PlayerMatch],
    ) -> None:
        player = self._session.upsert(PlayerModel, **player_id.as_dict_flat())

        self._session.add_all(
            self._model_to_db(match, player) for match in match_series
        )