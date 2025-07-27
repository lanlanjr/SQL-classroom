from app import db
from datetime import datetime

class Assignment(db.Model):
    __tablename__ = 'assignments'
    __table_args__ = {'mysql_auto_increment': 100000}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    questions = db.relationship('AssignmentQuestion', backref='assignment', lazy=True)
    section_assignments = db.relationship('SectionAssignment', backref='assignment', 
                                          lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Assignment('{self.title}')"

class AssignmentQuestion(db.Model):
    __tablename__ = 'assignment_questions'
    __table_args__ = {'mysql_auto_increment': 100000}
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False, default=10)  # Points value for this question
    
    def __repr__(self):
        return f"AssignmentQuestion(assignment_id: {self.assignment_id}, question_id: {self.question_id})" 
