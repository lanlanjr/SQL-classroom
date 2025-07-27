#!/usr/bin/env python3
"""
Check the current schema_imports table structure
"""
import pymysql
import os

try:
    conn = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'), 
        password=os.environ.get('MYSQL_PASSWORD', 'admin'),
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        database='sql_classroom'
    )
    
    with conn.cursor() as cursor:
        # Check if schema_imports table exists
        cursor.execute("SHOW TABLES LIKE 'schema_imports'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ schema_imports table exists")
            
            # Get table structure
            cursor.execute("DESCRIBE schema_imports")
            columns = cursor.fetchall()
            
            print("\nTable structure:")
            for col in columns:
                field, type_info, null, key, default, extra = col
                print(f"  {field}: {type_info}")
                
                # Check specifically for schema_content column
                if field == 'schema_content':
                    print(f"    >>> schema_content type: {type_info}")
                    if 'text' in type_info.lower():
                        if 'longtext' in type_info.lower():
                            print("    >>> This can hold ~4GB of data - should be sufficient")
                        elif 'mediumtext' in type_info.lower():
                            print("    >>> This can hold ~16MB of data")
                        elif 'text' == type_info.lower():
                            print("    >>> This can hold ~65KB of data - TOO SMALL for large schemas!")
                        else:
                            print(f"    >>> Unknown text type: {type_info}")
        else:
            print("❌ schema_imports table does not exist")
            
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
