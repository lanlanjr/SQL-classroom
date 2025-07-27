"""Create AllowedDatabase table migration

Revision ID: allowed_database_table
Revises: (latest migration)
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = 'allowed_database_table'
down_revision = None  # This will be the latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Create the allowed_databases table."""
    op.create_table(
        'allowed_databases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('database_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.Index('ix_allowed_databases_database_name', 'database_name'),
        sa.Index('ix_allowed_databases_is_active', 'is_active'),
        sa.UniqueConstraint('database_name', name='unique_database_name')
    )


def downgrade():
    """Drop the allowed_databases table."""
    op.drop_table('allowed_databases')
