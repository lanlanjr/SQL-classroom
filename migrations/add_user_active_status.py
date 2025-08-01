"""
Add is_active field to users table for enabling/disabling user accounts
"""
from flask import Flask
from app import create_app, db
import sqlalchemy as sa

def upgrade():
    """Add is_active column to users table"""
    app = create_app()
    with app.app_context():
        # Get the SQLAlchemy connection
        conn = db.engine.connect()
        
        try:
            # Check if column exists
            result = conn.execute(sa.text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'is_active' not in columns:
                conn.execute(sa.text('''
                    ALTER TABLE users 
                    ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL
                '''))

                
                # Update existing users to be active by default
                conn.execute(sa.text('''
                    UPDATE users 
                    SET is_active = 1 
                    WHERE is_active IS NULL
                '''))

            else:

                
            # Commit the transaction
            conn.commit()

            
        except Exception as e:

            conn.rollback()
            raise
        finally:
            conn.close()

def downgrade():
    """Remove is_active column from users table"""
    app = create_app()
    with app.app_context():
        # SQLite doesn't support DROP COLUMN directly, so this would require
        # recreating the table, which is complex. For now, just log that
        # downgrade is not supported.


if __name__ == "__main__":
    upgrade()
