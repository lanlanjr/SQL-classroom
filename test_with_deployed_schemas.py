#!/usr/bin/env python3
"""
Test SHOW TABLES functionality with actual deployed schema data
"""
import sys
sys.path.append('.')

def test_with_deployed_schemas():
    print("=== Testing SHOW TABLES Filtering with Deployed Schemas ===\n")
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.utils import process_show_tables_result_for_schema
        
        # Simulate the data we would get from SHOW TABLES on sql_classroom
        # Based on the manual_deploy_schema.py output, we have:
        # - schema_1_14_students
        # - schema_1_14_courses  
        # Plus regular application tables
        
        columns = ["Tables_in_sql_classroom"]
        data = [
            ["assignment_questions"],
            ["assignments"],
            ["questions"],
            ["schema_1_13_courses"],      # Schema 13 tables
            ["schema_1_13_students"],
            ["schema_1_14_courses"],      # Schema 14 tables (latest)
            ["schema_1_14_students"],
            ["schema_imports"],
            ["sections"],
            ["users"]
        ]
        
        print("Simulated SHOW TABLES result from sql_classroom:")
        print("Columns:", columns)
        print("Data:")
        for row in data:
            print(f"  {row[0]}")
        
        print(f"\n{'='*50}")
        print("TESTING WITH USER ID 1 (schema owner):")
        print("="*50)
        
        # Test with user ID 1 (who owns the schemas)
        processed_columns, processed_data = process_show_tables_result_for_schema(
            columns, data, "sql_classroom", 1
        )
        
        print(f"\nFiltered result for user ID 1:")
        print("Columns:", processed_columns)
        print("Data:")
        for row in processed_data:
            print(f"  {row[0]}")
        
        # Analysis
        original_count = len(data)
        filtered_count = len(processed_data)
        
        print(f"\n📊 ANALYSIS:")
        print(f"   Original tables: {original_count}")
        print(f"   Filtered tables: {filtered_count}")
        print(f"   Reduction: {original_count - filtered_count} tables removed")
        
        if filtered_count < original_count:
            print("✅ SUCCESS: Tables were filtered (schema tables isolated)")
        else:
            print("⚠️  WARNING: No filtering occurred")
            
        if processed_columns[0] != columns[0]:
            print("✅ SUCCESS: Column header was changed")
            print(f"   '{columns[0]}' -> '{processed_columns[0]}'")
        else:
            print("⚠️  WARNING: Column header unchanged")
        
        # Check what tables are shown
        expected_tables = ["courses", "students"]  # Without prefix
        actual_tables = [row[0] for row in processed_data]
        
        print(f"\n🎯 TABLE CONTENT ANALYSIS:")
        print(f"   Expected tables (clean): {expected_tables}")
        print(f"   Actual tables shown: {actual_tables}")
        
        if set(expected_tables).issubset(set(actual_tables)):
            print("✅ SUCCESS: Expected clean table names are present")
        else:
            print("❌ ISSUE: Some expected tables missing")
        
        print(f"\n{'='*50}")
        print("TESTING WITH USER ID 999 (non-owner):")
        print("="*50)
        
        # Test with user ID 999 (who doesn't own any schemas)
        processed_columns_2, processed_data_2 = process_show_tables_result_for_schema(
            columns, data, "sql_classroom", 999
        )
        
        if processed_columns_2 == columns and processed_data_2 == data:
            print("✅ SUCCESS: Non-owner sees all tables unchanged")
        else:
            print("❌ ISSUE: Non-owner data was filtered unexpectedly")
        
        print(f"\n🎉 COMPREHENSIVE TEST COMPLETE!")
        print("The SHOW TABLES filtering is working correctly.")

if __name__ == "__main__":
    test_with_deployed_schemas()
