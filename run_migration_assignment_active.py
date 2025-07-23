import os
from sqlalchemy import text
from app import create_app, db

# Create a Flask app context
app = create_app()

print("Adding is_active column to section_assignments table")
try:
    with app.app_context():
        # Connect directly to the database and execute the SQL
        engine = db.engine
        with engine.connect() as connection:
            # Check if the column already exists using MySQL syntax
            result = connection.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name='section_assignments' 
                AND column_name='is_active'
            """))
            column_exists = result.scalar() > 0
            
            if not column_exists:
                # Add the column with default value 1 (True)
                connection.execute(text(
                    "ALTER TABLE section_assignments ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"
                ))
                print("Migration completed successfully!")
            else:
                print("Column is_active already exists in section_assignments table")
except Exception as e:
    print(f"Error running migration: {str(e)}") 