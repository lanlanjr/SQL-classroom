#!/usr/bin/env python3
"""
Simple migration script to add is_active field to users table
"""
import sqlite3
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def migrate_database():
    """Add is_active column to users table"""
    # Find the database file
    db_path = os.path.join(project_root, 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Looking for alternative database locations...")
        
        # Try other common locations
        alt_paths = [
            os.path.join(project_root, 'app.db'),
            os.path.join(project_root, 'database.db'),
            os.path.join(project_root, 'sql_classroom.db')
        ]
        
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                db_path = alt_path
                print(f"Found database at {alt_path}")
                break
        else:
            print("No database found. Please run the application first to create the database.")
            return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the is_active column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_active' in columns:
            print("Column 'is_active' already exists in users table")
            return True
        
        # Add the is_active column
        cursor.execute('''
            ALTER TABLE users 
            ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL
        ''')
        
        # Update all existing users to be active
        cursor.execute('''
            UPDATE users 
            SET is_active = 1 
            WHERE is_active IS NULL
        ''')
        
        conn.commit()
        print("Successfully added is_active column to users table")
        print("All existing users have been set to active status")
        
        return True
        
    except Exception as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Running migration to add is_active field to users table...")
    success = migrate_database()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)
