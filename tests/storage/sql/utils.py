import random
from datetime import datetime, timedelta

from codstattracker.api.models import BattleRoyaleStats, Game
from codstattracker.storage.sql.models import PlayerMatchModel


def random_match_model(id_, game, player, start=None, end=None):
    int_fields = (
        'kills',
        'assists',
        'deaths',
        'longest_streak',
        'suicides',
        'executions',
        'damage_dealt',
        'damage_received',
        'shots_fired',
        'shots_missed',
        'headshots',
        'wall_bangs',
    )
    float_fields = (
        'percent_time_moved',
        'distance_traveled',
        'average_speed',
        'kd_ratio',
    )
    if start and end:
        duration = end - start
    elif not start and not end:
        start = datetime.utcfromtimestamp(
            random.randint(1264118400, 1264218400)
        )
        duration = timedelta(seconds=random.randint(100, 10000))
        end = start + duration
    else:
        raise ValueError(
            'Either start and end args must be defined or omitted'
        )

    if game is Game.mw_wz:
        br_stats = BattleRoyaleStats(75, 150, random.randint(1, 150))
    else:
        br_stats = None

    return PlayerMatchModel(
        id=id_,
        game=game,
        br_stats=br_stats,
        player=player,
        is_win=random.choice((False, True)),
        weapon_stats=[],
        killstreaks_used=[],
        start=start,
        end=end,
        time_played=duration,
        map=random.choice(('shipment', 'shoot_house', 'rust')),
        **{int_field: random.randint(0, 50) for int_field in int_fields},
        **{
            float_field: random.uniform(0, 100) for float_field in float_fields
        },
    )
