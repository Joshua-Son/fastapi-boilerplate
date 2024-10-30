"""initialise

Revision ID: eaae517c1e2f
Revises: 
Create Date: 2020-10-01 12:32:07.701738

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eaae517c1e2f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create Arena table
    op.create_table(
        'arena',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('game_id', sa.UUID(), nullable=False),  # UUID for game_id
        sa.Column('max_users', sa.Integer, nullable=True),  # Nullable max_users for tournaments
        sa.Column('entry_fee', sa.Integer, nullable=True),  # Nullable entry_fee for tournaments
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('current_users', sa.Integer, nullable=False, default=0)
    )
    
    # Create indexes on Arena
    op.create_index(
        op.f('idx_arena_optimized'),  # Name of the index
        'arena',                # Name of the table
        ['game_id', 'entry_fee', 'max_users', 'created_at'],  # Columns to index
        unique=False            # Whether the index should enforce uniqueness
    )


    # Create Participations table
    op.create_table(
        'participation',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_uuid', sa.UUID(), nullable=False),  # UUID for user from external DB
        sa.Column('arena_id', sa.Integer, nullable=False),  # Reference to Arena, no FK constraint
        sa.Column('score', sa.Integer, nullable=True),
        sa.Column('status', sa.Enum('playing', 'finished', name='participationstatus'), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True)
    )

    # Create indexes on Participations
    op.create_index(op.f('idx_participation_arena_id'), 'participation', ['arena_id'], unique=False)  # Index on arena_id
    op.create_index(op.f('idx_participation_status'), 'participation', ['status'], unique=False)


def downgrade():
    # Drop indexes first
    op.drop_index('idx_participation_status', table_name='participation')
    op.drop_index('idx_participation_arena_id', table_name='participation')
    op.drop_index('idx_arena_optimized', table_name='arena')
    
    # Drop the tables in reverse order
    op.drop_table('participation')
    op.drop_table('arena')
