"""
Simple migration to add database_name column to sections table
This script uses direct SQL to avoid Flask app dependencies.
"""

import sqlite3
import os
import logging

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

            break
    
    if not db_path:


        logging.debug("ALTER TABLE sections ADD COLUMN database_name VARCHAR(100) NULL;")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(sections)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'database_name' not in columns:

            cursor.execute("ALTER TABLE sections ADD COLUMN database_name VARCHAR(100)")
            conn.commit()

        else:
            pass
        
        conn.close()
        return True
        
    except Exception as e:

        return False

if __name__ == '__main__':
    run_migration()
