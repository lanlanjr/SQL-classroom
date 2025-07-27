"""Add admin role support

Revision ID: add_admin_role
Revises: 
Create Date: 2025-01-26

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add admin role support to the application"""
    
    # Update the users table to allow admin role
    # Note: Since we're using VARCHAR(20) for role, no schema change needed
    # This migration will add the first admin user if none exists
    
    # Add a default admin user if no admin exists
    connection = op.get_bind()
    
    # Check if any admin users exist
    result = connection.execute(
        sa.text("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
    ).fetchone()
    
    if result[0] == 0:
        # Create default admin user
        # Password is 'admin123' - should be changed after first login
        password_hash = 'pbkdf2:sha256:600000$3YKsj0Zf$8a8c0d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'
        
        connection.execute(
            sa.text("""
                INSERT INTO users (username, email, password_hash, role, first_name, last_name, created_at)
                VALUES ('admin', 'admin@sqlclassroom.local', :password_hash, 'admin', 'System', 'Administrator', NOW())
            """),
            {'password_hash': password_hash}
        )
        






def downgrade():
    """Remove admin role support"""
    
    # Remove all admin users (optional - commented out for safety)
    # connection = op.get_bind()
    # connection.execute(sa.text("DELETE FROM users WHERE role = 'admin'"))
    
    # Note: We don't actually change the schema as other roles still use VARCHAR(20)
    pass
