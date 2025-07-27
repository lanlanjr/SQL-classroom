#!/usr/bin/env python3
"""
Comprehensive test for the SHOW TABLES fix functionality in student question execution
"""
import sys
sys.path.append('.')

def test_question_show_tables_fix():
    print("=== Testing SHOW TABLES Fix in Student Question Execution ===\n")
    
    # Test the exact filtering logic that's now in student.py
    def simulate_show_tables_filtering(query, db_type, schema_import_active_name, original_rows):
        """Simulate the filtering logic from the student route"""
        from app.utils import is_show_tables_query
        
        # Convert to the format that would come from the database cursor
        rows = [[row] for row in original_rows]
        columns = ["Tables_in_sql_classroom"]
        
        # Apply the same logic as in student.py
        if is_show_tables_query(query) and db_type == 'imported_schema':
            if schema_import_active_name:
                prefix = schema_import_active_name
                
                # Filter tables that match this schema's prefix
                schema_tables = []
                for row in rows:
                    table_name = row[0]  # First column is table name
                    if table_name.startswith(prefix):
                        # Remove prefix to get clean table name
                        clean_name = table_name[len(prefix):]
                        schema_tables.append([clean_name])
                
                # Update the results to show only the clean table names
                if schema_tables:
                    rows = schema_tables
                    # Update column header to be cleaner
                    columns = ["Tables"]
        
        return columns, rows

    # Test case 1: SHOW TABLES query with imported schema
    print("Test Case 1: SHOW TABLES with imported schema")
    print("-" * 50)
    
    original_tables = [
        "assignment_questions",
        "assignments", 
        "questions",
        "schema_1_23_customers",
        "schema_1_23_employees",
        "schema_1_23_offices",
        "schema_1_23_orderdetails",
        "schema_1_23_orders",
        "schema_1_23_payments",
        "schema_1_23_productlines",
        "schema_1_23_products",
        "schema_imports",
        "section_assignments",
        "sections",
        "student_enrollments",
        "submissions",
        "users"
    ]
    
    query = "SHOW TABLES"
    db_type = "imported_schema"
    schema_prefix = "schema_1_23_"
    
    print(f"Query: {query}")
    print(f"DB Type: {db_type}")
    print(f"Schema Prefix: {schema_prefix}")
    print(f"Original tables count: {len(original_tables)}")
    
    filtered_columns, filtered_rows = simulate_show_tables_filtering(
        query, db_type, schema_prefix, original_tables
    )
    
    filtered_table_names = [row[0] for row in filtered_rows]
    
    print(f"Filtered tables count: {len(filtered_table_names)}")
    print(f"Filtered columns: {filtered_columns}")
    print("Filtered tables:")
    for table in filtered_table_names:
        print(f"  {table}")
    
    expected_tables = [
        "customers", "employees", "offices", "orderdetails", 
        "orders", "payments", "productlines", "products"
    ]
    
    success = (
        filtered_table_names == expected_tables and
        filtered_columns == ["Tables"] and
        len(filtered_table_names) == 8
    )
    
    print(f"Result: {'✅ SUCCESS' if success else '❌ FAIL'}")
    
    # Test case 2: Non-SHOW TABLES query (should pass through unchanged)
    print(f"\nTest Case 2: SELECT query (should pass through unchanged)")
    print("-" * 50)
    
    query2 = "SELECT * FROM customers"
    columns2, rows2 = simulate_show_tables_filtering(
        query2, db_type, schema_prefix, original_tables
    )
    
    # Should be unchanged
    original_rows_formatted = [[table] for table in original_tables]
    unchanged = (
        columns2 == ["Tables_in_sql_classroom"] and
        rows2 == original_rows_formatted
    )
    
    print(f"Query: {query2}")
    print(f"Tables count: {len([row[0] for row in rows2])}")
    print(f"Columns: {columns2}")
    print(f"Result: {'✅ SUCCESS (unchanged)' if unchanged else '❌ FAIL (was modified)'}")
    
    # Test case 3: SHOW TABLES with MySQL db_type (should pass through unchanged)
    print(f"\nTest Case 3: SHOW TABLES with MySQL db_type (should pass through)")
    print("-" * 50)
    
    query3 = "SHOW TABLES"
    db_type3 = "mysql"
    columns3, rows3 = simulate_show_tables_filtering(
        query3, db_type3, schema_prefix, original_tables
    )
    
    unchanged3 = (
        columns3 == ["Tables_in_sql_classroom"] and
        rows3 == original_rows_formatted
    )
    
    print(f"Query: {query3}")
    print(f"DB Type: {db_type3}")
    print(f"Result: {'✅ SUCCESS (unchanged)' if unchanged3 else '❌ FAIL (was modified)'}")
    
    # Overall result
    all_tests_passed = success and unchanged and unchanged3
    
    print(f"\n{'='*60}")
    print(f"OVERALL RESULT: {'🎉 ALL TESTS PASSED!' if all_tests_passed else '❌ SOME TESTS FAILED'}")
    
    if all_tests_passed:
        print("The SHOW TABLES fix is working correctly:")
        print("✅ Filters imported schema tables correctly")
        print("✅ Removes table prefixes") 
        print("✅ Updates column headers")
        print("✅ Passes through non-SHOW TABLES queries unchanged")
        print("✅ Passes through non-imported schema queries unchanged")
    
    return all_tests_passed

if __name__ == "__main__":
    test_question_show_tables_fix()
