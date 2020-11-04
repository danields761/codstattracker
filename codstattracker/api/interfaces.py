from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Sequence


@dataclass
class PlayerID:
    nickname: str
    id: str
    platform: str

    def __repr__(self) -> str:
        return f'{self.platform}:{self.nickname}#{self.id}'


@dataclass
class PlayerMatchStats:
    kills: int
    assists: int
    deaths: int
    kd_ratio: float
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


@dataclass
class PlayerWeaponMatchStats:
    name: str
    hits: int
    kills: int
    deaths: int
    shots: int
    hits: int
    headshots: int


@dataclass
class PlayerGameMatch:
    id: str
    start: datetime
    end: datetime
    map: str
    is_win: bool
    general_stats: PlayerMatchStats
    weapon_stats: Sequence[PlayerWeaponMatchStats]


class PlayerAPI:
    def get_recent_matches(
        self,
        player_id: PlayerID,
        from_: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Sequence[PlayerGameMatch]:
        """

        :param player_id:
        :param from_:
        :param until:
        :return:
        :raises FetchError:
        :raises UnrecoverableFetchError:
        """
        raise NotImplementedError
