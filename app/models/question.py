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
    db_type = db.Column(db.String(20), default='sqlite', nullable=False)  # 'sqlite' or 'mysql'
    mysql_db_name = db.Column(db.String(100), nullable=True)  # Name of MySQL database if using existing DB
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disable_copy_paste = db.Column(db.Boolean, default=False, nullable=False)  # Control copy-paste functionality
    
    # Relationships
    submissions = db.relationship('Submission', backref='question', lazy=True)
    assignment_questions = db.relationship('AssignmentQuestion', backref='question', lazy=True)
    
    def __repr__(self):
        return f"Question('{self.title}', '{self.question_type}', difficulty: {self.difficulty})"
        
    def uses_mysql(self):
        return self.db_type == 'mysql' 