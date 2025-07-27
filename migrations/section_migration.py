"""
Migration script to add section tables and related columns
"""

from app import db
from app.models import User, Section, SectionAssignment 
from datetime import datetime
from sqlalchemy import text

def upgrade():
    """
    Create sections and section_assignments tables, and add section_id to users table
    """
    # Create new tables
    db.create_all()
    
    # Alter the users table to add section_id column if it doesn't exist
    engine = db.engine
    inspector = db.inspect(engine)
    
    # Check if section_id exists in the users table
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'section_id' not in user_columns:
        # Add section_id column to users table
        if engine.dialect.name == 'sqlite':
            # For SQLite, we need to use raw SQL to add the column
            with engine.connect() as conn:
                # Execute the query directly
                conn.execute(text("ALTER TABLE users ADD COLUMN section_id INTEGER REFERENCES sections(id)"))
                # No need to call commit - in newer SQLAlchemy versions, autocommit is used 
                # or the connection will commit on context exit
        else:
            # For other databases like MySQL or PostgreSQL
            with engine.begin() as conn:
                # Begin() automatically manages the transaction
                conn.execute(text("ALTER TABLE users ADD COLUMN section_id INTEGER"))
                conn.execute(text("ALTER TABLE users ADD CONSTRAINT fk_section FOREIGN KEY (section_id) REFERENCES sections(id)"))
    


def downgrade():
    """
    Drop sections and section_assignments tables, and remove section_id from users table
    """
    # This is dangerous and should not be used in production without careful consideration
    engine = db.engine
    
    if engine.dialect.name == 'sqlite':
        # SQLite doesn't support dropping columns directly, we'd need to recreate the table
        # For safety, we'll just drop the tables in this example
        with engine.connect() as conn:
            conn.execute(text('DROP TABLE IF EXISTS section_assignments'))
            conn.execute(text('DROP TABLE IF EXISTS sections'))
            # No commit needed
    else:
        with engine.begin() as conn:
            # Begin() automatically manages the transaction
            conn.execute(text('DROP TABLE IF EXISTS section_assignments'))
            conn.execute(text('DROP TABLE IF EXISTS sections'))
            conn.execute(text('ALTER TABLE users DROP COLUMN IF EXISTS section_id'))
    


if __name__ == "__main__":
    upgrade() 
