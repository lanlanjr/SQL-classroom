#!/usr/bin/env python3
"""
Migration to upgrade schema_content column to LONGTEXT
"""

def upgrade_schema_content_column():
    """
    Upgrade the schema_content column from TEXT to LONGTEXT
    to support larger SQL schema files.
    """
    import pymysql
    import os
    
    try:
        print("🔧 Upgrading schema_content column to LONGTEXT...")
        
        conn = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'), 
            password=os.environ.get('MYSQL_PASSWORD', 'admin'),
            port=int(os.environ.get('MYSQL_PORT', 3306)),
            database='sql_classroom'
        )
        
        with conn.cursor() as cursor:
            # Check current column type
            cursor.execute("DESCRIBE schema_imports")
            columns = cursor.fetchall()
            
            schema_content_type = None
            for col in columns:
                if col[0] == 'schema_content':
                    schema_content_type = col[1]
                    break
            
            if schema_content_type:
                print(f"Current schema_content type: {schema_content_type}")
                
                if 'longtext' in schema_content_type.lower():
                    print("✅ Column is already LONGTEXT - no upgrade needed!")
                else:
                    print("🔄 Upgrading column to LONGTEXT...")
                    
                    # Alter the column to LONGTEXT
                    alter_sql = "ALTER TABLE schema_imports MODIFY COLUMN schema_content LONGTEXT NOT NULL"
                    cursor.execute(alter_sql)
                    conn.commit()
                    
                    print("✅ Successfully upgraded schema_content to LONGTEXT!")
                    print("📈 New capacity: Up to 4GB of schema content")
            else:
                print("❌ schema_content column not found!")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        return False
    
    return True

if __name__ == "__main__":
    upgrade_schema_content_column()
