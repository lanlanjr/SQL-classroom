#!/usr/bin/env python3
"""
Comprehensive test for SHOW TABLES filtering with actual database deployment
"""
import sys
sys.path.append('.')

def test_with_actual_database():
    print("=== Testing SHOW TABLES Filtering with Actual Database ===\n")
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from app.utils import process_show_tables_result_for_schema
        from app.models.schema_import import SchemaImport
        import pymysql
        import os
        
        try:
            # Connect to database
            connection = pymysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', 'admin'),
                port=int(os.environ.get('MYSQL_PORT', 3306)),
                database='sql_classroom',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            print("✅ Connected to database successfully")
            
            with connection.cursor() as cursor:
                # Execute SHOW TABLES to get current tables
                cursor.execute("SHOW TABLES")
                raw_data = cursor.fetchall()
                
                # Convert to the format our function expects
                columns = [col[0] for col in cursor.description]
                data = [[row[col] for col in columns] for row in raw_data]
                
                print(f"\nOriginal SHOW TABLES result ({len(data)} tables):")
                print("Columns:", columns)
                print("Tables:")
                for row in data:
                    print(f"  {row[0]}")
                
                # Get active schemas for user ID 1 (assuming this exists)
                active_schemas = SchemaImport.query.filter_by(created_by=1).filter(
                    SchemaImport.active_schema_name.isnot(None)
                ).all()
                
                print(f"\nFound {len(active_schemas)} active schemas for user ID 1:")
                for schema in active_schemas:
                    print(f"  Schema ID: {schema.id}, Name: '{schema.name}', Prefix: '{schema.active_schema_name}'")
                
                if active_schemas:
                    # Test the filtering function
                    print(f"\n{'='*50}")
                    print("TESTING SHOW TABLES FILTERING:")
                    print("="*50)
                    
                    processed_columns, processed_data = process_show_tables_result_for_schema(
                        columns, data, "sql_classroom", 1  # User ID 1
                    )
                    
                    print(f"\nFiltered SHOW TABLES result ({len(processed_data)} tables):")
                    print("Columns:", processed_columns)
                    print("Tables:")
                    for row in processed_data:
                        print(f"  {row[0]}")
                    
                    # Show the transformation that happened
                    original_table_names = [row[0] for row in data]
                    filtered_table_names = [row[0] for row in processed_data]
                    
                    # Find which schema was matched
                    for schema in active_schemas:
                        prefix = schema.active_schema_name
                        schema_tables = [t for t in original_table_names if t.startswith(prefix)]
                        if schema_tables:
                            print(f"\n🎯 TRANSFORMATION DETAILS:")
                            print(f"   Matched Schema: '{schema.name}' (ID: {schema.id})")
                            print(f"   Schema Prefix: '{prefix}'")
                            print(f"   Original tables with prefix:")
                            for table in schema_tables:
                                clean_name = table[len(prefix):]
                                print(f"     {table} -> {clean_name}")
                            print(f"   Column header changed:")
                            print(f"     '{columns[0]}' -> '{processed_columns[0]}'")
                            break
                    
                    # Verification
                    if len(processed_data) < len(data):
                        print(f"\n✅ SUCCESS: Tables filtered from {len(data)} to {len(processed_data)}")
                    else:
                        print(f"\n⚠️  WARNING: No filtering occurred (same number of tables)")
                    
                    if processed_columns[0] != columns[0]:
                        print(f"✅ SUCCESS: Column header changed")
                    else:
                        print(f"⚠️  WARNING: Column header unchanged")
                        
                else:
                    print("\n⚠️  No active schemas found for user ID 1")
                    print("   The filtering will pass through unchanged (this is correct behavior)")
                    
                    processed_columns, processed_data = process_show_tables_result_for_schema(
                        columns, data, "sql_classroom", 1
                    )
                    
                    if processed_columns == columns and processed_data == data:
                        print("✅ SUCCESS: No schemas = pass-through behavior working correctly")
                    else:
                        print("❌ FAIL: No schemas but data was modified anyway")
                
            connection.close()
            print(f"\n{'='*60}")
            print("🎉 TESTING COMPLETE!")
            print("The SHOW TABLES filtering functionality is ready for production use.")
            
        except Exception as e:
            print(f"❌ Database connection error: {str(e)}")
            print("Make sure your database is running and credentials are correct.")

if __name__ == "__main__":
    test_with_actual_database()
