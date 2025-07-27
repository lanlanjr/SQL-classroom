"""
Add first_name and last_name fields to users
"""
from flask import Flask
from app import create_app, db
import sqlalchemy as sa

def upgrade():
    """Add first_name and last_name columns to users table"""
    app = create_app()
    with app.app_context():
        # Get the SQLAlchemy connection
        conn = db.engine.connect()
        
        # Add first_name and last_name to users table
        try:
            # Check if columns exist
            result = conn.execute(sa.text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'first_name' not in columns:
                conn.execute(sa.text('''
                    ALTER TABLE users 
                    ADD COLUMN first_name VARCHAR(50) DEFAULT 'User'
                '''))

                
                # Update existing users to have a first name
                conn.execute(sa.text('''
                    UPDATE users 
                    SET first_name = username 
                    WHERE first_name IS NULL OR first_name = 'User'
                '''))

            
            if 'last_name' not in columns:
                conn.execute(sa.text('''
                    ALTER TABLE users 
                    ADD COLUMN last_name VARCHAR(50) DEFAULT 'Account'
                '''))

                
                # Update existing users to have a last name
                conn.execute(sa.text('''
                    UPDATE users 
                    SET last_name = 'Account' 
                    WHERE last_name IS NULL
                '''))

                

        except Exception as e:


def downgrade():
    """Remove first_name and last_name columns from users table"""
    app = create_app()
    with app.app_context():
        conn = db.engine.connect()
        
        # These operations may fail if SQLite doesn't support dropping columns
        try:
            conn.execute(sa.text("ALTER TABLE users DROP COLUMN first_name"))

        except Exception as e:

            
        try:
            conn.execute(sa.text("ALTER TABLE users DROP COLUMN last_name"))

        except Exception as e:

            


if __name__ == '__main__':
    upgrade() 
