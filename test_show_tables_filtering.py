#!/usr/bin/env python3
"""
Test the SHOW TABLES filtering functionality for imported schemas
"""
import sys
sys.path.append('.')

def test_show_tables_detection():
    print("=== Testing SHOW TABLES Query Detection ===\n")
    
    from app.utils import is_show_tables_query
    
    test_queries = [
        ("SHOW TABLES;", True),
        ("show tables", True),
        ("SHOW TABLES FROM database", True),
        ("SELECT * FROM users", False),
        ("DESCRIBE table_name", False),
        ("SHOW DATABASES", False),
        ("   SHOW TABLES   ", True),
    ]
    
    for query, expected in test_queries:
        result = is_show_tables_query(query)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status}: '{query}' -> {result} (expected {expected})")
    
    print("\n" + "="*60 + "\n")

def test_show_tables_processing():
    print("=== Testing SHOW TABLES Result Processing ===\n")
    
    # Mock data that would come from SHOW TABLES on sql_classroom database
    original_columns = ["Tables_in_sql_classroom"]
    original_data = [
        ["assignment_questions"],
        ["assignments"],
        ["questions"],
        ["schema_1_13_courses"],      # These should be filtered
        ["schema_1_13_students"],     # and cleaned
        ["schema_1_14_courses"],      # Different schema - should be ignored
        ["schema_1_14_students"],     # if user_id doesn't match
        ["schema_imports"],
        ["sections"],
        ["users"]
    ]
    
    print("Original SHOW TABLES result:")
    print("Columns:", original_columns)
    print("Data:")
    for row in original_data:
        print(f"  {row[0]}")
    
    print("\n" + "-"*40 + "\n")
    
    # Test 1: Regular database (not sql_classroom) - should pass through unchanged
    print("Test 1: Regular database (should pass through unchanged)")
    
    # Create Flask application context for database operations
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.utils import process_show_tables_result_for_schema
        
        processed_columns, processed_data = process_show_tables_result_for_schema(
            original_columns, original_data, "some_other_db", 1
        )
        
        print("Result:")
        print("Columns:", processed_columns)
        print("Data:")
        for row in processed_data:
            print(f"  {row[0]}")
        
        if processed_columns == original_columns and processed_data == original_data:
            print("✅ PASS: Non-sql_classroom database passed through unchanged")
        else:
            print("❌ FAIL: Non-sql_classroom database was modified")
        
        print("\n" + "-"*40 + "\n")
        
        # Test 2: sql_classroom database but no matching schemas
        print("Test 2: sql_classroom database but no active schemas")
        processed_columns, processed_data = process_show_tables_result_for_schema(
            original_columns, original_data, "sql_classroom", 999  # Non-existent user
        )
        
        if processed_columns == original_columns and processed_data == original_data:
            print("✅ PASS: No schema match - passed through unchanged")
        else:
            print("❌ FAIL: No schema match but was modified anyway")
    
    print("\n" + "-"*40 + "\n")
    
    print("🎯 SUMMARY:")
    print("The filtering functionality is ready to be tested with actual database.")
    print("When there are active schemas, it will:")
    print("1. Find tables matching the schema prefix (e.g., 'schema_1_13_')")
    print("2. Remove the prefix from table names (courses, students)")  
    print("3. Change column header to 'Tables_in_<schema_name>'")
    print("4. Return only the cleaned schema tables")

if __name__ == "__main__":
    test_show_tables_detection()
    test_show_tables_processing()
