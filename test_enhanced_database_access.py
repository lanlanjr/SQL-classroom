#!/usr/bin/env python3
"""
Test script for enhanced AllowedDatabase functionality with teacher schemas
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_student_database_access():
    """Test the enhanced student database access functionality."""
    try:
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            from app.models.user import User
            from app.models.allowed_database import AllowedDatabase
            from app.models.schema_import import SchemaImport
            from app.models.section import Section
            from app.utils import is_show_databases_query, filter_show_databases_result
            
            print("✓ Successfully imported all required models")
            
            # Test that table exists
            result = db.session.execute(db.text("SHOW TABLES LIKE 'allowed_databases'"))
            if result.fetchone():
                print("✓ allowed_databases table exists")
            else:
                print("❌ allowed_databases table does not exist")
                return False
            
            # Test basic model functionality
            count = AllowedDatabase.query.count()
            print(f"✓ Current allowed databases count: {count}")
            
            # Check for admin user
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("❌ Admin user not found - please run reset_app.py first")
                return False
            
            print(f"✓ Admin user found: {admin.username}")
            
            # Test with no allowed databases (should allow all)
            active_dbs = AllowedDatabase.get_active_database_names()
            print(f"✓ Active databases currently: {active_dbs}")
            
            # Test permission check with no databases configured
            is_allowed = AllowedDatabase.is_database_allowed('test_db')
            print(f"✓ Permission check for 'test_db' (no restrictions): {is_allowed}")
            
            # Test SHOW DATABASES filtering
            print("\nTesting SHOW DATABASES filtering...")
            assert is_show_databases_query("SHOW DATABASES") == True
            assert is_show_databases_query("SELECT * FROM users") == False
            print("✓ Query detection working")
            
            # Test filtering with mock data
            columns = ['Database']
            rows = [
                ['information_schema'],
                ['mysql'],
                ['performance_schema'],
                ['sql_classroom'],
                ['classicmodels'],
                ['sakila']
            ]
            
            # Test with no restrictions
            filtered_columns, filtered_rows = filter_show_databases_result(columns, rows)
            print(f"✓ No restrictions - returned {len(filtered_rows)} databases")
            
            # Test adding some allowed databases
            print("\nTesting with allowed databases...")
            
            # Add test allowed databases
            db1 = AllowedDatabase(
                database_name='classicmodels',
                description='Classic models sample database',
                created_by=admin.id
            )
            db2 = AllowedDatabase(
                database_name='sql_classroom',
                description='Teacher imported schemas',
                created_by=admin.id
            )
            
            db.session.add(db1)
            db.session.add(db2)
            db.session.commit()
            
            try:
                # Test with restrictions
                filtered_columns, filtered_rows = filter_show_databases_result(columns, rows)
                actual_dbs = [row[0] for row in filtered_rows]
                expected_dbs = ['classicmodels', 'sql_classroom']
                print(f"✓ With restrictions - returned: {actual_dbs}")
                
                # Test permission checks
                assert AllowedDatabase.is_database_allowed('classicmodels') == True
                assert AllowedDatabase.is_database_allowed('sql_classroom') == True
                assert AllowedDatabase.is_database_allowed('forbidden_db') == False
                print("✓ Permission checking works correctly")
                
            finally:
                # Clean up test data
                AllowedDatabase.query.filter(AllowedDatabase.database_name.in_(['classicmodels', 'sql_classroom'])).delete(synchronize_session=False)
                db.session.commit()
                print("✓ Test data cleaned up")
            
            print("\n🎉 Enhanced database access functionality test passed!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the enhanced test."""
    print("Testing enhanced AllowedDatabase functionality with teacher schemas...\n")
    
    if test_student_database_access():
        print("\nTest completed successfully!")
        return 0
    else:
        print("\nTest failed!")
        return 1


if __name__ == '__main__':
    exit(main())
