from app import db
from datetime import datetime

class SchemaImport(db.Model):
    __tablename__ = 'schema_imports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    schema_content = db.Column(db.Text, nullable=False)  # The actual SQL schema content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_template = db.Column(db.Boolean, default=False)  # Whether this is a template schema
    active_schema_name = db.Column(db.String(100), nullable=True)  # The name of the schema where this is currently deployed
    
    def __repr__(self):
        return f"SchemaImport('{self.name}', created_at: {self.created_at})" 