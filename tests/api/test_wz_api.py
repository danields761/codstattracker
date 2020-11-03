from functools import lru_cache
from importlib.resources import read_text
from unittest.mock import Mock, call

from _pytest.mark import param
from pytest import fixture, mark, raises
from requests import Response, Session

from codstattracker.api.exceptions import (
    FetchError,
    PlayerNotFoundError,
    UnrecoverableFetchError,
)
from codstattracker.api.models import Game, PlayerID
from codstattracker.api.mycallofduty.mw import PlayerAPI
from tests.api import assets
from tests.api.assets import MATCH_1_IN, MATCH_1_OUT, MATCH_2_IN, MATCH_2_OUT


@lru_cache
def get_asset_file(filename: str) -> str:
    return read_text(assets, filename)


def response_mock(body, status_code):
    resp = Mock(Response, name='response')
    resp.status_code = status_code
    resp.encoding = 'utf-8'
    resp.text = resp.content = body
    resp.json = lambda **kwargs: Response.json(resp, **kwargs)
    return resp


@fixture
def request_session():
    return Mock(Session, name='request_session')


@mark.parametrize(
    'game, url, response, result',
    [
        param(
            Game.mw_mp,
            (
                'http://fake-host/api'
                '/platform/battle/gamer/test_user%231234/matches'
                '/mp/start/0/end/0/details'
            ),
            MATCH_1_IN,
            MATCH_1_OUT,
            id='Parse MP matches',
        ),
        param(
            Game.mw_wz,
            (
                'http://fake-host/api'
                '/platform/battle/gamer/test_user%231234/matches'
                '/wz/start/0/end/0/details'
            ),
            MATCH_2_IN,
            MATCH_2_OUT,
            id='Parse WZ matches',
        ),
    ],
)
def test_parses_successful_response(
    game, url, response, result, request_session
):
    request_session.get.return_value = response_mock(response, 200)
    api = PlayerAPI(request_session, 'http://fake-host/api')

    matches = api.get_recent_matches(
        game, PlayerID('battle', 'test_user', '1234')
    )

    assert request_session.get.mock_calls == [call(url)]
    assert matches == [result]


@mark.parametrize(
    'response_body, exc_cls, exc_args',
    [
        param(
            get_asset_file('user-not-found-response.json'),
            PlayerNotFoundError,
            (),
            id='Received error response',
        ),
        param(
            'something meaningful',
            UnrecoverableFetchError,
            (
                'API response is not a JSON, make '
                'sure url or other params are valid',
            ),
            id='Where API response provides some JSON in unknown format',
        ),
        (
            '{"some": "value"}',
            UnrecoverableFetchError,
            ('Incorrect response received', {'some': 'value'}),
        ),
        param(
            get_asset_file('success-response-a-bit-broken.json'),
            FetchError,
            ('Player info decode error',),
            id='Response generally valid but a bit broken',
        ),
    ],
)
def test_errors(request_session, response_body, exc_cls, exc_args):
    request_session.get.return_value = response_mock(response_body, 200)
    api = PlayerAPI(request_session, 'http://fake-host/api')
    with raises(exc_cls) as exc_info:
        api.get_recent_matches(
            Game.mw_mp, PlayerID('test_user', '1234', 'battle')
        )
    assert exc_info.value.args == exc_args
