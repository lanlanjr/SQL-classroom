from flask import Flask
from app import create_app, db
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from datetime import datetime
from sqlalchemy.sql import func

def check_column_exists(conn, table, column):
    """Helper function to check if a column exists in MySQL"""
    result = conn.execute(sa.text(f"SHOW COLUMNS FROM {table} LIKE '{column}'"))
    return result.rowcount > 0

def upgrade():
    app = create_app()
    with app.app_context():
        # Get the SQLAlchemy connection
        conn = db.engine.connect()

        # Create sections table if it doesn't exist
        conn.execute(sa.text('''
            CREATE TABLE IF NOT EXISTS sections (
                id INT AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                creator_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                invitation_token VARCHAR(64) UNIQUE,
                FOREIGN KEY (creator_id) REFERENCES users (id),
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''))

        # Create section_assignments table if it doesn't exist
        conn.execute(sa.text('''
            CREATE TABLE IF NOT EXISTS section_assignments (
                id INT AUTO_INCREMENT,
                section_id INT NOT NULL,
                assignment_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (section_id) REFERENCES sections (id),
                FOREIGN KEY (assignment_id) REFERENCES assignments (id),
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''))

        # Add section_id to users table if it doesn't exist
        try:
            if not check_column_exists(conn, 'users', 'section_id'):
                conn.execute(sa.text('''
                    ALTER TABLE users 
                    ADD COLUMN section_id INTEGER,
                    ADD FOREIGN KEY (section_id) REFERENCES sections(id)
                '''))
                print("Added section_id column to users table")
        except Exception as e:
            print(f"Error adding section_id to users: {e}")

        # Add disable_copy_paste to questions table if it doesn't exist
        try:
            if not check_column_exists(conn, 'questions', 'disable_copy_paste'):
                conn.execute(sa.text('''
                    ALTER TABLE questions 
                    ADD COLUMN disable_copy_paste BOOLEAN NOT NULL DEFAULT 0
                '''))
                print("Added disable_copy_paste column to questions table")
        except Exception as e:
            print(f"Error adding disable_copy_paste to questions: {e}")

        # Add first_name and last_name to users table if they don't exist
        try:
            if not check_column_exists(conn, 'users', 'first_name'):
                conn.execute(sa.text('''
                    ALTER TABLE users 
                    ADD COLUMN first_name VARCHAR(50) DEFAULT 'User'
                '''))
                print("Added first_name column to users table")
                
                # Update existing users to have a first name
                conn.execute(sa.text('''
                    UPDATE users 
                    SET first_name = username 
                    WHERE first_name IS NULL OR first_name = 'User'
                '''))
                print("Updated existing users with default first_name values")
            
            if not check_column_exists(conn, 'users', 'last_name'):
                conn.execute(sa.text('''
                    ALTER TABLE users 
                    ADD COLUMN last_name VARCHAR(50) DEFAULT 'Account'
                '''))
                print("Added last_name column to users table")
                
                # Update existing users to have a last name
                conn.execute(sa.text('''
                    UPDATE users 
                    SET last_name = 'Account' 
                    WHERE last_name IS NULL
                '''))
                print("Updated existing users with default last_name values")
                
        except Exception as e:
            print(f"Error adding name fields to users: {e}")

        # Add invitation_token to sections table if it doesn't exist
        try:
            if not check_column_exists(conn, 'sections', 'invitation_token'):
                conn.execute(sa.text('''
                    ALTER TABLE sections 
                    ADD COLUMN invitation_token VARCHAR(64) UNIQUE
                '''))
                print("Added invitation_token column to sections table")
        except Exception as e:
            print(f"Error adding invitation_token to sections: {e}")

        print("All migrations completed successfully")

def downgrade():
    app = create_app()
    with app.app_context():
        conn = db.engine.connect()
        
        # Drop columns in MySQL
        try:
            conn.execute(sa.text("ALTER TABLE users DROP COLUMN first_name"))
        except Exception as e:
            print(f"Could not drop first_name from users: {e}")
            
        try:
            conn.execute(sa.text("ALTER TABLE users DROP COLUMN last_name"))
        except Exception as e:
            print(f"Could not drop last_name from users: {e}")
        
        try:
            conn.execute(sa.text("ALTER TABLE users DROP FOREIGN KEY users_ibfk_2")) # Drop the foreign key first
            conn.execute(sa.text("ALTER TABLE users DROP COLUMN section_id"))
        except Exception as e:
            print(f"Could not drop section_id from users: {e}")
            
        try:
            conn.execute(sa.text("ALTER TABLE questions DROP COLUMN disable_copy_paste"))
        except Exception as e:
            print(f"Could not drop disable_copy_paste from questions: {e}")
            
        try:
            conn.execute(sa.text("DROP TABLE IF EXISTS section_assignments"))
        except Exception as e:
            print(f"Could not drop section_assignments table: {e}")
            
        try:
            conn.execute(sa.text("DROP TABLE IF EXISTS sections"))
        except Exception as e:
            print(f"Could not drop sections table: {e}")
            
        print("Downgrade completed with possible warnings")

def run_migration():
    upgrade()
    print("Unified migration completed successfully")

if __name__ == '__main__':
    run_migration() 