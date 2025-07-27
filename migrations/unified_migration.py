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

        except Exception as e:


        # Add disable_copy_paste to questions table if it doesn't exist
        try:
            if not check_column_exists(conn, 'questions', 'disable_copy_paste'):
                conn.execute(sa.text('''
                    ALTER TABLE questions 
                    ADD COLUMN disable_copy_paste BOOLEAN NOT NULL DEFAULT 0
                '''))

        except Exception as e:


        # Add first_name and last_name to users table if they don't exist
        try:
            if not check_column_exists(conn, 'users', 'first_name'):
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

            
            if not check_column_exists(conn, 'users', 'last_name'):
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


        # Add invitation_token to sections table if it doesn't exist
        try:
            if not check_column_exists(conn, 'sections', 'invitation_token'):
                conn.execute(sa.text('''
                    ALTER TABLE sections 
                    ADD COLUMN invitation_token VARCHAR(64) UNIQUE
                '''))

        except Exception as e:




def downgrade():
    app = create_app()
    with app.app_context():
        conn = db.engine.connect()
        
        # Drop columns in MySQL
        try:
            conn.execute(sa.text("ALTER TABLE users DROP COLUMN first_name"))
        except Exception as e:

            
        try:
            conn.execute(sa.text("ALTER TABLE users DROP COLUMN last_name"))
        except Exception as e:

        
        try:
            conn.execute(sa.text("ALTER TABLE users DROP FOREIGN KEY users_ibfk_2")) # Drop the foreign key first
            conn.execute(sa.text("ALTER TABLE users DROP COLUMN section_id"))
        except Exception as e:

            
        try:
            conn.execute(sa.text("ALTER TABLE questions DROP COLUMN disable_copy_paste"))
        except Exception as e:

            
        try:
            conn.execute(sa.text("DROP TABLE IF EXISTS section_assignments"))
        except Exception as e:

            
        try:
            conn.execute(sa.text("DROP TABLE IF EXISTS sections"))
        except Exception as e:

            


def run_migration():
    upgrade()


if __name__ == '__main__':
    run_migration() 
