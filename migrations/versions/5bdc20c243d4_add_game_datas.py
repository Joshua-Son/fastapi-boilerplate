"""add gamestream arena

Revision ID: 5bdc20c243d4
Revises: eaae517c1e2f
Create Date: 2023-06-01 14:31:22.211647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5bdc20c243d4'
down_revision = 'eaae517c1e2f'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('gamedatas',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('game_name', sa.String(), nullable=False),
        sa.Column('window_name', sa.String(), nullable=False),
        sa.Column('game_id', sa.String(), nullable=False, unique=True),
        sa.Column('game_path', sa.String(), nullable=False, unique=True),
    )

    op.create_index(op.f('idx_gamedatas_gameid'), 'gamedatas', ['game_id'], unique=True)
    # ### end Alembic commands ###

def downgrade():
    op.drop_index(op.f('idx_gamedatas_gameid'), table_name='gamedatas')
    op.drop_table('gamedatas')
