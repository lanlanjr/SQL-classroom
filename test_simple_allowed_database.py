#!/usr/bin/env python3
"""
Simple test script for AllowedDatabase functionality
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic AllowedDatabase functionality."""
    try:
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            from app.models.allowed_database import AllowedDatabase
            from app.utils import is_show_databases_query, filter_show_databases_result
            
            print("✓ Successfully imported AllowedDatabase model")
            print("✓ Successfully imported utility functions")
            
            # Test query detection
            assert is_show_databases_query("SHOW DATABASES") == True
            assert is_show_databases_query("SELECT * FROM users") == False
            print("✓ Query detection working")
            
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
            
            # Test static methods
            active_dbs = AllowedDatabase.get_active_database_names()
            print(f"✓ Active databases: {active_dbs}")
            
            # Test permission check with no databases configured
            is_allowed = AllowedDatabase.is_database_allowed('test_db')
            print(f"✓ Permission check for 'test_db': {is_allowed}")
            
            print("\n🎉 Basic functionality test passed!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the basic test."""
    print("Testing basic AllowedDatabase functionality...\n")
    
    if test_basic_functionality():
        print("\nTest completed successfully!")
        return 0
    else:
        print("\nTest failed!")
        return 1


if __name__ == '__main__':
    exit(main())
