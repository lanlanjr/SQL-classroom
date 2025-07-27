#!/usr/bin/env python3
"""
Check current database state
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
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        print('Current tables in sql_classroom:')
        for table in tables:
            print(f'  {table[0]}')
            
        # Check for schema tables
        schema_tables = [t[0] for t in tables if 'schema_' in t[0]]
        if schema_tables:
            print(f'\nFound {len(schema_tables)} schema tables:')
            for t in schema_tables:
                print(f'  {t}')
        else:
            print('\nNo schema tables found.')
            
    conn.close()
    print('\n✅ Database check complete')
    
except Exception as e:
    print(f'❌ Error: {e}')
