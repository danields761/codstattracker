from datetime import datetime, timedelta
from typing import Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel as _BaseModel
from pydantic.generics import GenericModel

from codstattracker.api.models import (
    BattleRoyaleStats,
    Game,
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
        nemesis: Optional[str] = None
        most_killed: Optional[str] = None
        killstreak_usage: Dict[str, int] = {}

    class PlayerStats(BaseResponse):
        kills: int
        assists: int
        deaths: int
        longest_streak: int
        suicides: int = 0
        executions: int
        damage_done: int
        damage_taken: int
        percent_time_moving: float
        shots_fired: int = 0
        shots_landed: int = 0
        shots_missed: int = 0
        headshots: int
        wall_bangs: int
        time_played: int
        distance_traveled: float
        average_speed_during_match: float = 0.0
        team_placement: int = -1

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
    game_type: str
    duration: int
    result: Optional[str] = None
    winning_team: Optional[str] = None
    player_count: Optional[int] = None
    team_count: Optional[int] = None

    player: Player
    player_stats: PlayerStats
    weapon_stats: Dict[str, WeaponStats] = {}


class MatchesDataResponse(BaseResponse):
    matches: List[MatchResponse]


def convert_api_resp_to_player_match(
    api_resp: MatchResponse, game: Game
) -> PlayerMatch:
    ps = api_resp.player_stats
    if api_resp.game_type == 'wz':
        br_stats = BattleRoyaleStats(
            teams_count=api_resp.team_count,
            players_count=api_resp.player_count,
            placement=api_resp.player_stats.team_placement,
        )
        is_win = api_resp.player_stats.team_placement == 1
    else:
        br_stats = None
        is_win = api_resp.winning_team == api_resp.player.team

    return PlayerMatch(
        id=api_resp.match_id,
        game=game,
        start=datetime.utcfromtimestamp(api_resp.utc_start_seconds),
        end=datetime.utcfromtimestamp(api_resp.utc_end_seconds),
        map=api_resp.map,
        is_win=is_win,
        br_stats=br_stats,
        stats=MatchStats(
            kills=ps.kills,
            assists=ps.assists,
            deaths=ps.deaths,
            kd_ratio=ps.kills / (ps.deaths if ps.deaths else 1),
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
