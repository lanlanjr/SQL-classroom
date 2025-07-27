#!/usr/bin/env python3
"""
Test script to verify schema deletion works correctly
"""
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_schema_deletion():
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
        
        print("Connected to sql_classroom database")
        
        with connection.cursor() as cursor:
            # Check what prefixed tables exist
            cursor.execute("SHOW TABLES")
            all_tables = [row[0] for row in cursor.fetchall()]
            
            print(f"\nAll tables in sql_classroom database ({len(all_tables)} total):")
            for table in sorted(all_tables):
                print(f"  - {table}")
            
            # Look for any schema-prefixed tables
            schema_prefixes = []
            for table in all_tables:
                if table.startswith('schema_'):
                    parts = table.split('_')
                    if len(parts) >= 3:  # schema_userid_schemaid_tablename
                        prefix = '_'.join(parts[:3]) + '_'
                        if prefix not in schema_prefixes:
                            schema_prefixes.append(prefix)
            
            if schema_prefixes:
                print(f"\nFound {len(schema_prefixes)} schema prefixes:")
                for prefix in schema_prefixes:
                    prefix_tables = [t for t in all_tables if t.startswith(prefix)]
                    print(f"  Prefix '{prefix}': {len(prefix_tables)} tables")
                    for table in prefix_tables:
                        print(f"    - {table}")
            else:
                print("\nNo schema-prefixed tables found.")
        
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_schema_deletion()
