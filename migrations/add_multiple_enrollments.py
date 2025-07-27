"""Migration to add support for multiple enrollments per student

This migration:
1. Creates the new student_enrollments table
2. Migrates existing student-section relationships to the new table
3. Drops the section_id column from the users table
"""

from app import db
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime, Boolean, MetaData, select, func
from sqlalchemy.ext.declarative import declarative_base
import datetime

def upgrade():
    # Get metadata from current connection
    meta = MetaData()
    meta.reflect(bind=db.engine)
    
    # Get existing tables
    users = Table('users', meta, autoload_with=db.engine)
    sections = Table('sections', meta, autoload_with=db.engine)
    
    # Create new student_enrollments table
    student_enrollments = Table(
        'student_enrollments', meta,
        Column('id', Integer, primary_key=True),
        Column('student_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('section_id', Integer, ForeignKey('sections.id'), nullable=False),
        Column('enrolled_at', DateTime, default=datetime.datetime.utcnow),
        Column('is_active', Boolean, default=True)
    )
    
    meta.create_all(db.engine)
    
    # Migrate existing student-section relationships
    connection = db.engine.connect()
    transaction = connection.begin()
    
    try:
        # Get all students with section_id
        students_with_section = connection.execute(
            select([users.c.id, users.c.section_id])
            .where(users.c.section_id != None)
            .where(users.c.role == 'student')
        ).fetchall()
        
        # Insert into new enrollments table
        for student_id, section_id in students_with_section:
            connection.execute(
                student_enrollments.insert().values(
                    student_id=student_id,
                    section_id=section_id,
                    enrolled_at=datetime.datetime.utcnow(),
                    is_active=True
                )
            )
        
        transaction.commit()
    except:
        transaction.rollback()
        raise
    finally:
        connection.close()
    
    # Drop section_id column from users table (in a separate transaction)
    # Note: This is commented out for safety - run manually after verification
    # 
    # connection = db.engine.connect()
    # transaction = connection.begin()
    # try:
    #     connection.execute('ALTER TABLE users DROP COLUMN section_id')
    #     transaction.commit()
    # except:
    #     transaction.rollback()
    #     raise
    # finally:
    #     connection.close()

def downgrade():
    # Downgrade is not fully supported since data could be lost
    # when multiple enrollments exist for a student
    meta = MetaData()
    meta.reflect(bind=db.engine)
    
    # Drop student_enrollments table
    if 'student_enrollments' in meta.tables:
        student_enrollments = Table('student_enrollments', meta, autoload_with=db.engine)
        student_enrollments.drop(db.engine)
    
    # Add back section_id column if needed
    connection = db.engine.connect()
    transaction = connection.begin()
    try:
        # Check if section_id column exists in users table
        result = connection.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in result.fetchall()]
        
        if 'section_id' not in columns:
            connection.execute('ALTER TABLE users ADD COLUMN section_id INTEGER REFERENCES sections(id)')
        
        transaction.commit()
    except:
        transaction.rollback()
        raise
    finally:
        connection.close() 
