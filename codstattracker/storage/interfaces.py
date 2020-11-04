from datetime import datetime
from typing import (
    Callable,
    ContextManager,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
)

from codstattracker.api.interfaces import PlayerGameMatch, PlayerID

S = TypeVar('S')


StorageContext = Callable[[], ContextManager[S]]


class SaveStorage(Protocol):
    def save_match_series(
        self, player_id: PlayerID, match_series: Sequence[PlayerGameMatch]
    ) -> None:
        raise NotImplementedError


class LoadStorage(Protocol):
    def load_last_matches(
        self,
        player_id: PlayerID,
        from_: Optional[datetime],
        until: Optional[datetime],
    ) -> Sequence[PlayerGameMatch]:
        raise NotImplementedError

    def load_last_matches_by_offset(
        self, player_id: PlayerID, tail_index: int, count: int
    ) -> Sequence[PlayerGameMatch]:
        raise NotImplementedError
