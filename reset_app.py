"""
Reset Application Script - Cleans database and runs all migrations
"""
import os
from app import create_app, db
from app.models import User
from migrations.unified_migration import upgrade as run_migrations
import pymysql
from sqlalchemy import text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reset_database():
    app = create_app()
    
    with app.app_context():
        print("Starting database reset...")
        
        try:
            # Get database name from environment
            app_db_name = os.environ.get('APP_DB_NAME', 'sql_classroom')
            
            # Create the database if it doesn't exist
            connection = pymysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', 'admin'),
                port=int(os.environ.get('MYSQL_PORT', 3306))
            )
            with connection.cursor() as cursor:
                # Drop the database if it exists and create it fresh
                cursor.execute(f"DROP DATABASE IF EXISTS {app_db_name}")
                cursor.execute(f"CREATE DATABASE {app_db_name}")
                cursor.execute(f"USE {app_db_name}")
            connection.close()
            print(f"Created fresh database: {app_db_name}")
            
            # Create core tables
            db.create_all()
            print("Core tables created")
            
            # Run our unified migration for all additional features
            run_migrations()
            print("All migrations applied")
            
            # Create an admin/teacher user
            admin = User(
                username="admin",
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                role="teacher"
            )
            admin.set_password("password")
            db.session.add(admin)
            
            db.session.commit()
            print("Admin user created with username 'admin' and password 'password'")
            
            # Create classicmodels database if it doesn't exist
            connection = pymysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', 'admin'),
                port=int(os.environ.get('MYSQL_PORT', 3306))
            )
            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS classicmodels")
            connection.close()
            print("Created classicmodels database if it didn't exist")
            
            print("Database reset completed successfully!")
            
        except Exception as e:
            print(f"Error during database reset: {str(e)}")
            raise

if __name__ == "__main__":
    # Reset database
    reset_database()