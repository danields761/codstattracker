from datetime import datetime, timedelta
from typing import Dict, Generic, List, TypeVar

from pydantic import BaseModel as _BaseModel
from pydantic.generics import GenericModel

from codstattracker.api.models import (
    MW_MULTIPLAYER,
    MatchStats,
    PlayerMatch,
    WeaponStats,
)

DT = TypeVar('DT')


class ResponseBody(GenericModel, Generic[DT]):
    status: str
    data: DT


class BaseResponse(_BaseModel):
    class Config:
        @staticmethod
        def alias_generator(snake_str):
            components = snake_str.split('_')
            return components[0] + ''.join(x.title() for x in components[1:])


class ErrorData(BaseResponse):
    message: str


class MatchResponse(BaseResponse):
    class Config:
        fields = {'match_id': {'alias': 'matchID'}}

    class Player(BaseResponse):
        team: str
        nemesis: str
        most_killed: str
        killstreak_usage: Dict[str, int]

    class PlayerStats(BaseResponse):
        kills: int
        assists: int
        deaths: int
        longest_streak: int
        suicides: int
        executions: int
        damage_done: int
        damage_taken: int
        percent_time_moving: float
        shots_fired: int
        shots_landed: int
        shots_missed: int
        headshots: int
        wall_bangs: int
        time_played: int
        distance_traveled: float
        average_speed_during_match: float

    class WeaponStats(BaseResponse):
        hits: int
        shots: int
        kills: int
        deaths: int
        headshots: int
        loadout_index: int

    match_id: str
    utc_start_seconds: int
    utc_end_seconds: int
    map: str
    duration: int
    result: str
    winning_team: str

    player: Player
    player_stats: PlayerStats
    weapon_stats: Dict[str, WeaponStats]


class MatchesDataResponse(BaseResponse):
    matches: List[MatchResponse]


def convert_api_resp_to_player_match(api_resp: MatchResponse) -> PlayerMatch:
    ps = api_resp.player_stats
    return PlayerMatch(
        id=api_resp.match_id,
        game=MW_MULTIPLAYER,
        start=datetime.utcfromtimestamp(api_resp.utc_start_seconds),
        end=datetime.utcfromtimestamp(api_resp.utc_end_seconds),
        map=api_resp.map,
        is_win=api_resp.winning_team == api_resp.player.team,
        stats=MatchStats(
            kills=ps.kills,
            assists=ps.assists,
            deaths=ps.deaths,
            kd_ratio=ps.kills / ps.deaths,
            killstreaks_used=list(api_resp.player.killstreak_usage),
            longest_streak=ps.longest_streak,
            suicides=ps.suicides,
            executions=ps.executions,
            damage_dealt=ps.damage_done,
            damage_received=ps.damage_taken,
            percent_time_moved=ps.percent_time_moving,
            shots_fired=ps.shots_fired,
            shots_missed=ps.shots_missed,
            headshots=ps.headshots,
            wall_bangs=ps.wall_bangs,
            time_played=timedelta(seconds=ps.time_played),
            distance_traveled=ps.distance_traveled,
            average_speed=ps.average_speed_during_match,
        ),
        weapon_stats=[
            WeaponStats(
                name=weapon_name,
                hits=weapon_stat.hits,
                kills=weapon_stat.kills,
                deaths=weapon_stat.deaths,
                shots=weapon_stat.shots,
                headshots=weapon_stat.headshots,
            )
            for weapon_name, weapon_stat in api_resp.weapon_stats.items()
        ],
    )
