"""Upgrade schema_content column to LONGTEXT

Revision ID: upgrade_schema_content
Revises: f4ee6b384f91
Create Date: 2025-07-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'upgrade_schema_content'
down_revision = 'f4ee6b384f91'
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade the schema_content column from TEXT to LONGTEXT
    to support larger SQL schema files (up to 4GB).
    """
    # Check if schema_imports table exists, create if it doesn't
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'schema_imports' not in inspector.get_table_names():
        # Create the schema_imports table if it doesn't exist
        op.create_table('schema_imports',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('schema_content', mysql.LONGTEXT(), nullable=False),  # Use LONGTEXT from the start
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('is_template', sa.Boolean(), nullable=True),
            sa.Column('active_schema_name', sa.String(length=100), nullable=True),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    else:
        # Table exists, just modify the column
        op.alter_column('schema_imports', 'schema_content',
                       existing_type=sa.TEXT(),
                       type_=mysql.LONGTEXT(),
                       nullable=False)


def downgrade():
    """
    Downgrade the schema_content column back to TEXT.
    Warning: This may cause data loss if there are large schemas stored.
    """
    # Only modify the column if table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'schema_imports' in inspector.get_table_names():
        op.alter_column('schema_imports', 'schema_content',
                       existing_type=mysql.LONGTEXT(),
                       type_=sa.TEXT(),
                       nullable=False)
