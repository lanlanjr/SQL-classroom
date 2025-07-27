#!/usr/bin/env python3
"""
Test script for AllowedDatabase functionality
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db


def test_allowed_database_model():
    """Test the AllowedDatabase model functionality."""
    print("Testing AllowedDatabase model...")
    
    app = create_app()
    with app.app_context():
        from app.models.user import User
        from app.models.allowed_database import AllowedDatabase
        
        # Test empty state
        assert AllowedDatabase.get_active_database_names() == []
        assert AllowedDatabase.is_database_allowed('any_db') == True  # No restrictions when empty
        print("✓ Empty state tests passed")
        
        # Create test admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found - please run reset_app.py first")
            return False
        
        # Add some test allowed databases
        db1 = AllowedDatabase(
            database_name='classicmodels',
            description='Classic models sample database',
            created_by=admin.id
        )
        db2 = AllowedDatabase(
            database_name='sakila',
            description='Sakila sample database',
            created_by=admin.id
        )
        db3 = AllowedDatabase(
            database_name='test_db',
            description='Test database',
            is_active=False,  # Inactive
            created_by=admin.id
        )
        
        # Temporarily add to session for testing
        db.session.add(db1)
        db.session.add(db2)
        db.session.add(db3)
        db.session.commit()
        
        try:
            # Test getting active databases
            active_dbs = AllowedDatabase.get_active_database_names()
            expected = ['classicmodels', 'sakila']
            assert set(active_dbs) == set(expected), f"Expected {expected}, got {active_dbs}"
            print("✓ Active database retrieval tests passed")
            
            # Test database permission checking
            assert AllowedDatabase.is_database_allowed('classicmodels') == True
            assert AllowedDatabase.is_database_allowed('sakila') == True
            assert AllowedDatabase.is_database_allowed('test_db') == False  # Inactive
            assert AllowedDatabase.is_database_allowed('forbidden_db') == False
            print("✓ Database permission tests passed")
            
        finally:
            # Clean up test data
            AllowedDatabase.query.filter(AllowedDatabase.database_name.in_(['classicmodels', 'sakila', 'test_db'])).delete(synchronize_session=False)
            db.session.commit()
        
        print("✓ AllowedDatabase model tests completed successfully")
        return True


def test_show_databases_filtering():
    """Test the SHOW DATABASES filtering functionality."""
    print("\nTesting SHOW DATABASES filtering...")
    
    from app.utils import is_show_databases_query, filter_show_databases_result
    
    # Test query detection
    assert is_show_databases_query("SHOW DATABASES") == True
    assert is_show_databases_query("show databases;") == True
    assert is_show_databases_query("SHOW SCHEMAS") == True
    assert is_show_databases_query("SELECT * FROM users") == False
    print("✓ Query detection tests passed")
    
    # Test filtering with mock data
    columns = ['Database']
    rows = [
        ['information_schema'],
        ['mysql'],
        ['performance_schema'],
        ['classicmodels'],
        ['sakila'],
        ['forbidden_db']
    ]
    
    app = create_app()
    with app.app_context():
        from app.models.user import User
        from app.models.allowed_database import AllowedDatabase
        
        # Test with no allowed databases (should return all)
        filtered_columns, filtered_rows = filter_show_databases_result(columns, rows)
        assert len(filtered_rows) == len(rows)
        print("✓ No restrictions filtering test passed")
        
        # Create test admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found - please run reset_app.py first")
            return False
        
        # Add allowed databases for testing
        db1 = AllowedDatabase(
            database_name='classicmodels',
            description='Classic models sample database',
            created_by=admin.id
        )
        db2 = AllowedDatabase(
            database_name='sakila',
            description='Sakila sample database',
            created_by=admin.id
        )
        
        db.session.add(db1)
        db.session.add(db2)
        db.session.commit()
        
        try:
            # Test with restrictions
            filtered_columns, filtered_rows = filter_show_databases_result(columns, rows)
            expected_dbs = ['classicmodels', 'sakila']
            actual_dbs = [row[0] for row in filtered_rows]
            assert set(actual_dbs) == set(expected_dbs), f"Expected {expected_dbs}, got {actual_dbs}"
            print("✓ Restricted filtering test passed")
            
        finally:
            # Clean up
            AllowedDatabase.query.filter(AllowedDatabase.database_name.in_(['classicmodels', 'sakila'])).delete(synchronize_session=False)
            db.session.commit()
    
    print("✓ SHOW DATABASES filtering tests completed successfully")
    return True


def main():
    """Run all tests."""
    print("Starting AllowedDatabase functionality tests...\n")
    
    try:
        success = True
        success &= test_allowed_database_model()
        success &= test_show_databases_filtering()
        
        if success:
            print("\n🎉 All tests passed! AllowedDatabase functionality is working correctly.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
