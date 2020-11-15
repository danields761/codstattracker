from codstattracker.api.models import Game, PlayerID
from codstattracker.storage.sql.models import PlayerMatchModel, PlayerModel
from tests.storage.sql.utils import random_match_model


def test_matches_filterable_by_player_id(session):
    player = PlayerModel(
        db_id=1, platform='battle', id='1234', nickname='test'
    )
    match = random_match_model('test_match', Game.mw_mp, player)
    session.add(match)
    session.add(
        random_match_model(
            'should_not_be_visible',
            Game.mw_mp,
            PlayerModel(
                platform='battle', id='another_id', nickname='another_nickname'
            ),
        )
    )
    session.flush()
    session.expunge(match)

    new_match = (
        session.query(PlayerMatchModel)
        .filter(PlayerMatchModel.player == PlayerID(**player.as_dict_flat()))
        .one()
    )
    assert match.id == new_match.id
    assert (
        session.query(PlayerMatchModel)
        .filter(PlayerMatchModel.id == 'test_match')
        .filter(PlayerMatchModel.player == PlayerID(**player.as_dict_flat()))
        .one()
        .id
        == 'test_match'
    )
