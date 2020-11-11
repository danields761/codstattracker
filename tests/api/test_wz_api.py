from datetime import datetime, timedelta
from functools import lru_cache
from importlib.resources import read_text
from unittest.mock import Mock, call

from pytest import fixture, mark, raises
from requests import Response, Session

from codstattracker.api.exceptions import (
    PlayerNotFoundError,
    UnrecoverableFetchError,
)
from codstattracker.api.models import (
    MW_MULTIPLAYER,
    MatchStats,
    PlayerID,
    PlayerMatch,
    WeaponStats,
)
from codstattracker.api.mycallofduty.mw import PlayerAPI
from tests.api import assets


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


def test_parses_successful_response(request_session):
    request_session.get.return_value = response_mock(
        get_asset_file('success-response.json'), 200
    )
    api = PlayerAPI(request_session, 'http://fake-host/api')
    matches = api.get_recent_matches(
        MW_MULTIPLAYER, PlayerID('battle', 'test_user', '1234')
    )

    assert request_session.get.mock_calls == [
        call(
            'http://fake-host/api'
            '/platform/battle/gamer/test_user%231234/matches'
            '/mp/start/0/end/0/details'
        )
    ]

    assert matches == [
        PlayerMatch(
            id='8133155045257161843',
            game=MW_MULTIPLAYER,
            start=datetime.utcfromtimestamp(1604354327),
            end=datetime.utcfromtimestamp(1604354859),
            map='mp_m_speed',
            is_win=True,
            stats=MatchStats(
                kills=46,
                assists=7,
                deaths=23,
                kd_ratio=46 / 23,
                killstreaks_used=[],
                longest_streak=10,
                suicides=0,
                executions=0,
                damage_dealt=5053,
                damage_received=3574,
                percent_time_moved=99.04762,
                shots_fired=955,
                shots_missed=762,
                headshots=6,
                wall_bangs=1,
                time_played=timedelta(seconds=583),
                distance_traveled=7522.9775,
                average_speed=234.35248,
            ),
            weapon_stats=[
                WeaponStats(
                    name='iw8_ar_mike4',
                    hits=59,
                    kills=14,
                    deaths=10,
                    shots=271,
                    headshots=1,
                ),
                WeaponStats(
                    name='iw8_sm_mpapa5',
                    hits=134,
                    kills=33,
                    deaths=13,
                    shots=684,
                    headshots=5,
                ),
            ],
        )
    ]


@mark.parametrize(
    'response_body, exc_cls, exc_args',
    [
        (
            get_asset_file('user-not-found-response.json'),
            PlayerNotFoundError,
            (),
        ),
        (
            'something meaningful',
            UnrecoverableFetchError,
            (
                'API response is not a JSON, make '
                'sure url or other params are valid',
            ),
        ),
        (
            '{"some": "value"}',
            UnrecoverableFetchError,
            ('Incorrect response received', {'some': 'value'}),
        ),
    ],
)
def test_errors(request_session, response_body, exc_cls, exc_args):
    request_session.get.return_value = response_mock(response_body, 200)
    api = PlayerAPI(request_session, 'http://fake-host/api')
    with raises(exc_cls) as exc_info:
        api.get_recent_matches(
            MW_MULTIPLAYER, PlayerID('test_user', '1234', 'battle')
        )

    assert exc_info.value.args == exc_args
