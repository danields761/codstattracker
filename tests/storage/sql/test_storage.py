import copy
from datetime import datetime, timedelta

from pytest import fixture, mark

from codstattracker.api.models import Game, PlayerID
from codstattracker.storage.sql.models import (
    PlayerMatchLogModel,
    PlayerMatchModel,
    PlayerModel,
)
from codstattracker.storage.sql.storages import LoadStorage, SaveStorage
from tests.storage.sql.utils import random_match_model

PLAYER_1_ID = PlayerID(platform='battle', nickname='p1', id='1234')


@fixture
def players():
    return (
        PlayerModel(**PLAYER_1_ID.as_dict_flat()),
        PlayerModel(db_id=2, platform='ps', nickname='p2', id='4321'),
    )


@fixture
def matches(players, session_ctx):
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
            f'match_{p_num}_{match_num}', Game.mw_mp, player, start, end
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
            PLAYER_1_ID,
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
    result = load_storage.load_last_matches(Game.mw_mp, player_id)
    assert [match.id for match in result] == matches_ids


@mark.parametrize(
    'player_id, start, end, matches_ids',
    [
        (
            PLAYER_1_ID,
            datetime(year=2010, month=1, day=1, hour=12, minute=0, second=0),
            datetime(year=2010, month=1, day=1, hour=12, minute=10, second=0),
            ['match_0_0'],
        ),
        (
            PLAYER_1_ID,
            datetime(year=2010, month=1, day=1, hour=12, minute=0, second=0),
            datetime(year=2010, month=1, day=1, hour=12, minute=20, second=0),
            ['match_0_0', 'match_0_1'],
        ),
        (
            PLAYER_1_ID,
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
    matches, load_storage, player_id, start, end, matches_ids
):
    result = load_storage.load_last_matches(Game.mw_mp, player_id, start, end)
    assert [match.id for match in result] == matches_ids


def test_saves_match_stats(matches, save_storage, load_storage):
    save_storage.save_match_series(
        PLAYER_1_ID,
        [
            random_match_model(
                'new_mp_match',
                Game.mw_mp,
                PLAYER_1_ID,
                datetime(
                    year=2010, month=1, day=1, hour=13, minute=0, second=0
                ),
                datetime(
                    year=2010, month=1, day=1, hour=13, minute=30, second=0
                ),
            ),
            random_match_model(
                'new_wz_match',
                Game.mw_wz,
                PLAYER_1_ID,
                datetime(
                    year=2010, month=1, day=1, hour=13, minute=0, second=0
                ),
                datetime(
                    year=2010, month=1, day=1, hour=13, minute=30, second=0
                ),
            ),
        ],
    )

    mp_load_result = load_storage.load_last_matches(Game.mw_mp, PLAYER_1_ID)
    assert [match.id for match in mp_load_result] == [
        'match_0_0',
        'match_0_1',
        'match_0_2',
        'new_mp_match',
    ]
    wz_load_result = load_storage.load_last_matches(Game.mw_wz, PLAYER_1_ID)
    assert [match.id for match in wz_load_result] == ['new_wz_match']


def test_repeated_save_successful(save_storage, session_ctx):
    matches = [
        random_match_model('some_id_1', Game.mw_mp, PLAYER_1_ID),
        random_match_model('some_id_2', Game.mw_mp, PLAYER_1_ID),
        random_match_model('some_id_3', Game.mw_mp, PLAYER_1_ID),
    ]
    with session_ctx() as s:
        SaveStorage(s).save_match_series(
            PLAYER_1_ID, copy.deepcopy(matches[:1])
        )
        s.commit()

    with session_ctx() as s:
        assert len(s.query(PlayerMatchModel).all()) == 1

    with session_ctx() as s:
        SaveStorage(s).save_match_series(PLAYER_1_ID, matches[1:])
        s.commit()


def test_saves_matches_logs(session):
    tracked_match = random_match_model('tracked', Game.mw_mp, PLAYER_1_ID)
    # Assigning instance attribute is enough to satisfy
    #  `runtime_checkable` protocol
    tracked_match.get_entity_info = lambda: (
        {'test': 'data'},
        {'test': 'meta'},
    )
    other_match = random_match_model('other', Game.mw_mp, PLAYER_1_ID)

    save_storage = SaveStorage(session, save_matches_logs=True)
    save_storage.save_match_series(PLAYER_1_ID, [tracked_match, other_match])
    session.commit()

    log_model = session.query(PlayerMatchLogModel).one()
    assert log_model.match_id == 'tracked'
    assert log_model.source == {'test': 'data'}
    assert log_model.meta == {'test': 'meta'}
