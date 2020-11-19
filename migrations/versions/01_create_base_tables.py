"""Create base tables

Revision ID: 01
Revises:
Create Date: 2020-11-18 15:07:52.717890

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '01'
down_revision = '00'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'players',
        sa.Column('db_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('nickname', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('db_id'),
        sa.UniqueConstraint('platform', 'id', 'nickname'),
    )
    op.create_table(
        'players_matches_stats',
        sa.Column('player_id', sa.Integer(), nullable=True),
        sa.Column('id', sa.String(), nullable=False),
        sa.Column(
            'game',
            sa.Enum('mw_mp', 'mw_wz', name='game', native_enum=False),
            nullable=True,
        ),
        sa.Column('start', sa.DateTime(), nullable=False),
        sa.Column('end', sa.DateTime(), nullable=False),
        sa.Column('map', sa.String(), nullable=False),
        sa.Column('is_win', sa.Boolean(), nullable=False),
        sa.Column('kills', sa.Integer(), nullable=False),
        sa.Column('assists', sa.Integer(), nullable=False),
        sa.Column('deaths', sa.Integer(), nullable=False),
        sa.Column('kd_ratio', sa.Float(), nullable=False),
        sa.Column('killstreaks_used', sa.JSON(), nullable=False),
        sa.Column('longest_streak', sa.Integer(), nullable=False),
        sa.Column('suicides', sa.Integer(), nullable=False),
        sa.Column('executions', sa.Integer(), nullable=False),
        sa.Column('damage_dealt', sa.Integer(), nullable=False),
        sa.Column('damage_received', sa.Integer(), nullable=False),
        sa.Column('percent_time_moved', sa.Float(), nullable=False),
        sa.Column('shots_fired', sa.Integer(), nullable=False),
        sa.Column('shots_missed', sa.Integer(), nullable=False),
        sa.Column('headshots', sa.Integer(), nullable=False),
        sa.Column('wall_bangs', sa.Integer(), nullable=False),
        sa.Column('time_played', sa.Interval(), nullable=False),
        sa.Column('distance_traveled', sa.Float(), nullable=False),
        sa.Column('average_speed', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ['player_id'],
            ['players.db_id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'br_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.String(), nullable=True),
        sa.Column('teams_count', sa.Integer(), nullable=False),
        sa.Column('players_count', sa.Integer(), nullable=False),
        sa.Column('placement', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['match_id'],
            ['players_matches_stats.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id'),
    )
    op.create_table(
        'weapon_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('hits', sa.Integer(), nullable=False),
        sa.Column('kills', sa.Integer(), nullable=False),
        sa.Column('deaths', sa.Integer(), nullable=False),
        sa.Column('shots', sa.Integer(), nullable=False),
        sa.Column('headshots', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['match_id'],
            ['players_matches_stats.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('weapon_stats')
    op.drop_table('br_stats')
    op.drop_table('players_matches_stats')
    op.drop_table('players')
