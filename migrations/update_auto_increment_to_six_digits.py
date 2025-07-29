"""
Migration script to update all table AUTO_INCREMENT values to start from 100000 for 6-digit IDs
"""

import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Update AUTO_INCREMENT values to start from 100000 for all tables"""
    
    try:
        # Connect directly to MySQL
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', ''),
            user=os.getenv('MYSQL_USER', ''),
            password=os.getenv('MYSQL_PASSWORD', ''),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            database=os.getenv('APP_DB_NAME', ''),
            connect_timeout=30
        )
        
        with connection.cursor() as cursor:
            # List of all tables that need AUTO_INCREMENT update
            tables_to_update = [
                'users',
                'questions', 
                'assignments',
                'submissions',
                'sections',
                'section_assignments',
                'assignment_questions',
                'student_enrollments',
                'allowed_databases',
                'schema_imports'
            ]
            
            print("Starting AUTO_INCREMENT migration to 6-digit IDs...")
            
            for table_name in tables_to_update:
                try:
                    # Check if table exists
                    cursor.execute("SHOW TABLES LIKE %s", (table_name,))
                    if cursor.fetchone():
                        # Get current max ID
                        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
                        result = cursor.fetchone()
                        max_id = result[0] if result[0] else 0
                        
                        # Get current AUTO_INCREMENT value
                        cursor.execute(f"SHOW TABLE STATUS LIKE '{table_name}'")
                        table_status = cursor.fetchone()
                        current_auto_increment = table_status[10] if table_status else 0
                        
                        # Set AUTO_INCREMENT to ensure 6-digit IDs
                        if max_id >= 100000:
                            # If existing records are already 6-digit, continue from next available
                            new_auto_increment = max_id + 1
                        else:
                            # Start from 100000 for 6-digit IDs
                            new_auto_increment = 100000
                        
                        # Update AUTO_INCREMENT
                        cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = {new_auto_increment}")
                        print(f"✓ Updated {table_name} AUTO_INCREMENT from {current_auto_increment} to {new_auto_increment} (max existing ID: {max_id})")
                    else:
                        print(f"⚠ Table {table_name} does not exist, skipping...")
                        
                except Exception as e:
                    print(f"✗ Error updating {table_name}: {str(e)}")
                    continue
            
            connection.commit()
            
        connection.close()
        print("\n✓ AUTO_INCREMENT migration completed successfully!")
        print("All new records will now have 6-digit IDs starting from 100000")
        
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = run_migration()
    if success:
        print("\nMigration completed successfully!")
    else:
        print("\nMigration failed!")
        import sys
        sys.exit(1)
