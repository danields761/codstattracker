from datetime import datetime, timedelta
from importlib.resources import read_text

from codstattracker.api.models import (
    BattleRoyaleStats,
    Game,
    MatchStats,
    PlayerMatch,
    WeaponStats,
)

MATCH_1_IN = read_text(__package__, 'success-response.json')
MATCH_1_OUT = PlayerMatch(
    id='8133155045257161843',
    game=Game.mw_mp,
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

MATCH_2_IN = read_text(__package__, 'success-response-wz.json')
MATCH_2_OUT = PlayerMatch(
    id='13733821167676440496',
    game=Game.mw_wz,
    start=datetime.utcfromtimestamp(1605354410),
    end=datetime.utcfromtimestamp(1605356002),
    map='mp_don3',
    is_win=False,
    stats=MatchStats(
        kills=12,
        assists=0,
        deaths=2,
        kd_ratio=6,
        killstreaks_used=[],
        longest_streak=8,
        suicides=0,
        executions=0,
        damage_dealt=3920,
        damage_received=534,
        percent_time_moved=97.75171,
        shots_fired=0,
        shots_missed=0,
        headshots=1,
        wall_bangs=0,
        time_played=timedelta(seconds=1103),
        distance_traveled=597077.3,
        average_speed=0.0,
    ),
    br_stats=BattleRoyaleStats(
        teams_count=77, players_count=150, placement=16
    ),
    weapon_stats=[],
)
