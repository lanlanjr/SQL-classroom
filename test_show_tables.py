#!/usr/bin/env python3
"""
Test script for the SHOW TABLES filtering functionality
"""

# Test the helper functions we created
def test_find_matching_schema_tables():
    """Test the helper function that finds matching schema tables"""
    
    # Mock schema object
    class MockSchema:
        def __init__(self, active_schema_name, name):
            self.active_schema_name = active_schema_name
            self.name = name
    
    # Test data
    schemas = [
        MockSchema("schema_1_23_", "ClassicModels"),
        MockSchema("schema_2_15_", "Hospital")
    ]
    
    table_names = [
        'assignment_questions',
        'assignments', 
        'questions',
        'schema_1_23_customers',
        'schema_1_23_employees',
        'schema_1_23_offices',
        'schema_1_23_orderdetails',
        'schema_1_23_orders',
        'schema_1_23_payments',
        'schema_1_23_productlines',
        'schema_1_23_products',
        'schema_imports',
        'section_assignments',
        'sections',
        'student_enrollments',
        'submissions',
        'users'
    ]
    
    # Simulate the function logic
    def find_matching_schema_tables(schemas, table_names):
        for schema in schemas:
            prefix = schema.active_schema_name
            if prefix:
                schema_tables = [table for table in table_names if table.startswith(prefix)]
                if schema_tables:
                    return schema, schema_tables
        return None, []
    
    matching_schema, matching_tables = find_matching_schema_tables(schemas, table_names)
    
    print("Original tables:")
    for table in table_names:
        print(f"  {table}")
    
    print(f"\nMatching schema: {matching_schema.name if matching_schema else 'None'}")
    print(f"Prefix: {matching_schema.active_schema_name if matching_schema else 'None'}")
    
    print(f"\nMatching tables (with prefix):")
    for table in matching_tables:
        print(f"  {table}")
    
    print(f"\nClean table names (without prefix):")
    if matching_schema and matching_tables:
        prefix = matching_schema.active_schema_name
        for table in matching_tables:
            if table.startswith(prefix):
                clean_name = table[len(prefix):]
                print(f"  {clean_name}")
    
    print(f"\nExpected result format:")
    print("Column: ['Tables']")
    if matching_schema and matching_tables:
        prefix = matching_schema.active_schema_name
        clean_tables = []
        for table in matching_tables:
            if table.startswith(prefix):
                clean_name = table[len(prefix):]
                clean_tables.append(clean_name)
        print("Data:")
        for table in clean_tables:
            print(f"  ['{table}']")

if __name__ == "__main__":
    test_find_matching_schema_tables()
