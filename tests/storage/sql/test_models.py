from codstattracker.api.models import Game, PlayerID
from codstattracker.storage.sql.models import PlayerMatchModel, PlayerModel
from tests.storage.sql.utils import random_match_model


def test_matches_filterable_by_player_id(session):
    player1 = PlayerModel(platform='battle', id='1234', nickname='test')
    player2 = PlayerModel(
        platform='battle', id='another_id', nickname='another_nickname'
    )
    match1 = random_match_model('player_1_match', Game.mw_mp, player1)
    match2 = random_match_model(
        'should_not_be_visible',
        Game.mw_mp,
        player2,
    )
    session.add(match1)
    session.add(match2)
    session.commit()

    assert (
        session.query(PlayerMatchModel)
        .filter(PlayerMatchModel.player == PlayerID(**player1.as_dict_flat()))
        .one()
        .id
        == 'player_1_match'
    )
