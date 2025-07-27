#!/usr/bin/env python3
"""
Manual schema deployment script to debug table creation
"""
import pymysql
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def deploy_schema_manually():
    # Get schema content from database
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
            # First, let's see what schemas exist
            cursor.execute("SELECT id, name, schema_content, active_schema_name FROM schema_imports")
            all_schemas = cursor.fetchall()
            
            print("All schemas in database:")
            for schema in all_schemas:
                schema_id, name, content, active_name = schema
                content_length = len(content) if content else 0
                print(f"  ID: {schema_id}, Name: {name}, Content Length: {content_length}, Active: {active_name}")
            
            if not all_schemas:
                print("No schemas found in database!")
                return
            
            # Use the latest schema
            latest_schema = all_schemas[-1]  # Get the last one
            schema_id, schema_name, schema_content, active_schema_name = latest_schema
            
            print(f"\nUsing latest schema: ID {schema_id}, Name: {schema_name}")
            print(f"Content length: {len(schema_content)} characters")
            print(f"Active schema name: {active_schema_name}")
            print(f"Content preview:\n{schema_content[:500]}...")
            
            # Parse statements using the improved parser
            # Import the function from app.utils
            import sys
            sys.path.append('.')
            from app.utils import parse_schema_statements
            
            statements = parse_schema_statements(schema_content)
            print(f"\nParsed {len(statements)} statements using improved parser")
            
            # Look for CREATE TABLE statements and filtered statements
            create_table_statements = []
            create_database_statements = []
            use_statements = []
            
            for i, stmt in enumerate(statements):
                if len(stmt) > 100:
                    preview = stmt[:100] + "..."
                else:
                    preview = stmt
                print(f"\nStatement {i+1}: {preview}")
                
                stmt_upper = stmt.upper().strip()
                
                if stmt_upper.startswith('CREATE TABLE'):
                    create_table_statements.append(stmt)
                    print(f"  -> This is a CREATE TABLE statement")
                    
                    # Try to extract table name
                    try:
                        import re
                        pattern = r'CREATE\s+TABLE\s+`?([^`\s(]+)`?'
                        match = re.search(pattern, stmt, re.IGNORECASE)
                        if match:
                            table_name = match.group(1)
                            print(f"  -> Extracted table name: '{table_name}'")
                    except Exception as e:
                        print(f"  -> Error extracting table name: {e}")
                
                elif stmt_upper.startswith('CREATE DATABASE') or stmt_upper.startswith('CREATE SCHEMA'):
                    create_database_statements.append(stmt)
                    print(f"  -> CREATE DATABASE/SCHEMA statement (should be filtered)")
                
                elif stmt_upper.startswith('USE '):
                    use_statements.append(stmt)
                    print(f"  -> USE statement (should be filtered)")
            
            print(f"\nSummary:")
            print(f"  - CREATE TABLE statements: {len(create_table_statements)}")
            print(f"  - CREATE DATABASE statements found in original (should be 0 after filtering): {len(create_database_statements)}")
            print(f"  - USE statements found in original (should be 0 after filtering): {len(use_statements)}")
            
            if create_database_statements:
                print(f"\n⚠️  WARNING: Found CREATE DATABASE statements that should have been filtered:")
                for stmt in create_database_statements:
                    print(f"    {stmt[:100]}...")
            
            if use_statements:
                print(f"\n⚠️  WARNING: Found USE statements that should have been filtered:")
                for stmt in use_statements:
                    print(f"    {stmt[:100]}...")
            
            if len(create_table_statements) == 0:
                print("ERROR: No CREATE TABLE statements found!")
                print("This explains why no tables are being created.")
                print("\nLet's check the actual content:")
                print("="*50)
                print(schema_content)
                print("="*50)
            else:
                # Try to create tables with prefix
                table_prefix = f"schema_1_{schema_id}_"
                print(f"\nUsing table prefix: {table_prefix}")
                
                for stmt in create_table_statements:
                    try:
                        # Extract table name
                        table_start = stmt.upper().find('TABLE') + 5
                        table_part = stmt[table_start:].strip()
                        original_table = table_part.split()[0].strip('`').rstrip('(').strip('`')
                        
                        # Create modified statement
                        modified_stmt = re.sub(
                            r'CREATE TABLE\s+`?' + re.escape(original_table) + r'`?',
                            f'CREATE TABLE `{table_prefix}{original_table}`',
                            stmt,
                            flags=re.IGNORECASE
                        )
                        
                        print(f"\nOriginal: {stmt[:100]}...")
                        print(f"Modified: {modified_stmt[:100]}...")
                        
                        # Try to execute
                        cursor.execute(f"DROP TABLE IF EXISTS `{table_prefix}{original_table}`")
                        cursor.execute(modified_stmt)
                        print(f"✓ Successfully created table: {table_prefix}{original_table}")
                        
                    except Exception as e:
                        print(f"✗ Error creating table: {e}")
                
                # Verify tables were created
                cursor.execute("SHOW TABLES")
                all_tables = [row[0] for row in cursor.fetchall()]
                prefixed_tables = [t for t in all_tables if t.startswith(table_prefix)]
                print(f"\nVerification: {len(prefixed_tables)} tables created with prefix {table_prefix}")
                for table in prefixed_tables:
                    print(f"  - {table}")
                
                connection.commit()
                print("\nCommitted changes to database")
        
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    deploy_schema_manually()
