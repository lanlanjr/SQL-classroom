from app import create_app, db
from app.models import User, Question, Assignment, AssignmentQuestion, Submission

app = create_app()

# Create a context to work within the Flask application
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Question': Question, 
        'Assignment': Assignment,
        'AssignmentQuestion': AssignmentQuestion, 
        'Submission': Submission
    }

if __name__ == '__main__':
    app.run() 