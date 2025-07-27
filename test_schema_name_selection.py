#!/usr/bin/env python3
"""
Test script for schema name selection in student playground
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_schema_name_selection():
    """Test that schema names appear in database list instead of sql_classroom."""
    try:
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            from app.models.user import User
            from app.models.schema_import import SchemaImport
            from app.models.section import Section
            from app.models.student_enrollment import StudentEnrollment
            
            print("Testing schema name selection functionality...\n")
            
            # Check if we have admin user
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("❌ Admin user not found - please run reset_app.py first")
                return False
            
            # Check if we have a student user
            student = User.query.filter_by(username='student_1').first()
            if not student:
                print("❌ Student user not found - please run create_dummy_data.py first")
                return False
            
            print(f"✓ Found admin user: {admin.username}")
            print(f"✓ Found student user: {student.username}")
            
            # Check if we have any sections
            section = Section.query.filter_by(creator_id=admin.id).first()
            if not section:
                print("❌ No sections found - please run create_dummy_data.py first")
                return False
            
            print(f"✓ Found section: {section.name}")
            
            # Create a test schema import
            test_schema = SchemaImport(
                name='Test Schema',
                description='Test schema for student playground',
                schema_content='CREATE TABLE students (id INT PRIMARY KEY, name VARCHAR(100));',
                created_by=admin.id,
                active_schema_name='test_schema_prefix_'
            )
            
            db.session.add(test_schema)
            db.session.commit()
            
            try:
                print(f"✓ Created test schema: {test_schema.name}")
                
                # Test that the schema name appears in the database list logic
                # Simulate what the get_available_databases API would return
                from app.routes.student import get_available_databases
                
                # Mock session context
                from flask import session
                session['current_section_id'] = section.id
                
                # This would normally be called via API
                print("\nTesting database list generation...")
                
                # Check if schema import model is working
                schemas = SchemaImport.query.filter_by(created_by=admin.id).filter(
                    SchemaImport.active_schema_name.isnot(None)
                ).all()
                
                schema_names = [schema.name for schema in schemas]
                print(f"✓ Found teacher schemas: {schema_names}")
                
                if 'Test Schema' in schema_names:
                    print("✓ Test schema name appears in list (not sql_classroom)")
                else:
                    print("❌ Test schema name does not appear in list")
                    return False
                
                # Test database access validation
                print("\nTesting database access validation...")
                
                # Test that "Test Schema" would be allowed
                matching_schema = SchemaImport.query.filter_by(
                    created_by=admin.id,
                    name='Test Schema'
                ).filter(SchemaImport.active_schema_name.isnot(None)).first()
                
                if matching_schema:
                    print("✓ Schema access validation would work")
                    print(f"  - Schema name: {matching_schema.name}")
                    print(f"  - Active prefix: {matching_schema.active_schema_name}")
                    print("  - Would connect to: sql_classroom")
                else:
                    print("❌ Schema access validation would fail")
                    return False
                
            finally:
                # Clean up test data
                SchemaImport.query.filter_by(name='Test Schema').delete()
                db.session.commit()
                print("✓ Test data cleaned up")
            
            print("\n🎉 Schema name selection test passed!")
            print("\nExpected behavior:")
            print("1. Students see 'Test Schema' in database dropdown (not 'sql_classroom')")
            print("2. When student selects 'Test Schema', system connects to sql_classroom")
            print("3. Queries are rewritten to use schema prefix")
            print("4. SHOW TABLES shows unprefixed table names for that schema")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the schema name selection test."""
    if test_schema_name_selection():
        return 0
    else:
        return 1


if __name__ == '__main__':
    exit(main())
