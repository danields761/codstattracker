from datetime import datetime, timedelta
from typing import Sequence, Protocol, Optional


class PlayerID(Protocol):
    id: str
    platform: str


class Player(Protocol):
    id: PlayerID
    nickname: str


class PlayerMatchStats(Protocol):
    kills: int
    assists: int
    death: int
    longest_streak: int
    suicides: int
    executions: int
    damage_dealt: int
    damage_received: int
    distance_traveled: int

    time_played: timedelta


class PlayerGameMatch(Protocol):
    id: str
    start: datetime
    end: datetime
    map: str
    mode: str
    is_win: bool


class PlayerAPI:
    def get_base_info(self, player_id: PlayerID) -> Player:
        raise NotImplementedError

    def get_recent_matches(
        self,
        player_id: PlayerID,
        from_: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Sequence[PlayerGameMatch]:
        raise NotImplementedError
