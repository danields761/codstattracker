from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SEnum
from sqlalchemy import Float, ForeignKey, Integer, Interval, String, and_
from sqlalchemy.orm import RelationshipProperty, relationship
from sqlalchemy.schema import UniqueConstraint

from codstattracker.api.models import (
    BattleRoyaleStats,
    Game,
    MatchStats,
    PlayerID,
    PlayerMatch,
    WeaponStats,
)
from codstattracker.base_model import Model
from codstattracker.storage.sql.ext import Base


def _select_model_fields(model: Model, **fields: Any) -> dict[str, Any]:
    model_fields = {field.name for field in model.all_fields()}
    return {
        name: value for name, value in fields.items() if name in model_fields
    }


class PlayerModel(PlayerID, Base):
    db_id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)
    id = Column(String, nullable=False)
    nickname = Column(String, nullable=False)

    __tablename__ = 'players'
    __tableargs__ = (UniqueConstraint(platform, id, nickname),)

    def __init__(self, *args, db_id: Optional[int] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_id = db_id


class WeaponStatsModel(WeaponStats, Base):
    id = Column(Integer, primary_key=True)
    match_id = Column(String, ForeignKey('players_matches_stats.id'))

    name = Column(String, nullable=False)
    hits = Column(Integer, nullable=False)
    kills = Column(Integer, nullable=False)
    deaths = Column(Integer, nullable=False)
    shots = Column(Integer, nullable=False)
    headshots = Column(Integer, nullable=False)

    __tablename__ = 'weapon_stats'

    def __init__(
        self,
        *args,
        id: Optional[int] = None,
        match_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.id = id
        self.match_id = match_id


class BrStatsModel(BattleRoyaleStats, Base):
    id = Column(Integer, primary_key=True)
    match_id = Column(String, ForeignKey('players_matches_stats.id'))

    teams_count = Column(Integer, nullable=False)
    players_count = Column(Integer, nullable=False)
    placement = Column(Integer, nullable=False)

    __tablename__ = 'br_stats'
    __tableargs__ = (UniqueConstraint(match_id),)


class PlayerMatchModel(PlayerMatch, MatchStats, Base):
    class PlayerComparator(RelationshipProperty.Comparator):
        def __eq__(self, other):
            if not isinstance(other, PlayerID) or isinstance(
                other, PlayerModel
            ):
                return super().__eq__(other)

            return and_(
                self.__clause_element__(),
                PlayerModel.platform == other.platform,
                PlayerModel.nickname == other.nickname,
                PlayerModel.id == other.id,
            )

    player_id = Column(Integer, ForeignKey(PlayerModel.db_id))
    player = relationship(
        PlayerModel,
        comparator_factory=PlayerComparator,
        uselist=False,
        lazy='joined',
        innerjoin=True,
    )

    id = Column(String, primary_key=True)
    game = Column(SEnum(Game))
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    map = Column(String, nullable=False)
    is_win = Column(Boolean, nullable=False)
    br_stats = relationship(
        BrStatsModel,
        innerjoin=False,
        lazy='joined',
        uselist=False,
    )
    weapon_stats = relationship(WeaponStatsModel, lazy='joined')

    kills = Column(Integer, nullable=False)
    assists = Column(Integer, nullable=False)
    deaths = Column(Integer, nullable=False)
    kd_ratio = Column(Float, nullable=False)
    killstreaks_used = Column(JSON, nullable=False)
    longest_streak = Column(Integer, nullable=False)
    suicides = Column(Integer, nullable=False)
    executions = Column(Integer, nullable=False)
    damage_dealt = Column(Integer, nullable=False)
    damage_received = Column(Integer, nullable=False)
    percent_time_moved = Column(Float, nullable=False)
    shots_fired = Column(Integer, nullable=False)
    shots_missed = Column(Integer, nullable=False)
    headshots = Column(Integer, nullable=False)
    wall_bangs = Column(Integer, nullable=False)
    time_played = Column(Interval, nullable=False)
    distance_traveled = Column(Float, nullable=False)
    average_speed = Column(Float, nullable=False)

    __tablename__ = 'players_matches_stats'

    def __init__(
        self,
        game: Game,
        player: Optional[PlayerModel] = None,
        player_id: Optional[int] = None,
        br_stats: Optional[BattleRoyaleStats] = None,
        **kwargs,
    ):
        if br_stats:
            assert game is not Game.mw_mp
            save_br_stats = BrStatsModel(**br_stats.as_dict_flat())
        else:
            save_br_stats = None

        PlayerMatch.__init__(
            self,
            game=game,
            stats=self,
            br_stats=save_br_stats,
            **_select_model_fields(PlayerMatch, **kwargs),
        )
        MatchStats.__init__(self, **_select_model_fields(MatchStats, **kwargs))
        self.player = player
        self.player_id = player_id
        self.game = game
