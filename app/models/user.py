from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class StudentEnrollment(db.Model):
    __tablename__ = 'student_enrollments'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'section_id', name='unique_student_section'),
        {'mysql_auto_increment': 100000}
    )
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"StudentEnrollment(student_id={self.student_id}, section_id={self.section_id})"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'mysql_auto_increment': 100000}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'teacher', or 'admin'
    first_name = db.Column(db.String(50), nullable=False, default='User')
    last_name = db.Column(db.String(50), nullable=False, default='Account')
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # User account status
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='author', lazy=True)
    assignments = db.relationship('Assignment', backref='creator', lazy=True)
    sections = db.relationship('Section', backref='creator', lazy=True)
    submissions = db.relationship('Submission', backref='student', lazy=True)
    # New relationship for student enrollments
    enrollments = db.relationship('StudentEnrollment', 
                                 foreign_keys=[StudentEnrollment.student_id],
                                 backref=db.backref('student', lazy=True),
                                 lazy='dynamic')
    
    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_authenticated(self):
        """Override Flask-Login's is_authenticated to check if user is active"""
        return self.is_active
    
    def get_active_enrollments(self):
        """Get all active section enrollments for this student"""
        if self.is_student():
            return self.enrollments.filter_by(is_active=True).all()
        return []
    
    def get_active_sections(self):
        """Get all sections the student is actively enrolled in"""
        from app.models.section import Section
        enrollments = self.get_active_enrollments()
        section_ids = [enrollment.section_id for enrollment in enrollments]
        return Section.query.filter(Section.id.in_(section_ids)).all() if section_ids else []
    
    def get_section_teachers(self):
        """Get all teachers whose sections this student is enrolled in"""
        sections = self.get_active_sections()
        teacher_ids = [section.creator_id for section in sections]
        return User.query.filter(User.id.in_(teacher_ids)).all() if teacher_ids else []

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 
