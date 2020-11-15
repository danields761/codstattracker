from __future__ import annotations

from dataclasses import field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Sequence

from codstattracker.base_model import Model


class Game(str, Enum):
    mw_mp = 'mw:mp'
    mw_wz = 'mw:wz'

    @property
    def name(self) -> str:
        name, _ = self.value.split(':')
        return name

    @property
    def mode(self) -> str:
        _, mode = self.value.split(':')
        return mode

    def __repr__(self) -> str:
        return repr(self.value)


class PlayerID(Model, unsafe_hash=True):
    platform: str
    nickname: str
    id: str

    def __repr__(self) -> str:
        return f'{self.platform}:{self.nickname}#{self.id}'


class MatchStats(Model):
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


class WeaponStats(Model):
    name: str
    hits: int
    kills: int
    deaths: int
    shots: int
    hits: int
    headshots: int


class BattleRoyaleStats(Model):
    teams_count: int
    players_count: int
    placement: int


class PlayerMatch(Model):
    id: str
    game: Game
    start: datetime
    end: datetime
    map: str
    is_win: bool
    stats: MatchStats
    weapon_stats: Sequence[WeaponStats] = field(default_factory=list)
    br_stats: Optional[BattleRoyaleStats] = None
