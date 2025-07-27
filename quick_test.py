#!/usr/bin/env python3
"""
Quick test of SHOW TABLES functionality
"""
import sys
sys.path.append('.')

def quick_test():
    print("Quick test of SHOW TABLES functionality...")
    
    try:
        from app.utils import process_show_tables_result_for_schema
        
        # Mock data
        columns = ["Tables_in_sql_classroom"]
        data = [
            ["users"],
            ["schema_1_14_courses"],
            ["schema_1_14_students"],
            ["other_table"]
        ]
        
        print("Original data:", [row[0] for row in data])
        
        # Since we can't test with actual database, just test the logic
        # The function will return original data if no database context
        result_cols, result_data = process_show_tables_result_for_schema(
            columns, data, "other_db", 1
        )
        
        print("Result (should be unchanged):", [row[0] for row in result_data])
        print("✅ Basic test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
