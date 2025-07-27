import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(*args, **kwargs):
    """
    Application factory function that accepts optional arguments.
    PythonAnywhere's WSGI server might pass arguments that we can safely ignore.
    """
    app = Flask(__name__)
    
    # Get database name from environment variable
    app_db_name = os.environ.get('APP_DB_NAME', 'sql_classroom')
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', f'mysql+pymysql://root:admin@localhost:3306/{app_db_name}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Add after_request handler to prevent caching of authenticated pages
    @app.after_request
    def add_cache_headers(response):
        if current_user.is_authenticated:
            # Tell browsers not to cache authenticated pages
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    
    # Import and register blueprints
    from app.routes.auth import auth
    from app.routes.main import main
    from app.routes.teacher import teacher
    from app.routes.student import student
    from app.routes.admin import admin
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(teacher)
    app.register_blueprint(student)
    app.register_blueprint(admin)
    
    # Add context processor for section teachers
    @app.context_processor
    def section_teachers():
        from flask_login import current_user
        from app.models.user import User
        
        if current_user.is_authenticated and current_user.is_student():
            # Get active sections
            active_sections = current_user.get_active_sections()
            
            # Get teachers for each section
            section_teachers = {}
            for section in active_sections:
                teacher = User.query.get(section.creator_id)
                if teacher:
                    section_teachers[section.id] = teacher
            
            return {'section_teachers': section_teachers}
        return {'section_teachers': {}}
    
    # Add context processor for current year
    @app.context_processor
    def inject_year():
        return {'current_year': datetime.now().year}
    
    return app 