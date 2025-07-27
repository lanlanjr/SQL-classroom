#!/usr/bin/env python3
"""
Script to create an admin account for the SQL Classroom application.
This script should be run once to set up the initial admin user.
"""

import os
import sys
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.user import User

def create_admin_account():
    """Create an admin account"""
    
    # Initialize the Flask app and database
    app = create_app()
    
    with app.app_context():
        # Check if any admin accounts already exist
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            print(f"Admin account already exists: {existing_admin.username} ({existing_admin.email})")
            response = input("Do you want to create another admin account? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Admin account creation cancelled.")
                return
        
        print("Creating SQL Classroom Admin Account")
        print("=" * 40)
        
        # Get admin details from user input
        while True:
            username = input("Enter admin username: ").strip()
            if not username:
                print("Username cannot be empty!")
                continue
            
            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"Username '{username}' already exists!")
                continue
            break
        
        while True:
            email = input("Enter admin email: ").strip()
            if not email or '@' not in email:
                print("Please enter a valid email address!")
                continue
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print(f"Email '{email}' already exists!")
                continue
            break
        
        while True:
            password = input("Enter admin password: ").strip()
            if len(password) < 6:
                print("Password must be at least 6 characters long!")
                continue
            break
        
        first_name = input("Enter first name (default: Admin): ").strip() or "Admin"
        last_name = input("Enter last name (default: User): ").strip() or "User"
        
        # Create the admin user
        try:
            admin_user = User(
                username=username,
                email=email,
                role='admin',
                first_name=first_name,
                last_name=last_name
            )
            admin_user.set_password(password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("\n" + "=" * 40)
            print("✅ Admin account created successfully!")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Name: {first_name} {last_name}")
            print(f"Role: admin")
            print("\nYou can now log in to the admin panel at /admin/dashboard")
            print("=" * 40)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating admin account: {str(e)}")
            return False
    
    return True

def list_admin_accounts():
    """List all existing admin accounts"""
    app = create_app()
    
    with app.app_context():
        admins = User.query.filter_by(role='admin').all()
        
        if not admins:
            print("No admin accounts found.")
            return
        
        print("\nExisting Admin Accounts:")
        print("-" * 40)
        for admin in admins:
            print(f"ID: {admin.id}")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Name: {admin.full_name}")
            print(f"Created: {admin.created_at}")
            print("-" * 40)

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_admin_accounts()
        return
    
    print("SQL Classroom - Admin Account Management")
    print("=" * 50)
    
    # Check if we have command line arguments for non-interactive mode
    if len(sys.argv) >= 6:
        username, email, password, first_name, last_name = sys.argv[1:6]
        
        app = create_app()
        with app.app_context():
            try:
                # Check if username or email already exists
                if User.query.filter_by(username=username).first():
                    print(f"❌ Username '{username}' already exists!")
                    return False
                
                if User.query.filter_by(email=email).first():
                    print(f"❌ Email '{email}' already exists!")
                    return False
                
                admin_user = User(
                    username=username,
                    email=email,
                    role='admin',
                    first_name=first_name,
                    last_name=last_name
                )
                admin_user.set_password(password)
                
                db.session.add(admin_user)
                db.session.commit()
                
                print(f"✅ Admin account '{username}' created successfully!")
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating admin account: {str(e)}")
                return False
    else:
        # Interactive mode
        return create_admin_account()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
