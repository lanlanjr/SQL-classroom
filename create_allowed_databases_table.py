#!/usr/bin/env python3
"""
Manual migration script to create the allowed_databases table
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text


def create_allowed_databases_table():
    """Create the allowed_databases table manually."""
    app = create_app()
    
    with app.app_context():
        # Check if table already exists
        result = db.session.execute(text("SHOW TABLES LIKE 'allowed_databases'"))
        if result.fetchone():
            print("Table 'allowed_databases' already exists.")
            return True
        
        # Create the table
        create_table_sql = """
        CREATE TABLE allowed_databases (
            id INT PRIMARY KEY AUTO_INCREMENT,
            database_name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by INT NOT NULL,
            KEY ix_allowed_databases_database_name (database_name),
            KEY ix_allowed_databases_is_active (is_active),
            CONSTRAINT fk_allowed_databases_created_by 
                FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        try:
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("✓ Successfully created 'allowed_databases' table.")
            return True
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            db.session.rollback()
            return False


def main():
    """Run the migration."""
    print("Creating allowed_databases table...")
    
    if create_allowed_databases_table():
        print("Migration completed successfully!")
        return 0
    else:
        print("Migration failed!")
        return 1


if __name__ == '__main__':
    exit(main())
