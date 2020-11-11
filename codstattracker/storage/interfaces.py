from datetime import datetime
from typing import (
    Callable,
    ContextManager,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
)

from codstattracker.api.models import Game, PlayerID, PlayerMatch

SC = TypeVar('SC')


StorageContext = Callable[[], ContextManager[SC]]


class SaveStorage(Protocol):
    def save_match_series(
        self, player_id: PlayerID, match_series: Sequence[PlayerMatch]
    ) -> None:
        raise NotImplementedError


class LoadStorage(Protocol):
    def load_last_matches(
        self,
        game: Game,
        player_id: PlayerID,
        from_: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Sequence[PlayerMatch]:
        raise NotImplementedError
