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
    kd_ration: float
    killstreaks_used: Sequence[str]
    longest_streak: int
    suicides: int
    executions: int
    damage_dealt: int
    damage_received: int
    percent_time_moved: float
    shots_fired: int
    shots_missed: int
    headshots: int
    wall_bangs: int
    time_played: timedelta
    distance_traveled: float
    average_speed: float


class PlayerWeaponMatchStats(Protocol):
    name: str
    hits: int
    kills: int
    death: int
    shots: int
    hits: int
    headshots: int


class PlayerGameMatch(Protocol):
    id: str
    start: datetime
    end: datetime
    map: str
    mode: str
    is_win: bool
    general_stats: PlayerMatchStats
    weapon_stats: PlayerWeaponMatchStats


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
