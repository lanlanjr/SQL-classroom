#!/usr/bin/env python3
"""
Simple test to verify SHOW TABLES functionality works
"""
import sys
sys.path.append('.')

def main():
    # Test the basic functionality first
    from app.utils import is_show_tables_query, process_show_tables_result_for_schema
    
    print("Testing SHOW TABLES detection...")
    assert is_show_tables_query("SHOW TABLES") == True
    assert is_show_tables_query("SELECT * FROM users") == False
    print("✅ Detection works!")
    
    print("\nTesting result processing...")
    
    # Mock data simulating what we'd get from the database
    columns = ["Tables_in_sql_classroom"]
    data = [
        ["users"],
        ["assignments"], 
        ["schema_1_7_authors"],
        ["schema_1_7_books"],
        ["other_table"]
    ]
    
    # Test on non-sql_classroom database (should pass through)
    new_cols, new_data = process_show_tables_result_for_schema(columns, data, "other_db", 1)
    assert new_cols == columns and new_data == data
    print("✅ Non-sql_classroom passthrough works!")
    
    print("\n🎉 Basic functionality verified!")
    print("Ready to test with web interface.")

if __name__ == "__main__":
    main()
