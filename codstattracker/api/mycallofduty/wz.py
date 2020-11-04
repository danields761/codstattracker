from datetime import datetime, timedelta, timezone
from enum import Enum
from json import JSONDecodeError
from typing import Sequence, Optional, TypeVar, Any, Generic
from urllib.parse import quote

from pydantic import BaseModel as _BaseModel, ValidationError
from pydantic.generics import GenericModel
from requests import RequestException, Session, Response

from codstattracker.api.exceptions import (
    FetchError,
    PlayerNotFoundError,
    UnrecoverableFetchError,
)
from codstattracker.api.interfaces import (
    PlayerGameMatch,
    PlayerID,
    PlayerMatchStats,
    PlayerWeaponMatchStats,
)


class GameMode(str, Enum):
    warzone = 'wz'
    multiplayer = 'mp'


DT = TypeVar('DT')


class ResponseBody(GenericModel, Generic[DT]):
    status: str
    data: DT


class BaseModel(_BaseModel):
    class Config:
        @staticmethod
        def alias_generator(snake_str):
            components = snake_str.split('_')
            return components[0] + ''.join(x.title() for x in components[1:])


class ErrorData(BaseModel):
    message: str


class MatchModel(BaseModel):
    class Config:
        fields = {'match_id': {'alias': 'matchID'}}

    class Player(BaseModel):
        team: str
        nemesis: str
        most_killed: str
        killstreak_usage: dict[str, int]

    class PlayerStats(BaseModel):
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

    class WeaponStats(BaseModel):
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
    weapon_stats: dict[str, WeaponStats]

    def convert(self) -> PlayerGameMatch:
        ps = self.player_stats
        return PlayerGameMatch(
            id=self.match_id,
            start=datetime.utcfromtimestamp(self.utc_start_seconds),
            end=datetime.utcfromtimestamp(self.utc_end_seconds),
            map=self.map,
            is_win=self.winning_team == self.player.team,
            general_stats=PlayerMatchStats(
                kills=ps.kills,
                assists=ps.assists,
                deaths=ps.deaths,
                kd_ratio=ps.kills / ps.deaths,
                killstreaks_used=list(self.player.killstreak_usage),
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
                PlayerWeaponMatchStats(
                    name=weapon_name,
                    hits=weapon_stat.hits,
                    kills=weapon_stat.kills,
                    deaths=weapon_stat.deaths,
                    shots=weapon_stat.shots,
                    headshots=weapon_stat.headshots,
                )
                for weapon_name, weapon_stat in self.weapon_stats.items()
            ],
        )


class MatchesDataModel(BaseModel):
    matches: list[MatchModel]


def _player_id_as_user_name(player_id: PlayerID) -> str:
    return quote(f'{player_id.nickname}#{player_id.id}')


def _datetime_as_utctimestamp(dt: datetime) -> int:
    return int(dt.astimezone(timezone.utc).timestamp())


class PlayerAPI:
    API_HOST = 'https://my.callofduty.com'
    BASE_API_SUFFIX = '/api/papi-client/crm/cod/v2/title/mw'
    PROFILE_INFO_URL_PATTERN = '/platform/{pf}/gamer/{un}/profile/type/{gm}'
    MATCH_HISTORY_URL_PATTERN = (
        '/platform/{pf}/gamer/{un}/matches/'
        '{gm}/start/{start}/end/{end}/details'
    )

    def __init__(
        self,
        authorized_session: Session,
        game_mode: GameMode,
        base_api_url: Optional[str] = None,
    ):
        self._session = authorized_session
        self._game_mode = game_mode
        self._base_api_url = base_api_url or (
            self.API_HOST + self.BASE_API_SUFFIX
        )

    @staticmethod
    def _raise_if_resp_error(response: Response) -> dict[str, Any]:
        try:
            body = response.json()
        except JSONDecodeError:
            raise UnrecoverableFetchError(
                'API response is not a JSON, '
                'make sure url or other params is valid'
            )

        if body.get('status') != 'success':
            try:
                error = ResponseBody[ErrorData].parse_obj(body)
            except ValidationError:
                raise UnrecoverableFetchError(
                    'Incorrect response received', body
                )

            player_not_found_err = 'user not found' in error.data.message
            if player_not_found_err:
                raise PlayerNotFoundError()
            raise FetchError(error.data.message or body)

        return body

    def get_recent_matches(
        self,
        player_id: PlayerID,
        from_: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Sequence[PlayerGameMatch]:
        start = _datetime_as_utctimestamp(from_) if from_ else 0
        end = _datetime_as_utctimestamp(until) if until else 0
        url = (self._base_api_url + self.MATCH_HISTORY_URL_PATTERN).format(
            pf=quote(player_id.platform),
            un=_player_id_as_user_name(player_id),
            gm=self._game_mode,
            start=start,
            end=end,
        )

        try:
            response = self._session.get(url)
        except RequestException:
            raise FetchError

        body = self._raise_if_resp_error(response)
        parsed_data = ResponseBody[MatchesDataModel].parse_obj(body)
        return [match.convert() for match in parsed_data.data.matches]
