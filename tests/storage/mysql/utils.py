import random
from datetime import datetime, timedelta

from codstattracker.storage.msql.models import PlayerMatchModel


def random_match_model(id_, game_mode, player, start=None, end=None):
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
    return PlayerMatchModel(
        id=id_,
        game=game_mode,
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
