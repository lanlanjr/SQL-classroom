#!/usr/bin/env python3
"""
Run the database migration to upgrade schema_content column
"""
import sys
import subprocess
import os

def run_migration():
    """
    Run the Flask database migration to upgrade the schema_content column
    """
    try:
        print("🔧 Running database migration to upgrade schema_content column...")
        print("   This will change TEXT to LONGTEXT (65KB -> 4GB capacity)")
        print()
        
        # Change to the project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the migration
        print("▶️  Executing: flask db upgrade")
        result = subprocess.run([
            sys.executable, '-m', 'flask', 'db', 'upgrade'
        ], capture_output=True, text=True, env=dict(os.environ, FLASK_APP='run.py'))
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            print()
            print("📈 Benefits:")
            print("   • schema_content column now supports up to 4GB")
            print("   • Large phpMyAdmin exports can now be imported")
            print("   • No more 'Data too long' errors")
            print()
            print("🚀 You can now retry importing your large SQL schema!")
        else:
            print("❌ Migration failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        print()
        print("💡 Alternative solutions:")
        print("   1. Manually run: flask db upgrade")
        print("   2. Or manually execute this SQL:")
        print("      ALTER TABLE schema_imports MODIFY COLUMN schema_content LONGTEXT NOT NULL;")

if __name__ == "__main__":
    run_migration()
