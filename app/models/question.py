from app import db
from datetime import datetime

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # 'multiple_choice', 'free_response', 'fill_in_blank'
    difficulty = db.Column(db.Integer, nullable=False)  # 1-5 scale
    correct_answer = db.Column(db.Text, nullable=False)  # SQL query or answer
    sample_db_schema = db.Column(db.Text, nullable=True)  # SQL schema to load (optional if using existing DB)
    db_type = db.Column(db.String(20), default='sqlite', nullable=False)  # 'sqlite', 'mysql', or 'imported_schema'
    mysql_db_name = db.Column(db.String(100), nullable=True)  # Name of MySQL database if using existing DB
    schema_import_id = db.Column(db.Integer, db.ForeignKey('schema_imports.id'), nullable=True)  # Reference to imported schema
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disable_copy_paste = db.Column(db.Boolean, default=False, nullable=False)  # Control copy-paste functionality
    
    # Relationships
    submissions = db.relationship('Submission', backref='question', lazy=True)
    assignment_questions = db.relationship('AssignmentQuestion', backref='question', lazy=True)
    schema_import = db.relationship('SchemaImport', backref='questions', lazy=True)
    
    def __repr__(self):
        return f"Question('{self.title}', '{self.question_type}', difficulty: {self.difficulty})"
        
    def uses_mysql(self):
        return self.db_type in ('mysql', 'imported_schema')
        
    def get_schema_name(self):
        """Get the actual schema/database name to use for this question"""
        if self.db_type == 'imported_schema' and self.schema_import:
            return 'sql_classroom'  # Always use the sql_classroom database
        return self.mysql_db_name

    def get_table_prefix(self):
        """Get the table prefix for imported schemas"""
        if self.db_type == 'imported_schema' and self.schema_import:
            prefix = self.schema_import.active_schema_name
            print(f"[DEBUG] Question {self.id} - Schema Import ID: {self.schema_import_id}, Active Schema Name: {prefix}")
            return prefix
        print(f"[DEBUG] Question {self.id} - Not imported schema or no schema import (db_type: {self.db_type}, schema_import: {self.schema_import})")
        return '' 