from app import db
from datetime import datetime
import secrets

class Section(db.Model):
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    invitation_token = db.Column(db.String(64), unique=True, nullable=True)
    
    # Relationships
    enrollments = db.relationship('StudentEnrollment', 
                                 backref=db.backref('section', lazy=True),
                                 lazy='dynamic',
                                 cascade='all, delete-orphan')
    section_assignments = db.relationship('SectionAssignment', backref='section', 
                                          lazy=True, cascade='all, delete-orphan')
    
    def generate_invitation_token(self):
        """Generate a unique invitation token for this section"""
        self.invitation_token = secrets.token_urlsafe(32)
        return self.invitation_token
    
    def get_enrolled_students(self, active_only=True):
        """Get all students enrolled in this section"""
        from app.models.user import User, StudentEnrollment
        
        # Get enrollments (filtered by active status if requested)
        query = self.enrollments
        if active_only:
            query = query.filter_by(is_active=True)
            
        # Get student IDs from enrollments
        student_ids = [enrollment.student_id for enrollment in query.all()]
        
        # Return students
        return User.query.filter(User.id.in_(student_ids)).all() if student_ids else []
    
    @classmethod
    def find_by_token(cls, token):
        """Find a section by its invitation token"""
        if not token:
            print(f"Empty token provided")
            return None
            
        # Get all sections to check for token match
        sections = cls.query.all()
        for section in sections:
            print(f"Comparing: '{token}' with '{section.invitation_token}'")
            if section.invitation_token and section.invitation_token == token:
                print(f"Found matching section: {section.name}")
                return section
                
        print(f"No section found with token: {token}")
        return cls.query.filter_by(invitation_token=token).first()
    
    def __repr__(self):
        return f'<Section {self.name}>' 