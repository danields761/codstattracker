import copy
from datetime import datetime, timedelta

from pytest import fixture, mark

from codstattracker.api.models import MW_MULTIPLAYER, PlayerID
from codstattracker.storage.msql.models import PlayerMatchModel, PlayerModel
from codstattracker.storage.msql.storages import LoadStorage, SaveStorage
from tests.storage.mysql.utils import random_match_model


@fixture
def players():
    return (
        PlayerModel(db_id=1, platform='battle', nickname='p1', id='1234'),
        PlayerModel(db_id=2, platform='ps', nickname='p2', id='4321'),
    )


@fixture
def matches(players, game_mode, session_ctx):
    first_match_time = datetime(
        year=2010, month=1, day=1, hour=12, minute=0, second=0
    )
    match_duration = timedelta(minutes=10)
    matches_per_player = 3
    matches_timings = [(first_match_time, first_match_time + match_duration)]
    for i in range(1, matches_per_player):
        prev_match_start, _ = matches_timings[-1]
        match_start = prev_match_start + 2 * match_duration
        matches_timings.append((match_start, match_start + match_duration))

    matches = [
        random_match_model(
            f'match_{p_num}_{match_num}', game_mode, player, start, end
        )
        for p_num, player in enumerate(players)
        for match_num, (start, end) in enumerate(matches_timings)
    ]
    with session_ctx() as s:
        s.add_all(matches)
        s.flush()
        s.expunge_all()
        s.commit()
    return matches


@fixture
def load_storage(session):
    return LoadStorage(session)


@fixture
def save_storage(session):
    return SaveStorage(session)


@mark.parametrize(
    'player_id, matches_ids',
    [
        (
            PlayerID(platform='battle', nickname='p1', id='1234'),
            [
                'match_0_0',
                'match_0_1',
                'match_0_2',
            ],
        ),
        (
            PlayerID(platform='ps', nickname='p2', id='4321'),
            [
                'match_1_0',
                'match_1_1',
                'match_1_2',
            ],
        ),
    ],
)
def test_load_storage(matches, load_storage, player_id, matches_ids):
    result = load_storage.load_last_matches(MW_MULTIPLAYER, player_id)
    assert [match.id for match in result] == matches_ids


@mark.parametrize(
    'player_id, start, end, matches_ids',
    [
        (
            PlayerID(platform='battle', nickname='p1', id='1234'),
            datetime(year=2010, month=1, day=1, hour=12, minute=0, second=0),
            datetime(year=2010, month=1, day=1, hour=12, minute=10, second=0),
            ['match_0_0'],
        ),
        (
            PlayerID(platform='battle', nickname='p1', id='1234'),
            datetime(year=2010, month=1, day=1, hour=12, minute=0, second=0),
            datetime(year=2010, month=1, day=1, hour=12, minute=20, second=0),
            ['match_0_0', 'match_0_1'],
        ),
        (
            PlayerID(platform='battle', nickname='p1', id='1234'),
            datetime(year=2010, month=1, day=1, hour=12, minute=20, second=0),
            datetime(year=2010, month=1, day=1, hour=12, minute=50, second=0),
            ['match_0_1', 'match_0_2'],
        ),
        (
            PlayerID(platform='ps', nickname='p2', id='4321'),
            datetime(year=2010, month=1, day=1, hour=12, minute=20, second=0),
            datetime(year=2010, month=1, day=1, hour=12, minute=50, second=0),
            ['match_1_1', 'match_1_2'],
        ),
    ],
)
def test_load_storage_by_time_ranges(
    game_mode, matches, load_storage, player_id, start, end, matches_ids
):
    result = load_storage.load_last_matches(game_mode, player_id, start, end)
    assert [match.id for match in result] == matches_ids


def test_saves_match_stats(matches, save_storage, load_storage):
    player = PlayerID(platform='battle', nickname='p1', id='1234')
    save_storage.save_match_series(
        player,
        [
            random_match_model(
                'new_match',
                MW_MULTIPLAYER,
                player,
                datetime(
                    year=2010, month=1, day=1, hour=13, minute=0, second=0
                ),
                datetime(
                    year=2010, month=1, day=1, hour=13, minute=30, second=0
                ),
            ),
        ],
    )

    load_result = load_storage.load_last_matches(MW_MULTIPLAYER, player)
    assert [match.id for match in load_result] == [
        'match_0_0',
        'match_0_1',
        'match_0_2',
        'new_match',
    ]


def test_saves_same_matches_successfully(save_storage, game_mode, session_ctx):
    player = PlayerID(platform='battle', nickname='p1', id='1234')
    matches = [
        random_match_model('some_id_1', game_mode, player),
        random_match_model('some_id_2', game_mode, player),
        random_match_model('some_id_3', game_mode, player),
    ]
    with session_ctx() as s:
        SaveStorage(s).save_match_series(player, copy.deepcopy(matches[:1]))
        s.commit()

    with session_ctx() as s:
        assert len(s.query(PlayerMatchModel).all()) == 1

    with session_ctx() as s:
        SaveStorage(s).save_match_series(player, matches[1:])
        s.commit()
