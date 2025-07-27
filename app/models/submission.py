from app import db
from datetime import datetime

class Submission(db.Model):
    __tablename__ = 'submissions'
    __table_args__ = {'mysql_auto_increment': 100000}
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    submitted_answer = db.Column(db.Text, nullable=False)  # SQL query or answer
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Submission(student_id: {self.student_id}, question_id: {self.question_id}, is_correct: {self.is_correct})" 
