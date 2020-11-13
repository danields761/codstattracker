from __future__ import annotations

from datetime import datetime, timedelta
from typing import Sequence

from codstattracker.base_model import Model


class Game(Model):
    name: str
    mode: str

    def __repr__(self) -> str:
        return f'{self.name}:{self.mode}'


MW_MULTIPLAYER = Game(name='mw', mode='mp')
MW_WARZONE = Game(name='mw', mode='wz')


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


class PlayerMatch(Model):
    id: str
    game: Game
    start: datetime
    end: datetime
    map: str
    is_win: bool
    stats: MatchStats
    weapon_stats: Sequence[WeaponStats]
