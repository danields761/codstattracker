from datetime import datetime
from typing import Protocol, Sequence, Optional

from codstattracker.poller.interfaces import PlayerGameMatch


class SaveStorage(Protocol):
    def save_match_series(self, match_series: Sequence[PlayerGameMatch]):
        raise NotImplementedError


class LoadStorage(Protocol):
    def load_series(
        self, from_: Optional[datetime], until: Optional[datetime]
    ) -> Sequence[PlayerGameMatch]:
        raise NotImplementedError
