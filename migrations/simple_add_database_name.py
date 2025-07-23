"""
Simple migration to add database_name column to sections table
This script uses direct SQL to avoid Flask app dependencies.
"""

import sqlite3
import os

def run_migration():
    """Add database_name column to sections table if it doesn't exist"""
    
    # Find the database file - usually in the instance folder or main directory
    possible_db_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'instance', 'app.db'),
        os.path.join(os.path.dirname(__file__), '..', 'app.db'),
        os.path.join(os.path.dirname(__file__), '..', 'instance', 'sql_classroom.db'),
        os.path.join(os.path.dirname(__file__), '..', 'sql_classroom.db'),
    ]
    
    db_path = None
    for path in possible_db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Found database at: {path}")
            break
    
    if not db_path:
        print("Could not find database file. Please run the migration manually.")
        print("The SQL to add the column is:")
        print("ALTER TABLE sections ADD COLUMN database_name VARCHAR(100) NULL;")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(sections)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'database_name' not in columns:
            print("Adding database_name column to sections table...")
            cursor.execute("ALTER TABLE sections ADD COLUMN database_name VARCHAR(100)")
            conn.commit()
            print("Successfully added database_name column to sections table")
        else:
            print("database_name column already exists in sections table")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error running migration: {e}")
        return False

if __name__ == '__main__':
    run_migration()
