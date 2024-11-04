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
        sa.Column('current_users', sa.Integer, nullable=False, server_default='0')
    )
    
    # Create indexes on Arena
    op.create_index(
        op.f('idx_arena_optimized'),  # Name of the index
        'arena',                # Name of the table
        ['game_id', 'current_users', 'entry_fee', 'max_users', 'created_at'],  # Columns to index
        unique=False            # Whether the index should enforce uniqueness
    )


    # Create Participations table
    op.create_table(
        'participation',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_uuid', sa.UUID(), nullable=False),  # UUID for user from external DB
        sa.Column('arena_id', sa.UUID(), sa.ForeignKey('arena.id', ondelete='CASCADE'), nullable=False),  # Reference to Arena with cascade
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('challenge', sa.Integer, nullable=False),
        # sa.ForeignKeyConstraint(['arena_id'], ['arena.id'])
    )

    # Create indexes on Participations
    op.create_index(op.f('idx_participation_arena_id'), 'participation', ['arena_id', 'user_uuid', 'challenge'], unique=False)

    # Create Gamestream table
    op.create_table(
        'gamestream',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('addrapi', sa.String(), nullable=False),
        sa.Column('game_id', sa.String(), nullable=True),
        sa.Column('player_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('started', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('time_updated', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('id', 'addrapi', 'address', name='uq_gamestream')
    )

    # Create indexes on Gamestream
    op.create_index(op.f('idx_gamestream_status'), 'gamestream', ['status'], unique=False)


    # Create the function to update current_users
    op.execute("""
    CREATE OR REPLACE FUNCTION update_current_users() 
    RETURNS TRIGGER AS $$
    BEGIN
        IF (TG_OP = 'INSERT') THEN
            UPDATE arena 
            SET current_users = current_users + 1 
            WHERE id = NEW.arena_id;
            RETURN NEW;
        ELSIF (TG_OP = 'DELETE') THEN
            UPDATE arena 
            SET current_users = current_users - 1 
            WHERE id = OLD.arena_id;
            RETURN OLD;
        END IF;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Create the triggers
    op.execute("""
    CREATE OR REPLACE TRIGGER participation_insert
    AFTER INSERT ON participation
    FOR EACH ROW
    EXECUTE FUNCTION update_current_users();
    """)

    op.execute("""
    CREATE OR REPLACE TRIGGER participation_delete
    AFTER DELETE ON participation
    FOR EACH ROW
    EXECUTE FUNCTION update_current_users();
    """)



def downgrade():
    # Drop the triggers
    op.execute("DROP TRIGGER participation_insert ON participation;")
    op.execute("DROP TRIGGER participation_delete ON participation;")
    
    # Drop the function
    op.execute("DROP FUNCTION update_current_users();")

    # Drop indexes first
    op.drop_index('idx_participation_arena_id', table_name='participation')
    op.drop_index('idx_arena_optimized', table_name='arena')
    op.drop_index(op.f('idx_gamestream_status'), table_name='gamestream')
    
    # Drop the tables in reverse order
    op.drop_table('participation')
    op.drop_table('arena')
    op.drop_table('gamestream')
