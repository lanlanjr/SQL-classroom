#!/usr/bin/env python3
"""
Test the SQL filtering functionality
"""
import sys
sys.path.append('.')
from app.utils import parse_schema_statements

def test_sql_filtering():
    # Read the test SQL file
    with open('test_filtering.sql', 'r') as f:
        content = f.read()
    
    print("Original SQL content:")
    print("=" * 50)
    print(content)
    print("=" * 50)
    
    # Parse using our function
    statements = parse_schema_statements(content)
    
    print(f"\nParsed {len(statements)} statements after filtering:")
    
    create_database_count = 0
    use_count = 0
    create_table_count = 0
    insert_count = 0
    
    for i, stmt in enumerate(statements, 1):
        stmt_upper = stmt.upper().strip()
        stmt_type = "OTHER"
        
        if stmt_upper.startswith('CREATE DATABASE') or stmt_upper.startswith('CREATE SCHEMA'):
            create_database_count += 1
            stmt_type = "CREATE DATABASE/SCHEMA"
        elif stmt_upper.startswith('USE '):
            use_count += 1
            stmt_type = "USE"
        elif stmt_upper.startswith('CREATE TABLE'):
            create_table_count += 1
            stmt_type = "CREATE TABLE"
        elif stmt_upper.startswith('INSERT'):
            insert_count += 1
            stmt_type = "INSERT"
        
        print(f"{i}. [{stmt_type}] {stmt[:80]}...")
    
    print(f"\nSummary:")
    print(f"  CREATE DATABASE/SCHEMA: {create_database_count} (should be 0)")
    print(f"  USE statements: {use_count} (should be 0)")
    print(f"  CREATE TABLE: {create_table_count} (should be 2)")
    print(f"  INSERT: {insert_count} (should be 1)")
    
    if create_database_count == 0 and use_count == 0:
        print("\n✅ SUCCESS: CREATE DATABASE and USE statements properly filtered!")
    else:
        print(f"\n❌ FAILURE: Found {create_database_count} CREATE DATABASE and {use_count} USE statements")

if __name__ == "__main__":
    test_sql_filtering()
