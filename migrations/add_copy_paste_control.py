from flask import Flask
from app import create_app, db
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Boolean, text

def column_exists(conn, table_name, column_name):
    """Check if a column exists in a table"""
    # For SQLite, we can check the table info
    result = conn.execute(text(f"PRAGMA table_info({table_name})"))
    columns = [row[1] for row in result.fetchall()]
    return column_name in columns

def upgrade():
    # Create a Flask app context
    app = create_app()
    with app.app_context():
        # Check if column already exists
        with db.engine.connect() as conn:
            if not column_exists(conn, 'questions', 'disable_copy_paste'):
                # Execute raw SQL to add the column using newer SQLAlchemy method
                conn.execute(text('ALTER TABLE questions ADD COLUMN disable_copy_paste BOOLEAN NOT NULL DEFAULT 0'))

            else:

    
def downgrade():
    # Create a Flask app context
    app = create_app()
    with app.app_context():
        # Check if column exists before dropping
        with db.engine.connect() as conn:
            if column_exists(conn, 'questions', 'disable_copy_paste'):
                # Execute raw SQL to remove the column using newer SQLAlchemy method
                conn.execute(text('ALTER TABLE questions DROP COLUMN disable_copy_paste'))

            else:


def run_migration():
    upgrade()


if __name__ == '__main__':
    run_migration() 
