from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add is_active column to section_assignments table with default value True
    op.add_column('section_assignments', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))

def downgrade():
    # Remove is_active column from section_assignments
    op.drop_column('section_assignments', 'is_active') 
