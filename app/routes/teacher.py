from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file, after_this_request
from flask_login import current_user, login_required
from app import db
from app.models import User, Question, Assignment, AssignmentQuestion, Submission, Section, SectionAssignment, StudentEnrollment
from datetime import datetime
import json
import os
from openpyxl.utils import get_column_letter
import bleach
from bleach.css_sanitizer import CSSSanitizer
import pymysql

# Configure allowed HTML tags and attributes for rich text editor
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'strike', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'pre', 'code', 'div', 'span', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'a', 'img', 'sub', 'sup', 'b', 'i'
]

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style', 'data-*'],  # Allow style on all elements
    'a': ['href', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height', 'data-src'],
    'td': ['colspan', 'rowspan', 'align'],
    'th': ['colspan', 'rowspan', 'align'],
    'div': ['align'],
    'p': ['align'],
    'span': ['data-*'],
    'li': ['class', 'data-list'],
    'ul': ['class'],
    'ol': ['class']
}

# Define allowed CSS styles
ALLOWED_STYLES = [
    'color', 'background-color', 'font-size', 'text-align', 'margin', 'padding',
    'font-weight', 'font-style', 'text-decoration', 'width', 'height', 'display',
    'float', 'text-indent', 'font-family', 'line-height', 'list-style-type',
    # Add specific color values
    '#000000', '#e60000', '#ff9900', '#ffff00', '#008a00', '#0066cc', '#9933ff', '#ffffff',
    '#facccc', '#ffebcc', '#ffffcc', '#cce8cc', '#cce0f5', '#ebd6ff', '#bbbbbb',
    '#f06666', '#ffc266', '#ffff66', '#66b966', '#66a3e0', '#c285ff', '#888888',
    '#a10000', '#b26b00', '#b2b200', '#006100', '#0047b2', '#6b24b2', '#444444',
    '#5c0000', '#663d00', '#666600', '#003700', '#002966', '#3d1466'
]

def sanitize_html(html_content):
    """Sanitize HTML content to prevent XSS attacks"""
    if not html_content:
        return ""
    
    # Create CSS sanitizer with allowed styles
    css_sanitizer = CSSSanitizer(allowed_css_properties=ALLOWED_STYLES)
    
    # Clean the HTML with only allowed tags, attributes, and styles
    clean_html = bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        css_sanitizer=css_sanitizer,
        strip=True
    )
    return clean_html

teacher = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher.before_request
def check_teacher():
    if not current_user.is_authenticated or not current_user.is_teacher():
        flash('Access denied. You must be a teacher to view this page.', 'danger')
        return redirect(url_for('main.index'))

@teacher.route('/dashboard')
@login_required
def dashboard():
    assignments = Assignment.query.filter_by(creator_id=current_user.id).all()
    questions = Question.query.filter_by(author_id=current_user.id).all()
    return render_template('teacher/dashboard.html', assignments=assignments, questions=questions)

@teacher.route('/questions')
@login_required
def questions():
    questions = Question.query.filter_by(author_id=current_user.id).all()
    return render_template('teacher/questions.html', questions=questions)

@teacher.route('/question/new', methods=['GET', 'POST'])
@login_required
def new_question():
    if request.method == 'POST':
        # Debug: Print form data to console
        print("Form data received:")
        for key, value in request.form.items():
            print(f"{key}: {value}")
        
        try:
            title = request.form.get('title')
            description = sanitize_html(request.form.get('description'))
            question_type = request.form.get('question_type')
            difficulty = request.form.get('difficulty')
            correct_answer = request.form.get('correct_answer')
            db_type = request.form.get('db_type')
            
            # Validation
            if not title or not description or not question_type or not difficulty or not correct_answer or not db_type:
                flash('Please fill in all required fields.', 'danger')
                return redirect(url_for('teacher.new_question'))
            
            # Different handling based on database type
            if db_type == 'mysql':
                mysql_db_name = request.form.get('mysql_db_name')
                if not mysql_db_name:
                    flash('MySQL database name is required when using MySQL.', 'danger')
                    return redirect(url_for('teacher.new_question'))
                    
                sample_db_schema = None
                
                # Validate MySQL database connection
                try:
                    print(f"Attempting to connect to MySQL: {mysql_db_name}")
                    
                    # Try to connect to the database
                    connection = pymysql.connect(
                        host=os.environ.get('MYSQL_HOST', 'localhost'),
                        user=os.environ.get('MYSQL_USER', 'root'),
                        password=os.environ.get('MYSQL_PASSWORD', 'admin'),
                        port=int(os.environ.get('MYSQL_PORT', 3306)),
                        database=mysql_db_name
                    )
                    print("MySQL connection successful")
                    connection.close()
                except Exception as e:
                    print(f"MySQL connection error: {str(e)}")
                    flash(f'Could not connect to MySQL database: {str(e)}', 'danger')
                    return redirect(url_for('teacher.new_question'))
            else:
                mysql_db_name = None
                sample_db_schema = request.form.get('sample_db_schema')
                
                # Validate SQLite schema
                if not sample_db_schema:
                    flash('SQLite database schema is required when using the in-memory database option.', 'danger')
                    return redirect(url_for('teacher.new_question'))
            
            # Create the question object
            question = Question(
                title=title,
                description=description,
                question_type=question_type,
                difficulty=int(difficulty),  # Ensure this is an integer
                correct_answer=correct_answer,
                sample_db_schema=sample_db_schema,
                db_type=db_type,
                mysql_db_name=mysql_db_name,
                author_id=current_user.id,
                disable_copy_paste=bool(request.form.get('disable_copy_paste'))
            )
            
            # Add and commit to the database
            print("Adding question to database")
            db.session.add(question)
            db.session.commit()
            print(f"Question created with ID: {question.id}")
            
            flash('Question created successfully!', 'success')
            return redirect(url_for('teacher.questions'))
        except Exception as e:
            db.session.rollback()
            print(f"Error creating question: {str(e)}")
            flash(f'Error creating question: {str(e)}', 'danger')
            return redirect(url_for('teacher.new_question'))
    
    return render_template('teacher/new_question.html')

@teacher.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    if question.author_id != current_user.id:
        flash('You can only edit your own questions.', 'danger')
        return redirect(url_for('teacher.questions'))
    
    if request.method == 'POST':
        try:
            # Print form data for debugging
            print("Edit question form data received:")
            for key, value in request.form.items():
                print(f"{key}: {value}")
        
            question.title = request.form.get('title')
            question.description = sanitize_html(request.form.get('description'))
            question.question_type = request.form.get('question_type')
            question.difficulty = int(request.form.get('difficulty'))
            question.correct_answer = request.form.get('correct_answer')
            question.disable_copy_paste = bool(request.form.get('disable_copy_paste'))
            
            # Handle database type changes
            db_type = request.form.get('db_type')
            question.db_type = db_type
            
            if db_type == 'mysql':
                mysql_db_name = request.form.get('mysql_db_name')
                
                if not mysql_db_name:
                    flash('MySQL database name is required when using MySQL.', 'danger')
                    return redirect(url_for('teacher.edit_question', question_id=question.id))
                
                # Validate MySQL database connection
                try:
                    print(f"Attempting to connect to MySQL: {mysql_db_name}")
                    
                    # Try to connect to the database
                    connection = pymysql.connect(
                        host=os.environ.get('MYSQL_HOST', 'localhost'),
                        user=os.environ.get('MYSQL_USER', 'root'),
                        password=os.environ.get('MYSQL_PASSWORD', 'admin'),
                        port=int(os.environ.get('MYSQL_PORT', 3306)),
                        database=mysql_db_name
                    )
                    print("MySQL connection successful")
                    connection.close()
                    
                    question.mysql_db_name = mysql_db_name
                    question.sample_db_schema = None
                except Exception as e:
                    print(f"MySQL connection error: {str(e)}")
                    flash(f'Could not connect to MySQL database: {str(e)}', 'danger')
                    return redirect(url_for('teacher.edit_question', question_id=question.id))
            else:
                sample_db_schema = request.form.get('sample_db_schema')
                
                # Validate SQLite schema
                if not sample_db_schema:
                    flash('SQLite database schema is required when using the in-memory database option.', 'danger')
                    return redirect(url_for('teacher.edit_question', question_id=question.id))
                
                question.sample_db_schema = sample_db_schema
                question.mysql_db_name = None
            
            print("Saving question changes to database")
            db.session.commit()
            print(f"Question {question.id} updated successfully")
            
            flash('Question updated successfully!', 'success')
            return redirect(url_for('teacher.questions'))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating question: {str(e)}")
            flash(f'Error updating question: {str(e)}', 'danger')
            return redirect(url_for('teacher.edit_question', question_id=question.id))
    
    return render_template('teacher/edit_question.html', question=question)

@teacher.route('/assignments')
@login_required
def assignments():
    assignments = Assignment.query.filter_by(creator_id=current_user.id).all()
    return render_template('teacher/assignments.html', assignments=assignments)

@teacher.route('/assignment/new', methods=['GET', 'POST'])
@login_required
def new_assignment():
    if request.method == 'POST':
        title = request.form.get('title')
        description = sanitize_html(request.form.get('description'))
        due_date_str = request.form.get('due_date')
        due_time_str = request.form.get('due_time')
        
        # Combine date and time if both are provided
        due_date = None
        if due_date_str:
            if due_time_str:
                # Combine date and time
                due_datetime_str = f"{due_date_str} {due_time_str}"
                due_date = datetime.strptime(due_datetime_str, '%Y-%m-%d %H:%M')
            else:
                # Just date, set time to end of day (23:59:59)
                due_datetime_str = f"{due_date_str} 23:59:59"
                due_date = datetime.strptime(due_datetime_str, '%Y-%m-%d %H:%M:%S')
        
        assignment = Assignment(
            title=title,
            description=description,
            due_date=due_date,
            creator_id=current_user.id
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        # Process questions and scores
        question_ids = request.form.getlist('question_ids')
        question_scores = request.form.getlist('question_scores')
        
        # Default to 10 points if no score is provided
        if not question_scores or len(question_scores) != len(question_ids):
            question_scores = [10] * len(question_ids)
        
        for order, (question_id, score) in enumerate(zip(question_ids, question_scores), 1):
            # Ensure score is an integer and at least 1
            try:
                score_value = int(score)
                if score_value < 1:
                    score_value = 1
            except (ValueError, TypeError):
                score_value = 10  # Default if conversion fails
            
            assignment_question = AssignmentQuestion(
                assignment_id=assignment.id,
                question_id=int(question_id),
                order=order,
                score=score_value
            )
            db.session.add(assignment_question)
        
        db.session.commit()
        
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('teacher.assignments'))
    
    questions = Question.query.filter_by(author_id=current_user.id).all()
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('teacher/new_assignment.html', questions=questions, today_date=today_date)

@teacher.route('/assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    if assignment.creator_id != current_user.id:
        flash('You can only view your own assignments.', 'danger')
        return redirect(url_for('teacher.assignments'))
    
    # Get all questions for this assignment ordered by their order field
    assignment_questions = AssignmentQuestion.query.filter_by(assignment_id=assignment.id).order_by(AssignmentQuestion.order).all()
    questions = [aq.question for aq in assignment_questions]
    
    # Create a mapping of question_id to assignment_question for easy access to scores
    question_scores = {aq.question_id: aq.score for aq in assignment_questions}
    
    # Get all submissions for this assignment
    submissions = Submission.query.filter_by(assignment_id=assignment.id).all()
    
    # Group submissions by student
    submissions_by_student = {}
    for submission in submissions:
        student_id = submission.student_id
        if student_id not in submissions_by_student:
            submissions_by_student[student_id] = []
        submissions_by_student[student_id].append(submission)
    
    # Get student information
    students = {}
    student_scores = {}
    max_score = sum(aq.score for aq in assignment_questions)
    
    for student_id in submissions_by_student:
        student = User.query.get(student_id)
        if student:
            students[student_id] = student
            
            # Calculate student's score for this assignment
            student_score = 0
            student_subs = submissions_by_student[student_id]
            
            # Debug output
            print(f"Calculating score for student {student_id} ({student.username}):")
            
            # For each correct submission, add the points for that question
            for submission in student_subs:
                if submission.is_correct and submission.question_id in question_scores:
                    question_score = question_scores[submission.question_id]
                    student_score += question_score
                    print(f"  Question {submission.question_id}: is_correct={submission.is_correct}, score={question_score}")
                else:
                    print(f"  Question {submission.question_id}: is_correct={submission.is_correct}, score=0")
            
            student_scores[student_id] = student_score
            print(f"  Total score: {student_score}/{max_score}")
    
    return render_template(
        'teacher/view_assignment.html',
        assignment=assignment,
        questions=questions,
        assignment_questions=assignment_questions,
        submissions_by_student=submissions_by_student,
        students=students,
        student_scores=student_scores,
        max_score=max_score
    )

@teacher.route('/assignment/<int:assignment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    if assignment.creator_id != current_user.id:
        flash('You can only edit your own assignments.', 'danger')
        return redirect(url_for('teacher.assignments'))
    
    if request.method == 'POST':
        assignment.title = request.form.get('title')
        assignment.description = sanitize_html(request.form.get('description'))
        due_date_str = request.form.get('due_date')
        due_time_str = request.form.get('due_time')
        
        # Combine date and time if both are provided
        if due_date_str:
            if due_time_str:
                # Combine date and time
                due_datetime_str = f"{due_date_str} {due_time_str}"
                assignment.due_date = datetime.strptime(due_datetime_str, '%Y-%m-%d %H:%M')
            else:
                # Just date, set time to end of day (23:59:59)
                due_datetime_str = f"{due_date_str} 23:59:59"
                assignment.due_date = datetime.strptime(due_datetime_str, '%Y-%m-%d %H:%M:%S')
        else:
            assignment.due_date = None
        
        # Delete existing assignment questions
        AssignmentQuestion.query.filter_by(assignment_id=assignment.id).delete()
        
        # Add new assignment questions with scores
        question_ids = request.form.getlist('question_ids')
        question_scores = request.form.getlist('question_scores')
        
        # Default to 10 points if no score is provided
        if not question_scores or len(question_scores) != len(question_ids):
            question_scores = [10] * len(question_ids)
        
        for order, (question_id, score) in enumerate(zip(question_ids, question_scores), 1):
            # Ensure score is an integer and at least 1
            try:
                score_value = int(score)
                if score_value < 1:
                    score_value = 1
            except (ValueError, TypeError):
                score_value = 10  # Default if conversion fails
            
            assignment_question = AssignmentQuestion(
                assignment_id=assignment.id,
                question_id=int(question_id),
                order=order,
                score=score_value
            )
            db.session.add(assignment_question)
        
        db.session.commit()
        
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('teacher.assignments'))
    
    # Get current questions in the assignment with their scores
    current_questions = AssignmentQuestion.query.filter_by(assignment_id=assignment.id).order_by(AssignmentQuestion.order).all()
    current_question_ids = [aq.question_id for aq in current_questions]
    current_question_scores = [aq.score for aq in current_questions]
    
    all_questions = Question.query.filter_by(author_id=current_user.id).all()
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('teacher/edit_assignment.html', 
                          assignment=assignment, 
                          questions=all_questions, 
                          current_question_ids=current_question_ids,
                          current_question_scores=current_question_scores,
                          today_date=today_date)

@teacher.route('/question/simple/new', methods=['GET'])
@login_required
def simple_new_question():
    """A simplified question creation form for testing"""
    return render_template('teacher/simple_new_question.html')

@teacher.route('/questions/delete/<int:question_id>')
@login_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    # Check ownership
    if question.author_id != current_user.id:
        flash('You can only delete your own questions.', 'danger')
        return redirect(url_for('teacher.questions'))
    
    try:
        # Check if this question is used in any assignments
        assignment_questions = AssignmentQuestion.query.filter_by(question_id=question.id).all()
        if assignment_questions:
            # Get the assignment titles
            assignment_titles = []
            for aq in assignment_questions:
                assignment = Assignment.query.get(aq.assignment_id)
                if assignment:
                    assignment_titles.append(assignment.title)
            
            flash(f'This question cannot be deleted because it is used in the following assignments: {", ".join(assignment_titles)}', 'danger')
            return redirect(url_for('teacher.questions'))
        
        # Check if there are any submissions for this question
        submissions = Submission.query.filter_by(question_id=question.id).count()
        if submissions > 0:
            flash(f'This question cannot be deleted because it has {submissions} student submissions.', 'danger')
            return redirect(url_for('teacher.questions'))
        
        # Store the title for the success message
        title = question.title
        
        # Delete the question
        db.session.delete(question)
        db.session.commit()
        
        flash(f'Question "{title}" has been successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while deleting the question: {str(e)}', 'danger')
    
    return redirect(url_for('teacher.questions'))

@teacher.route('/students')
@login_required
def students():
    # Get only students enrolled in sections created by this teacher
    teacher_sections = Section.query.filter_by(creator_id=current_user.id).all()
    teacher_section_ids = [section.id for section in teacher_sections]
    
    # Find students from enrollments in these sections
    students_query = db.session.query(User).join(
        StudentEnrollment,
        (StudentEnrollment.student_id == User.id) & (StudentEnrollment.is_active == True)
    ).filter(
        User.role == 'student',
        StudentEnrollment.section_id.in_(teacher_section_ids) if teacher_section_ids else False
    ).group_by(User.id)
    
    students = students_query.all()
    
    # Get assignment stats for each student
    stats = {}
    
    for student in students:
        # Get the sections this student is enrolled in
        student_enrollments = StudentEnrollment.query.filter_by(
            student_id=student.id,
            is_active=True
        ).filter(StudentEnrollment.section_id.in_(teacher_section_ids)).all()
        
        student_section_ids = [enrollment.section_id for enrollment in student_enrollments]
        
        # Get assignments assigned to the student's sections
        section_assignments = SectionAssignment.query.filter(
            SectionAssignment.section_id.in_(student_section_ids)
        ).all()
        
        assignment_ids = [sa.assignment_id for sa in section_assignments]
        
        # Get all submissions for this student on their assigned assignments
        submissions = Submission.query.filter_by(student_id=student.id).filter(
            Submission.assignment_id.in_(assignment_ids)
        ).all() if assignment_ids else []
        
        # Get unique assignments that this student has submitted to
        submitted_assignment_ids = set(s.assignment_id for s in submissions)
        
        # Count correct submissions
        correct_submissions = [s for s in submissions if s.is_correct]
        
        stats[student.id] = {
            'total_assignments': len(assignment_ids),
            'started_assignments': len(submitted_assignment_ids),
            'total_submissions': len(submissions),
            'correct_submissions': len(correct_submissions)
        }
    
    return render_template('teacher/students.html', students=students, stats=stats)

@teacher.route('/student/<int:student_id>')
@login_required
def view_student(student_id):
    # Get the student
    student = User.query.filter_by(id=student_id, role='student').first_or_404()
    
    # Get the student's enrollments
    student_enrollments = StudentEnrollment.query.filter_by(
        student_id=student.id,
        is_active=True
    ).all()
    student_section_ids = [enrollment.section_id for enrollment in student_enrollments]
    
    # Get sections created by this teacher
    teacher_sections = Section.query.filter_by(creator_id=current_user.id).all()
    teacher_section_ids = [section.id for section in teacher_sections]
    
    # Check if the student is in any of the teacher's sections
    is_in_teacher_section = any(section_id in teacher_section_ids for section_id in student_section_ids)
    
    if not is_in_teacher_section:
        flash('You can only view students enrolled in your sections.', 'danger')
        return redirect(url_for('teacher.students'))
    
    # Get current time for checking due dates
    now = datetime.now()
    
    # Get assignments that are assigned to sections where this student is enrolled
    section_assignments = SectionAssignment.query.filter(
        SectionAssignment.section_id.in_(student_section_ids)
    ).all()
    
    # Get the assignment IDs from section assignments
    assignment_ids = [sa.assignment_id for sa in section_assignments]
    
    # Get all assignments created by this teacher that are assigned to the student's sections
    teacher_assignments = Assignment.query.filter(
        Assignment.creator_id == current_user.id,
        Assignment.id.in_(assignment_ids)
    ).all()
    
    # Get all submissions by this student for this teacher's assignments
    student_submissions = {}
    
    for assignment in teacher_assignments:
        # Get all questions for this assignment
        assignment_questions = AssignmentQuestion.query.filter_by(assignment_id=assignment.id).all()
        question_ids = [aq.question_id for aq in assignment_questions]
        
        # Create a map of question_id to assignment_question for score lookup
        question_to_aq = {aq.question_id: aq for aq in assignment_questions}
        
        # Skip if no questions
        if not question_ids:
            continue
        
        # Get submissions for these questions
        submissions = Submission.query.filter_by(
            student_id=student.id,
            assignment_id=assignment.id
        ).all()
        
        # Keep only submissions for questions that are still part of the assignment
        valid_submissions = [s for s in submissions if s.question_id in question_ids]
        
        # For each question, keep only the most recent submission
        latest_submissions_by_question = {}
        for submission in valid_submissions:
            question_id = submission.question_id
            if question_id not in latest_submissions_by_question or submission.submitted_at > latest_submissions_by_question[question_id].submitted_at:
                latest_submissions_by_question[question_id] = submission
        
        # Add score information to each submission
        for submission in valid_submissions:
            if submission.question_id in question_to_aq:
                aq = question_to_aq[submission.question_id]
                submission.question_score = aq.score
                submission.earned_score = aq.score if submission.is_correct else 0
            else:
                submission.question_score = 0
                submission.earned_score = 0
        
        # Get unique submitted question IDs based on latest submissions
        submitted_question_ids = set(latest_submissions_by_question.keys())
        
        # Calculate if assignment is completed - a student must have submitted to all questions
        is_completed = len(submitted_question_ids) == len(question_ids)
        
        # Count correct submissions in the latest submissions
        correct_count = sum(1 for s in latest_submissions_by_question.values() if s.is_correct)
        
        # Calculate total possible score for this assignment
        total_possible_score = sum(aq.score for aq in assignment_questions)
        
        # Calculate earned score based on latest correct submissions
        earned_score = 0
        for qid, submission in latest_submissions_by_question.items():
            if submission.is_correct and qid in question_to_aq:
                earned_score += question_to_aq[qid].score
        
        # Calculate progress
        if len(question_ids) > 0:
            progress = len(submitted_question_ids) / len(question_ids) * 100
        else:
            progress = 0
        
        student_submissions[assignment.id] = {
            'assignment': assignment,
            'submissions': valid_submissions,
            'question_count': len(question_ids),
            'submitted_count': len(submitted_question_ids),
            'correct_count': correct_count,
            'progress': progress,
            'total_possible_score': total_possible_score,
            'earned_score': earned_score,
            'is_completed': is_completed
        }
    
    return render_template(
        'teacher/view_student.html',
        student=student,
        student_submissions=student_submissions,
        now=now
    )

@teacher.route('/sections')
@login_required
def sections():
    # Get all sections created by this teacher
    sections = Section.query.filter_by(creator_id=current_user.id).all()
    
    # Get stats for each section
    section_stats = {}
    
    for section in sections:
        # Count students enrolled in the section using the StudentEnrollment relationship
        student_count = db.session.query(StudentEnrollment).filter_by(section_id=section.id, is_active=True).count()
        
        # Count assignments for the section
        assignment_count = SectionAssignment.query.filter_by(section_id=section.id).count()
        
        section_stats[section.id] = {
            'student_count': student_count,
            'assignment_count': assignment_count
        }
    
    return render_template('teacher/sections.html', sections=sections, section_stats=section_stats)

@teacher.route('/section/new', methods=['GET', 'POST'])
@login_required
def new_section():
    if request.method == 'POST':
        name = request.form.get('name')
        description = sanitize_html(request.form.get('description'))
        
        if not name:
            flash('Section name is required.', 'danger')
            return redirect(url_for('teacher.new_section'))
        
        # Create new section
        section = Section(
            name=name,
            description=description,
            creator_id=current_user.id
        )
        
        db.session.add(section)
        db.session.commit()
        
        flash('Section created successfully!', 'success')
        return redirect(url_for('teacher.sections'))
    
    return render_template('teacher/new_section.html')

@teacher.route('/section/<int:section_id>')
@login_required
def view_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    # Make sure the teacher owns this section
    if section.creator_id != current_user.id:
        flash('You can only view your own sections.', 'danger')
        return redirect(url_for('teacher.sections'))
    
    # Get all students in this section
    students = section.get_enrolled_students(active_only=True)
    
    # Get all assignments for this section
    section_assignments = SectionAssignment.query.filter_by(section_id=section.id).all()
    assignments = [sa.assignment for sa in section_assignments]
    
    # Get submission stats for each student
    student_stats = {}
    
    for student in students:
        assignment_ids = [sa.assignment_id for sa in section_assignments]
        
        # Skip if no assignments
        if not assignment_ids:
            student_stats[student.id] = {
                'total_submissions': 0,
                'correct_submissions': 0,
                'completed_assignments': 0
            }
            continue
        
        # Get all submissions for this student for section assignments
        submissions = Submission.query.filter_by(student_id=student.id).filter(
            Submission.assignment_id.in_(assignment_ids)
        ).all()
        
        # Get unique assignment IDs with submissions
        submitted_assignment_ids = set(s.assignment_id for s in submissions)
        
        # Count completed assignments
        completed_assignments = 0
        for assignment_id in assignment_ids:
            # Get all questions for this assignment
            assignment_questions = AssignmentQuestion.query.filter_by(assignment_id=assignment_id).all()
            question_ids = [aq.question_id for aq in assignment_questions]
            
            # Skip if no questions
            if not question_ids:
                continue
            
            # Get all submissions for this assignment
            assignment_submissions = [s for s in submissions if s.assignment_id == assignment_id]
            
            # For each question, keep only the most recent submission
            latest_submissions_by_question = {}
            for submission in assignment_submissions:
                question_id = submission.question_id
                if question_id not in latest_submissions_by_question or submission.submitted_at > latest_submissions_by_question[question_id].submitted_at:
                    latest_submissions_by_question[question_id] = submission
            
            # Get unique question IDs based on latest submissions
            submitted_question_ids = set(latest_submissions_by_question.keys())
            
            # If all questions have submissions, count as completed
            if len(submitted_question_ids) == len(question_ids):
                completed_assignments += 1
        
        # Count correct submissions
        correct_submissions = len([s for s in submissions if s.is_correct])
        
        student_stats[student.id] = {
            'total_submissions': len(submissions),
            'correct_submissions': correct_submissions,
            'completed_assignments': completed_assignments
        }
    
    return render_template('teacher/view_section.html', 
                           section=section, 
                           students=students, 
                           assignments=assignments,
                           student_stats=student_stats)

@teacher.route('/section/<int:section_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    if section.creator_id != current_user.id:
        flash('You can only edit sections you created.', 'danger')
        return redirect(url_for('teacher.sections'))
    
    if request.method == 'POST':
        section.name = request.form.get('name')
        section.description = sanitize_html(request.form.get('description'))
        
        db.session.commit()
        
        flash('Section updated successfully!', 'success')
        return redirect(url_for('teacher.view_section', section_id=section.id))
    
    return render_template('teacher/edit_section.html', section=section)

@teacher.route('/section/<int:section_id>/students', methods=['GET', 'POST'])
@login_required
def manage_section_students(section_id):
    section = Section.query.get_or_404(section_id)
    
    # Make sure the teacher owns this section
    if section.creator_id != current_user.id:
        flash('You can only manage your own sections.', 'danger')
        return redirect(url_for('teacher.sections'))
    
    if request.method == 'POST':
        # Get selected student IDs
        student_ids = request.form.getlist('student_ids')
        
        # Verify that these students are either not in any section or in one of this teacher's sections
        if student_ids:
            teacher_sections = Section.query.filter_by(creator_id=current_user.id).all()
            teacher_section_ids = [s.id for s in teacher_sections]
            
            # Query to check if any selected student is in a section not owned by this teacher
            invalid_students_query = db.session.query(User).join(
                StudentEnrollment, StudentEnrollment.student_id == User.id
            ).filter(
                User.id.in_(student_ids),
                StudentEnrollment.section_id.notin_(teacher_section_ids),
                StudentEnrollment.is_active == True
            )
            
            invalid_students = invalid_students_query.all()
            
            if invalid_students:
                invalid_names = [s.username for s in invalid_students]
                flash(f'Cannot add students that belong to other teachers\' sections: {", ".join(invalid_names)}', 'danger')
                return redirect(url_for('teacher.manage_section_students', section_id=section.id))
        
        # First, deactivate all existing enrollments for this section
        StudentEnrollment.query.filter_by(section_id=section.id).update({StudentEnrollment.is_active: False})
        
        # Add or reactivate enrollments for selected students
        if student_ids:
            for student_id in student_ids:
                # Check if enrollment already exists
                enrollment = StudentEnrollment.query.filter_by(
                    student_id=student_id,
                    section_id=section.id
                ).first()
                
                if enrollment:
                    # Reactivate existing enrollment
                    enrollment.is_active = True
                else:
                    # Create new enrollment
                    new_enrollment = StudentEnrollment(
                        student_id=student_id,
                        section_id=section.id,
                        is_active=True
                    )
                    db.session.add(new_enrollment)
        
        db.session.commit()
        
        flash('Students updated successfully!', 'success')
        return redirect(url_for('teacher.view_section', section_id=section.id))
    
    # Get current students in the section
    current_students = section.get_enrolled_students(active_only=True)
    current_student_ids = [s.id for s in current_students]
    
    # Get all sections created by this teacher
    teacher_sections = Section.query.filter_by(creator_id=current_user.id).all()
    teacher_section_ids = [s.id for s in teacher_sections]
    
    # Get all available students - using a simpler approach to avoid auto-correlation issues
    # Get all student users
    all_students = User.query.filter_by(role='student').all()
    
    # Get students with enrollments in sections not owned by this teacher
    students_in_other_sections_query = db.session.query(User.id).join(
        StudentEnrollment, 
        StudentEnrollment.student_id == User.id
    ).filter(
        StudentEnrollment.section_id.notin_(teacher_section_ids) if teacher_section_ids else True,
        StudentEnrollment.is_active == True
    ).distinct()
    
    students_in_other_sections = [r[0] for r in students_in_other_sections_query.all()]
    
    # Filter out students that are in other teachers' sections
    available_students = [s for s in all_students if s.id not in students_in_other_sections]
    
    # Get all students that are in other teachers' sections - simpler approach
    assigned_elsewhere_students = [s for s in all_students if s.id in students_in_other_sections]
    
    return render_template('teacher/manage_section_students.html', 
                           section=section, 
                           all_students=available_students,
                           assigned_elsewhere_students=assigned_elsewhere_students,
                           current_student_ids=current_student_ids)

@teacher.route('/section/<int:section_id>/assignments', methods=['GET', 'POST'])
@login_required
def manage_section_assignments(section_id):
    section = Section.query.get_or_404(section_id)
    
    # Make sure the teacher owns this section
    if section.creator_id != current_user.id:
        flash('You can only manage your own sections.', 'danger')
        return redirect(url_for('teacher.sections'))
    
    if request.method == 'POST':
        # Get selected assignment IDs
        assignment_ids = request.form.getlist('assignment_ids')
        
        # First, delete existing section assignments
        SectionAssignment.query.filter_by(section_id=section.id).delete()
        
        # Add new section assignments
        for assignment_id in assignment_ids:
            section_assignment = SectionAssignment(
                section_id=section.id,
                assignment_id=int(assignment_id)
            )
            db.session.add(section_assignment)
        
        db.session.commit()
        
        flash('Assignments updated successfully!', 'success')
        return redirect(url_for('teacher.view_section', section_id=section.id))
    
    # Get current assignments for this section
    current_assignments = SectionAssignment.query.filter_by(section_id=section.id).all()
    current_assignment_ids = [sa.assignment_id for sa in current_assignments]
    
    # Get all assignments created by this teacher
    all_assignments = Assignment.query.filter_by(creator_id=current_user.id).all()
    
    return render_template('teacher/manage_section_assignments.html',
                          section=section,
                          all_assignments=all_assignments,
                          current_assignment_ids=current_assignment_ids)

@teacher.route('/section/<int:section_id>/invitation', methods=['GET', 'POST'])
@login_required
def section_invitation(section_id):
    section = Section.query.get_or_404(section_id)
    
    # Make sure the teacher owns this section
    if section.creator_id != current_user.id:
        flash('You can only manage your own sections.', 'danger')
        return redirect(url_for('teacher.sections'))
    
    if request.method == 'POST':
        # Generate new invitation token
        token = section.generate_invitation_token()
        db.session.commit()
        flash('New invitation link generated successfully!', 'success')
    
    # Generate invitation URL if token exists
    invitation_url = None
    if section.invitation_token:
        invitation_url = url_for('auth.register_with_token', 
                                token=section.invitation_token, 
                                _external=True)
    
    return render_template('teacher/section_invitation.html', 
                          section=section, 
                          invitation_url=invitation_url)

@teacher.route('/section/<int:section_id>/invitation/revoke', methods=['POST'])
@login_required
def revoke_invitation(section_id):
    section = Section.query.get_or_404(section_id)
    
    # Make sure the teacher owns this section
    if section.creator_id != current_user.id:
        flash('You can only manage your own sections.', 'danger')
        return redirect(url_for('teacher.sections'))
    
    # Revoke the token
    section.invitation_token = None
    db.session.commit()
    
    flash('Invitation link has been revoked.', 'success')
    return redirect(url_for('teacher.section_invitation', section_id=section.id))

@teacher.route('/section/<int:section_id>/export_results')
@login_required
def export_section_results(section_id):
    """Export section results as Excel file with student scores for all assignments."""
    section = Section.query.get_or_404(section_id)
    
    # Make sure the teacher owns this section
    if section.creator_id != current_user.id:
        flash('You can only export results from your own sections.', 'danger')
        return redirect(url_for('teacher.sections'))
    
    # Get all students in this section
    students = section.get_enrolled_students(active_only=True)
    
    # Get all assignments for this section
    section_assignments = SectionAssignment.query.filter_by(section_id=section.id).all()
    assignments = [sa.assignment for sa in section_assignments]
    
    # Sort assignments by ID or creation date
    assignments.sort(key=lambda a: a.id)
    
    # Create Excel workbook
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill
    from openpyxl.utils.cell import get_column_letter
    from flask import send_file
    import tempfile
    import os
    
    # Create a workbook with proper properties
    wb = Workbook()
    
    # Set workbook properties
    wb.properties.creator = "SQL Classroom"
    wb.properties.title = f"Section {section.name} Results"
    wb.properties.description = f"Student results for section {section.name}"
    
    # Remove default sheet and create a new one with valid name
    if "Sheet" in wb.sheetnames:
        std = wb["Sheet"]
        wb.remove(std)
    
    # Create worksheet with properly escaped name (limit to 31 chars, no special chars)
    sheet_name = ''.join(c for c in section.name if c.isalnum() or c in ' _-')[:31]
    if not sheet_name:
        sheet_name = "Results"
    ws = wb.create_sheet(title=sheet_name)
    
    # Create header row
    headers = ["No.", "Last Name", "First Name", "Section"]
    
    # For each assignment, add both detailed score and raw score columns
    for assignment in assignments:
        # Limit title length to avoid Excel issues and remove invalid chars
        title = ''.join(c for c in assignment.title if c not in '"*:<>?/\\|')
        if len(title) > 100:
            title = title[:100] + "..."
            
        # headers.append(f"Assignment {assignment.id}: {title}")
        # headers.append(f"Raw Score {assignment.id}")
        headers.append(f"{title}")
        headers.append("Raw Score")

    headers.append("Total Score")
    headers.append("Raw Total")
    
    # Apply header styling
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
        cell.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
    
    # Add data rows
    for idx, student in enumerate(students, 1):
        row_num = idx + 1
        student_total_score = 0
        student_total_possible = 0
        
        # Basic student info - ensure values are strings
        ws.cell(row=row_num, column=1, value=idx)
        ws.cell(row=row_num, column=2, value=str(student.last_name or ""))
        ws.cell(row=row_num, column=3, value=str(student.first_name or ""))
        ws.cell(row=row_num, column=4, value=str(section.name))
        
        # For each assignment, calculate and add the score
        col_idx = 5
        for assignment in assignments:
            # Find all questions in the assignment
            assignment_questions = AssignmentQuestion.query.filter_by(assignment_id=assignment.id).all()
            question_ids = [aq.question_id for aq in assignment_questions]
            
            # Create score mapping for each question
            question_scores = {aq.question_id: aq.score for aq in assignment_questions}
            
            # Get all submissions for this student and assignment
            submissions = Submission.query.filter_by(
                student_id=student.id,
                assignment_id=assignment.id
            ).all()
            
            # Get the most recent submission for each question
            latest_submissions = {}
            for submission in submissions:
                question_id = submission.question_id
                if question_id not in latest_submissions or submission.submitted_at > latest_submissions[question_id].submitted_at:
                    latest_submissions[question_id] = submission
            
            # Calculate earned points
            earned_points = 0
            for question_id in question_ids:
                if question_id in latest_submissions and latest_submissions[question_id].is_correct:
                    earned_points += question_scores.get(question_id, 0)
            
            # Calculate total possible points for this assignment
            assignment_total_possible = sum(question_scores.values())
            
            # Update student totals
            student_total_score += earned_points
            student_total_possible += assignment_total_possible
            
            # Add the detailed score to the spreadsheet
            if assignment_total_possible > 0:
                percentage = round((earned_points / assignment_total_possible) * 100)
                score_display = f"{earned_points}/{assignment_total_possible} ({percentage}%)"
            else:
                score_display = "N/A"
            
            # Add the score display
            ws.cell(row=row_num, column=col_idx, value=score_display)
            
            # Add the raw score - ensure it's numeric
            ws.cell(row=row_num, column=col_idx + 1, value=float(earned_points))
            
            # Move to next set of columns
            col_idx += 2
        
        # Add total score
        if student_total_possible > 0:
            percentage = round((student_total_score / student_total_possible) * 100)
            ws.cell(row=row_num, column=col_idx, value=f"{student_total_score}/{student_total_possible} ({percentage}%)")
            ws.cell(row=row_num, column=col_idx + 1, value=float(student_total_score))
        else:
            ws.cell(row=row_num, column=col_idx, value="N/A")
            ws.cell(row=row_num, column=col_idx + 1, value=0)
    
    # Adjust column widths
    for col_idx, header in enumerate(headers, 1):
        column_letter = get_column_letter(col_idx)
        if col_idx == 1:  # Number column
            ws.column_dimensions[column_letter].width = 5
        elif col_idx in (2, 3):  # Name columns
            ws.column_dimensions[column_letter].width = 15
        elif col_idx == 4:  # Section column
            ws.column_dimensions[column_letter].width = 20
        elif "Raw Score" in header or header == "Raw Total":  # Raw score columns
            ws.column_dimensions[column_letter].width = 12
        else:  # Assignment and total columns
            ws.column_dimensions[column_letter].width = 25
    
    # Save to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    temp_file.close()
    
    try:
        # Set proper workbook protection options
        wb.security.lockStructure = False
        
        # Save with explicit options
        wb.save(temp_file.name)
        
        # Send the file
        filename = f"{sheet_name}_results.xlsx"
        return_data = send_file(
            temp_file.name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename
        )
        
        # Schedule file for deletion after request
        @after_this_request
        def remove_file(response):
            try:
                os.unlink(temp_file.name)
            except Exception as e:
                print(f"Error removing temporary file: {e}")
            return response
        
        return return_data
        
    except Exception as e:
        print(f"Error generating Excel file: {e}")
        # Clean up temp file in case of error
        try:
            os.unlink(temp_file.name)
        except:
            pass
        flash(f'Error generating Excel file. Please try again.', 'danger')
        return redirect(url_for('teacher.view_section', section_id=section.id))

@teacher.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    """Handle image uploads from the Quill editor"""
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'})
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'})
        
        # Check if it's a valid image
        if file and file.content_type.startswith('image/'):
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate a unique filename
            import uuid
            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)
            
            # Save the file
            file.save(file_path)
            
            # Return the URL to the image
            image_url = url_for('static', filename=f'uploads/{filename}')
            return jsonify({'success': True, 'url': image_url})
        else:
            return jsonify({'success': False, 'error': 'Invalid file type, must be an image'})
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}) 

@teacher.route('/assignment/delete/<int:assignment_id>', methods=['GET'])
@login_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Make sure the teacher owns this assignment
    if assignment.creator_id != current_user.id:
        flash('You can only delete your own assignments.', 'danger')
        return redirect(url_for('teacher.assignments'))
    
    # Delete all section assignments first (due to foreign key constraints)
    SectionAssignment.query.filter_by(assignment_id=assignment.id).delete()
    
    # Delete all assignment questions
    AssignmentQuestion.query.filter_by(assignment_id=assignment.id).delete()
    
    # Delete all submissions for this assignment
    Submission.query.filter_by(assignment_id=assignment.id).delete()
    
    # Finally delete the assignment
    db.session.delete(assignment)
    db.session.commit()
    
    flash('Assignment deleted successfully!', 'success')
    return redirect(url_for('teacher.assignments'))

@teacher.route('/import_schema', methods=['GET', 'POST'])
@login_required
def import_schema():
    if request.method == 'POST':
        try:
            # Get the schema file
            if 'schema_file' not in request.files:
                flash('No file uploaded', 'danger')
                return redirect(url_for('teacher.import_schema'))
            
            schema_file = request.files['schema_file']
            if schema_file.filename == '':
                flash('No file selected', 'danger')
                return redirect(url_for('teacher.import_schema'))
            
            # Get database name from form
            db_name = request.form.get('database_name')
            if not db_name:
                flash('Database name is required', 'danger')
                return redirect(url_for('teacher.import_schema'))
            
            # Validate database name to prevent SQL injection
            if not db_name.isalnum() and not '_' in db_name:
                flash('Database name can only contain letters, numbers, and underscores', 'danger')
                return redirect(url_for('teacher.import_schema'))
            
            # Read schema content
            try:
                schema_content = schema_file.read().decode('utf-8')
            except UnicodeDecodeError:
                flash('Invalid file encoding. Please ensure the file is saved with UTF-8 encoding.', 'danger')
                return redirect(url_for('teacher.import_schema'))
            
            # Split schema into individual statements and validate
            statements = [stmt.strip() for stmt in schema_content.split(';') if stmt.strip()]
            if not statements:
                flash('No valid SQL statements found in the file', 'danger')
                return redirect(url_for('teacher.import_schema'))
            
            # Try to establish connection with increased timeout
            try:
                connection = pymysql.connect(
                    host=os.environ.get('MYSQL_HOST', 'localhost'),
                    user=os.environ.get('MYSQL_USER', 'root'),
                    password=os.environ.get('MYSQL_PASSWORD', 'admin'),
                    port=int(os.environ.get('MYSQL_PORT', 3306)),
                    connect_timeout=30,
                    read_timeout=30,
                    write_timeout=30
                )
            except pymysql.Error as e:
                flash(f'Could not connect to MySQL server: {str(e)}', 'danger')
                return redirect(url_for('teacher.import_schema'))
            
            try:
                with connection.cursor() as cursor:
                    # Drop database if it exists and create new one
                    cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                    cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    cursor.execute(f"USE {db_name}")
                    
                    # Set session variables for better compatibility
                    cursor.execute("SET SESSION sql_mode = ''")
                    cursor.execute("SET foreign_key_checks = 0")
                    cursor.execute("SET unique_checks = 0")
                    cursor.execute("SET autocommit = 0")
                    
                    # First pass: Create tables without foreign keys
                    create_table_statements = []
                    other_statements = []
                    
                    for statement in statements:
                        if statement.strip().upper().startswith('CREATE TABLE'):
                            create_table_statements.append(statement)
                        else:
                            other_statements.append(statement)
                    
                    # Execute CREATE TABLE statements first
                    for statement in create_table_statements:
                        try:
                            cursor.execute(statement)
                        except pymysql.Error as e:
                            if "already exists" not in str(e).lower():
                                print(f"Error creating table: {str(e)}")
                                # Continue with other statements
                    
                    # Commit table creation
                    connection.commit()
                    
                    # Second pass: Add foreign keys and other constraints
                    for statement in other_statements:
                        try:
                            if statement.strip():
                                cursor.execute(statement)
                        except pymysql.Error as e:
                            print(f"Error executing statement: {str(e)}")
                            # Continue with other statements
                    
                    # Reset session variables
                    cursor.execute("SET foreign_key_checks = 1")
                    cursor.execute("SET unique_checks = 1")
                    cursor.execute("SET autocommit = 1")
                    
                    # Create or update student user with proper permissions
                    try:
                        cursor.execute("DROP USER IF EXISTS 'sql_student'@'localhost'")
                        cursor.execute("CREATE USER 'sql_student'@'localhost' IDENTIFIED BY 'student_password'")
                    except pymysql.Error:
                        cursor.execute("ALTER USER 'sql_student'@'localhost' IDENTIFIED BY 'student_password'")
                    
                    # Grant SELECT permissions on the new database
                    cursor.execute(f"GRANT SELECT ON {db_name}.* TO 'sql_student'@'localhost'")
                    
                    # Grant SELECT permissions on all existing databases used in questions
                    try:
                        # Get all unique MySQL database names from questions
                        cursor.execute("SELECT DISTINCT mysql_db_name FROM question WHERE db_type = 'mysql' AND mysql_db_name IS NOT NULL")
                        existing_dbs = [row[0] for row in cursor.fetchall()]
                        
                        # Grant permissions for each database
                        for db in existing_dbs:
                            try:
                                cursor.execute(f"GRANT SELECT ON {db}.* TO 'sql_student'@'localhost'")
                            except pymysql.Error as e:
                                print(f"Warning: Could not grant permissions for database {db}: {str(e)}")
                    except pymysql.Error as e:
                        print(f"Warning: Could not retrieve existing databases: {str(e)}")
                    
                    cursor.execute("FLUSH PRIVILEGES")
                    
                flash(f'Schema imported successfully to database "{db_name}"', 'success')
                
            except Exception as e:
                connection.rollback()
                flash(f'Error importing schema: {str(e)}', 'danger')
            finally:
                try:
                    cursor.execute("SET foreign_key_checks = 1")
                    cursor.execute("SET unique_checks = 1")
                    cursor.execute("SET autocommit = 1")
                except:
                    pass
                connection.close()
            
            return redirect(url_for('teacher.import_schema'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('teacher.import_schema'))
    
    return render_template('teacher/import_schema.html') 