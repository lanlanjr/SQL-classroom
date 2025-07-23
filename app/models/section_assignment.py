from app import db
from datetime import datetime

class SectionAssignment(db.Model):
    __tablename__ = 'section_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Make sure each assignment is only assigned once to each section
    __table_args__ = (
        db.UniqueConstraint('section_id', 'assignment_id', name='unique_section_assignment'),
    )
    
    def __repr__(self):
        return f'<SectionAssignment section_id={self.section_id} assignment_id={self.assignment_id}>' 