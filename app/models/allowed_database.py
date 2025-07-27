from app import db
from datetime import datetime

class AllowedDatabase(db.Model):
    __tablename__ = 'allowed_databases'
    
    id = db.Column(db.Integer, primary_key=True)
    database_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref='allowed_databases', lazy=True)
    
    def __repr__(self):
        return f"AllowedDatabase('{self.database_name}', active: {self.is_active})"
    
    @staticmethod
    def get_active_databases():
        """Get all active allowed databases"""
        return AllowedDatabase.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_active_database_names():
        """Get list of active allowed database names"""
        return [db.database_name for db in AllowedDatabase.get_active_databases()]
    
    @staticmethod
    def is_database_allowed(database_name):
        """Check if a database is in the allowed list and active"""
        return AllowedDatabase.query.filter_by(
            database_name=database_name, 
            is_active=True
        ).first() is not None
