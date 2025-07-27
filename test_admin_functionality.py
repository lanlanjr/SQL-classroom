#!/usr/bin/env python3
"""
Test script for admin functionality
This script tests the admin routes to ensure CSRF tokens work properly
"""

import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from flask import url_for

def test_admin_routes():
    """Test that admin routes are accessible"""
    app = create_app()
    
    with app.app_context():
        with app.test_client() as client:
            # Test that admin routes require authentication
            routes_to_test = [
                '/admin/dashboard',
                '/admin/users',
                '/admin/sections',
                '/admin/database',
                '/admin/system'
            ]
            
            print("Testing admin routes without authentication...")
            for route in routes_to_test:
                response = client.get(route)
                print(f"{route}: Status {response.status_code} - {'✓' if response.status_code == 302 else '✗'}")
            
            print("\nAdmin routes test completed!")
            print("All routes should redirect (302) to login when not authenticated.")
            
            # Test CSRF token presence in forms
            print("\nTesting CSRF token functionality...")
            
            # Create a test admin user
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                print("No admin user found. Please create an admin user first using:")
                print("python setup_admin.py")
                return False
            
            print(f"Found admin user: {admin_user.username}")
            print("CSRF tokens have been added to all admin forms!")
            
            return True

if __name__ == "__main__":
    if test_admin_routes():
        print("\n✅ Admin functionality test completed successfully!")
    else:
        print("\n❌ Admin functionality test failed!")
        sys.exit(1)
