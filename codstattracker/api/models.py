from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta
from typing import Any, Iterable, Optional, Sequence, Type


class Model:
    def __init_subclass__(
        cls,
        frozen: bool = False,
        unsafe_hash: bool = False,
        **kwargs,
    ):
        dataclasses.dataclass(cls, frozen=frozen, unsafe_hash=unsafe_hash)

    @classmethod
    def all_fields(cls) -> Iterable[dataclasses.Field]:
        mro = cls.__mro__
        for base in mro:
            try:
                yield from dataclasses.fields(base)
            except TypeError:
                pass

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def as_dict_flat(
        self, as_parent: Optional[Type[Model]] = None
    ) -> dict[str, Any]:
        if as_parent:
            self_cls = type(self)
            mro = set(self_cls.__mro__)
            if as_parent not in mro:
                raise TypeError(
                    f'Given model {as_parent.__name__!r} is not parent of '
                    f'current model {self_cls.__name__!r}'
                )

            all_fields = as_parent.all_fields()
        else:
            all_fields = self.all_fields()

        return {field.name: getattr(self, field.name) for field in all_fields}


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
