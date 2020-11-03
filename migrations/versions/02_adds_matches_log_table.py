"""Adds matches log table

Revision ID: 02
Revises: 01
Create Date: 2020-11-20 13:05:10.276400

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '02'
down_revision = '01'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('players_matches_stats', 'player_matches_stats')
    op.create_table(
        'player_matches_logs',
        sa.Column('match_id', sa.String(), nullable=False),
        sa.Column('source', sa.JSON(), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ['match_id'],
            ['player_matches_stats.id'],
        ),
        sa.PrimaryKeyConstraint('match_id'),
    )


def downgrade():
    op.rename_table('player_matches_stats', 'players_matches_stats')
    op.drop_table('player_matches_logs')
