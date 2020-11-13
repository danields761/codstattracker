from __future__ import annotations

from datetime import datetime, timezone
from json import JSONDecodeError
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence
from urllib.parse import quote

from pydantic import ValidationError
from requests import RequestException, Response, Session

from codstattracker import logging
from codstattracker.api.exceptions import (
    FetchError,
    PlayerNotFoundError,
    UnrecoverableFetchError,
)
from codstattracker.api.interfaces import PlayerAPI as _PlayerAPI
from codstattracker.api.models import Game, PlayerID, PlayerMatch
from codstattracker.api.mycallofduty.models import (
    ErrorData,
    MatchesDataResponse,
    ResponseBody,
    convert_api_resp_to_player_match,
)

if TYPE_CHECKING:
    from loguru import Logger


def _player_id_as_user_name(player_id: PlayerID) -> str:
    return quote(f'{player_id.nickname}#{player_id.id}')


def _datetime_as_utctimestamp(dt: datetime) -> int:
    return int(dt.astimezone(timezone.utc).timestamp())


class PlayerAPI(_PlayerAPI):
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
        base_api_url: Optional[str] = None,
        logger: Logger = logging.default,
    ):
        self._session = authorized_session
        self._base_api_url = base_api_url or (
            self.API_HOST + self.BASE_API_SUFFIX
        )
        self._logger = logger

    @staticmethod
    def _raise_if_resp_error(response: Response) -> Dict[str, Any]:
        try:
            body = response.json()
        except JSONDecodeError:
            raise UnrecoverableFetchError(
                'API response is not a JSON, '
                'make sure url or other params are valid'
            )

        if body.get('status') != 'success':
            try:
                error = ResponseBody[ErrorData].parse_obj(body)
            except ValidationError:
                raise UnrecoverableFetchError(
                    'Incorrect response received', body
                )

            if 'not authenticated ' in error.data.message:
                raise UnrecoverableFetchError('Access not authorized', body)

            player_not_found_err = 'user not found' in error.data.message
            if player_not_found_err:
                raise PlayerNotFoundError()
            raise FetchError(error.data.message or body)

        return body

    def get_recent_matches(
        self,
        game: Game,
        player_id: PlayerID,
        from_: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Sequence[PlayerMatch]:
        if game.name != 'mw':
            raise ValueError('Only Modern Warfare 2019 is supported now')
        if game.mode not in ('wz', 'mp'):
            raise ValueError('Unknown game mode given')

        log = self._logger.bind(game=game, player_id=player_id)

        start = _datetime_as_utctimestamp(from_) if from_ else 0
        end = _datetime_as_utctimestamp(until) if until else 0
        url = (self._base_api_url + self.MATCH_HISTORY_URL_PATTERN).format(
            pf=quote(player_id.platform),
            un=_player_id_as_user_name(player_id),
            gm=game.mode,
            start=start,
            end=end,
        )

        log.debug('Requesting url', url=url)
        try:
            response = self._session.get(url)
        except RequestException as exc:
            log.debug('Exception occurs', exc=exc)
            raise FetchError

        try:
            body = self._raise_if_resp_error(response)
        except FetchError:
            log.warning('Error caused by content', content=response.content)
            raise

        try:
            parsed_data = ResponseBody[MatchesDataResponse].parse_obj(body)
        except ValidationError:
            log.warning('Info decode failed', body=body)
            raise FetchError('Player info decode error')

        return [
            convert_api_resp_to_player_match(match)
            for match in parsed_data.data.matches
        ]
