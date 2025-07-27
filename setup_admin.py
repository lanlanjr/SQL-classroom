#!/usr/bin/env python3
"""
Quick setup script for SQL Classroom admin functionality.
This script will:
1. Set up the database with admin support
2. Create the default admin account
3. Provide next steps for the user
"""

import os
import sys
from werkzeug.security import generate_password_hash

def setup_admin():
    """Quick setup for admin functionality"""
    
    print("SQL Classroom - Admin Setup")
    print("=" * 40)
    print("Setting up admin functionality for SQL Classroom...")
    print()
    
    try:
        # Import Flask app components
        from app import create_app, db
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            
            # Check if admin user already exists
            existing_admin = User.query.filter_by(role='admin').first()
            
            if existing_admin:
                print(f"✅ Admin user already exists: {existing_admin.username}")
                print(f"   Email: {existing_admin.email}")
                print(f"   Name: {existing_admin.full_name}")
                print()
                print("🔗 You can access the admin panel at: /admin/dashboard")
                return True
            
            # Create default admin user
            admin_password = "admin123"  # Default password
            admin_user = User(
                username="admin",
                email="admin@sqlclassroom.local",
                role="admin",
                first_name="System",
                last_name="Administrator"
            )
            admin_user.set_password(admin_password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Admin account created successfully!")
            print()
            print("📋 Admin Account Details:")
            print(f"   Username: admin")
            print(f"   Password: {admin_password}")
            print(f"   Email: admin@sqlclassroom.local")
            print()
            print("🔗 Access admin panel at: /admin/dashboard")
            print()
            print("⚠️  IMPORTANT SECURITY NOTES:")
            print("   1. Please change the default password immediately after login")
            print("   2. Consider creating a custom admin account and removing the default one")
            print("   3. The admin panel allows full control over the application")
            print()
            print("🚀 Next Steps:")
            print("   1. Start your Flask application")
            print("   2. Navigate to /admin/dashboard")
            print("   3. Log in with the credentials above")
            print("   4. Change the password in the user management section")
            print("   5. Explore the admin features!")
            
            return True
            
    except ImportError as e:
        print(f"❌ Error: Could not import Flask application components.")
        print(f"   Details: {str(e)}")
        print("   Make sure you're running this from the correct directory")
        print("   and that all dependencies are installed.")
        return False
        
    except Exception as e:
        print(f"❌ Error setting up admin functionality: {str(e)}")
        return False

def print_usage():
    """Print usage instructions"""
    print("Admin Setup Instructions:")
    print("1. Make sure you're in the SQL Classroom project directory")
    print("2. Make sure your virtual environment is activated (if using one)")
    print("3. Run: python setup_admin.py")
    print()
    print("If you need to create additional admin accounts later:")
    print("   python create_admin.py")
    print()
    print("To list existing admin accounts:")
    print("   python create_admin.py --list")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print_usage()
        sys.exit(0)
    
    success = setup_admin()
    
    if not success:
        print()
        print("Setup failed. Please check the error messages above.")
        print("For help, run: python setup_admin.py --help")
        sys.exit(1)
    
    print()
    print("✅ Admin setup completed successfully!")
    sys.exit(0)
