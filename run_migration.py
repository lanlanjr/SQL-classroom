"""
Run this script to execute the migration for multiple student enrollments.
"""

from app import app, db
from migrations.add_multiple_enrollments import upgrade, downgrade
import sys

def run_upgrade():
    with app.app_context():
        print("Starting migration for multiple student enrollments...")
        upgrade()
        print("Migration completed successfully!")
        print("\nNOTE: The section_id column has not been dropped from the users table.")
        print("To complete the migration, manually run the following SQL after verification:")
        print("\nALTER TABLE users DROP COLUMN section_id;\n")

def run_downgrade():
    with app.app_context():
        print("Starting downgrade to remove multiple student enrollments...")
        downgrade()
        print("Downgrade completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        run_downgrade()
    else:
        run_upgrade() 