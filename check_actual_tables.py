#!/usr/bin/env python3
"""
Quick script to check what tables actually exist in sql_classroom database
"""
import pymysql
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

try:
    # Connect to sql_classroom database
    connection = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', 'admin'),
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        database='sql_classroom',
        connect_timeout=30
    )
    
    print("Connected to sql_classroom database successfully!")
    
    with connection.cursor() as cursor:
        # Show all tables
        cursor.execute("SHOW TABLES")
        all_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\nTotal tables in sql_classroom database: {len(all_tables)}")
        print("\nAll tables:")
        for table in sorted(all_tables):
            print(f"  - {table}")
        
        # Look for tables with schema prefixes
        schema_prefixes = ['schema_1_5_', 'teacher_2_schema_1_']
        
        for prefix in schema_prefixes:
            matching_tables = [t for t in all_tables if t.startswith(prefix)]
            print(f"\nTables with prefix '{prefix}': {len(matching_tables)}")
            for table in matching_tables:
                print(f"  - {table}")
                
                # Get table structure
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"    Columns: {[col[0] for col in columns]}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                print(f"    Row count: {row_count}")
    
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
