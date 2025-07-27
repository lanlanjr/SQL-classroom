"""
Migration script to add database_name field to sections table
"""
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.section import Section

def run_migration():
    """Add database_name column to sections table if it doesn't exist"""
    
    app = create_app()
    with app.app_context():
        # Check if we need to add the column by inspecting the table
        inspector = db.inspect(db.engine)
        columns = [column['name'] for column in inspector.get_columns('sections')]
        
        if 'database_name' not in columns:

            
            # Use direct SQL to add the column since we can't use Alembic migrations easily
            db.engine.execute("""
                ALTER TABLE sections 
                ADD COLUMN database_name VARCHAR(100) NULL
            """)
            

        else:


if __name__ == '__main__':
    run_migration()
