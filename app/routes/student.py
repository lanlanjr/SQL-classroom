from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app import db, csrf
from app.models import User, Question, Assignment, AssignmentQuestion, Submission, Section, SectionAssignment, StudentEnrollment
from sqlalchemy import text, create_engine
from datetime import datetime
import sqlite3
import pymysql
import pandas as pd
import json
import uuid
import os
from flask import session

student = Blueprint('student', __name__, url_prefix='/student')

# Dictionary to store student sessions (in-memory databases)
student_sessions = {}

@student.before_request
def check_student():
    if not current_user.is_authenticated or not current_user.is_student():
        flash('Access denied. You must be a student to view this page.', 'danger')
        return redirect(url_for('main.index'))

@student.route('/dashboard')
@login_required
def dashboard():
    # Get active sections for this student
    active_sections = current_user.get_active_sections()
    
    # Check if student is enrolled in any sections
    if not active_sections:
        flash('You are not enrolled in any classrooms yet. Please contact your teacher or use an enrollment link to join a classroom.', 'warning')
        return render_template('student/dashboard.html', 
                              assignments=[], 
                              assignment_stats={},
                              completed_assignments=0,
                              now=datetime.now(),
                              section=None,
                              active_sections=[],
                              teacher=None)
    
    # Get current section - either from session or default to first one
    current_section_id = session.get('current_section_id')
    current_section = None
    
    # Check if the student is still enrolled in the current section
    if current_section_id:
        # First, verify the student is still enrolled in this section
        enrollment = StudentEnrollment.query.filter_by(
            student_id=current_user.id,
            section_id=current_section_id,
            is_active=True
        ).first()
        
        if not enrollment:
            # Student was removed from this section, clear from session
            session.pop('current_section_id', None)
            current_section_id = None
    
    # If specified section ID exists and student is enrolled in it, use that
    if current_section_id:
        for section in active_sections:
            if section.id == current_section_id:
                current_section = section
                break
    
    # If no valid section found in session, use the first one
    if not current_section and active_sections:
        current_section = active_sections[0]
        session['current_section_id'] = current_section.id
    
    # Get the teacher for the current section
    teacher = User.query.get(current_section.creator_id) if current_section else None
    
    # Get all assignments for this student's current section that are active
    section_assignments = SectionAssignment.query.filter_by(section_id=current_section.id, is_active=True).all()
    assignment_ids = [sa.assignment_id for sa in section_assignments]
    
    # Make sure assignments have questions
    valid_assignment_ids = db.session.query(AssignmentQuestion.assignment_id)\
        .filter(AssignmentQuestion.assignment_id.in_(assignment_ids))\
        .distinct()
    
    # Get the assignments
    assignments = Assignment.query.filter(Assignment.id.in_(valid_assignment_ids)).all()
    
    print(f"Total assignments found for section {current_section.id}: {len(assignments)}")
    
    # Get submission stats for each assignment
    assignment_stats = {}
    completed_assignments = 0
    
    for assignment in assignments:
        # Find all questions in the assignment
        assignment_questions = AssignmentQuestion.query.filter_by(assignment_id=assignment.id).all()
        question_count = len(assignment_questions)
        question_ids = [aq.question_id for aq in assignment_questions]
        
        # Find all submissions by this student for this assignment
        submissions = Submission.query.filter_by(
            student_id=current_user.id, 
            assignment_id=assignment.id
        ).all()
        
        # Only count submissions for questions that are still part of the assignment
        valid_submissions = [s for s in submissions if s.question_id in question_ids]
        
        # For each question, keep only the most recent submission
        latest_submissions_by_question = {}
        for submission in valid_submissions:
            question_id = submission.question_id
            if question_id not in latest_submissions_by_question or submission.submitted_at > latest_submissions_by_question[question_id].submitted_at:
                latest_submissions_by_question[question_id] = submission
        
        # Get unique questions that have been submitted with the latest submission
        submitted_question_ids = set(latest_submissions_by_question.keys())
        
        # Count correct submissions
        correct_count = sum(1 for s in latest_submissions_by_question.values() if s.is_correct)
        
        # Store the stats
        assignment_stats[assignment.id] = {
            'question_count': question_count,
            'submitted_count': len(submitted_question_ids),
            'correct_count': correct_count
        }
        
        # Check if this assignment is completed - all questions must have submissions
        if question_count > 0 and len(submitted_question_ids) == question_count:
            completed_assignments += 1
            print(f"Assignment {assignment.id} '{assignment.title}' is COMPLETED")
        else:
            print(f"Assignment {assignment.id} '{assignment.title}' is NOT completed:")
            print(f"  Question count: {question_count}")
            print(f"  Unique submitted questions: {len(submitted_question_ids)}")
            print(f"  Question IDs: {question_ids}")
            print(f"  Submitted Question IDs: {submitted_question_ids}")
    
    print(f"Total completed assignments: {completed_assignments}")
    
    # Get current time for checking due dates
    now = datetime.now()
    
    return render_template('student/dashboard.html', 
                           assignments=assignments, 
                           assignment_stats=assignment_stats,
                           completed_assignments=completed_assignments,
                           now=now,
                           section=current_section,
                           active_sections=active_sections,
                           teacher=teacher)

@student.route('/assignment/<int:assignment_id>')
@login_required
def view_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Get current section from session or active sections
    current_section_id = session.get('current_section_id')
    active_sections = current_user.get_active_sections()
    
    if not active_sections:
        flash('You are not enrolled in any classroom yet. Please contact your teacher.', 'warning')
        return redirect(url_for('student.dashboard'))
    
    # If no current section or not valid, use first active section
    current_section = None
    if current_section_id:
        # First, verify the student is still enrolled in this section
        enrollment = StudentEnrollment.query.filter_by(
            student_id=current_user.id,
            section_id=current_section_id,
            is_active=True
        ).first()
        
        if not enrollment:
            # Student was removed from this section, redirect to dashboard
            flash('You are no longer enrolled in the section you were viewing.', 'warning')
            session.pop('current_section_id', None)
            return redirect(url_for('student.dashboard'))
            
        current_section = next((s for s in active_sections if s.id == current_section_id), None)
    
    if not current_section:
        current_section = active_sections[0]
        session['current_section_id'] = current_section.id
    
    # Check if this assignment is assigned to the student's current section and is active
    section_assignment = SectionAssignment.query.filter_by(
        section_id=current_section.id,
        assignment_id=assignment.id
    ).first()
    
    if not section_assignment:
        flash('This assignment is not available for your current classroom.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Check if the assignment is active
    if not section_assignment.is_active:
        flash('This assignment has been disabled by your teacher.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Get current time for checking due dates
    now = datetime.now()
    
    # Check if the assignment is past due
    is_past_due = assignment.due_date and assignment.due_date < now
    
    # If assignment is past due, redirect to dashboard with message
    if is_past_due:
        flash('This assignment has passed its due date. You can no longer view or submit solutions.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Get all questions for this assignment ordered by their order field
    assignment_questions = AssignmentQuestion.query.filter_by(assignment_id=assignment.id).order_by(AssignmentQuestion.order).all()
    questions = [aq.question for aq in assignment_questions]
    question_ids = [aq.question_id for aq in assignment_questions]
    
    # Debug: Print assignment questions and scores
    print(f"Assignment {assignment.id} '{assignment.title}' questions:")
    for aq in assignment_questions:
        print(f"  Question ID: {aq.question_id}, Score: {aq.score}")
    
    # Create a mapping of question_id to assignment_question for easy access to scores
    question_assignment_map = {aq.question_id: aq for aq in assignment_questions}
    
    # Get all submissions for this assignment by this student
    submissions = Submission.query.filter_by(
        assignment_id=assignment.id, 
        student_id=current_user.id
    ).all()
    
    # Debug: Print all submissions found
    print(f"Found {len(submissions)} submissions for student {current_user.id} on assignment {assignment.id}:")
    for sub in submissions:
        print(f"  Submission ID: {sub.id}, Question ID: {sub.question_id}, is_correct: {sub.is_correct}")
    
    # Only keep submissions for questions that are still part of the assignment
    valid_submissions = [s for s in submissions if s.question_id in question_ids]
    
    # For each question, keep only the most recent submission
    submissions_by_question = {}
    for submission in valid_submissions:
        question_id = submission.question_id
        if question_id not in submissions_by_question or submission.submitted_at > submissions_by_question[question_id].submitted_at:
            submissions_by_question[question_id] = submission
    
    # Debug: Print submissions_by_question
    print(f"Final submissions_by_question for calculating points:")
    for q_id, sub in submissions_by_question.items():
        print(f"  Question ID: {q_id}, is_correct: {sub.is_correct}, score in map: {question_assignment_map[q_id].score if q_id in question_assignment_map else 'N/A'}")
    
    # Calculate earned points for debugging
    debug_earned_points = 0
    for aq in assignment_questions:
        if aq.question_id in submissions_by_question and submissions_by_question[aq.question_id].is_correct:
            debug_earned_points += aq.score
            print(f"  Adding {aq.score} points for correct question {aq.question_id}")
    
    print(f"Total debug earned points: {debug_earned_points} out of {sum(aq.score for aq in assignment_questions)} possible")
    
    # Pre-calculate earned points to pass to template
    earned_points = 0
    for aq in assignment_questions:
        if aq.question_id in submissions_by_question and submissions_by_question[aq.question_id].is_correct:
            earned_points += aq.score
    
    return render_template(
        'student/view_assignment.html',
        assignment=assignment,
        questions=questions,
        assignment_questions=assignment_questions,
        question_assignment_map=question_assignment_map,
        submissions_by_question=submissions_by_question,
        now=now,
        section=current_section,
        active_sections=active_sections,
        earned_points=earned_points  # Add pre-calculated earned points
    )

@student.route('/question/<int:question_id>')
@login_required
def view_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    # Get the assignment_id from query parameters
    assignment_id = request.args.get('assignment_id')
    if not assignment_id:
        flash('Missing assignment information.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    assignment_id = int(assignment_id)
    
    # Get the assignment to check due date
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Get current section from session or active sections
    current_section_id = session.get('current_section_id')
    active_sections = current_user.get_active_sections()
    
    if not active_sections:
        flash('You are not enrolled in any classroom yet. Please contact your teacher.', 'warning')
        return redirect(url_for('student.dashboard'))
    
    # If no current section or not valid, use first active section
    current_section = None
    if current_section_id:
        # First, verify the student is still enrolled in this section
        enrollment = StudentEnrollment.query.filter_by(
            student_id=current_user.id,
            section_id=current_section_id,
            is_active=True
        ).first()
        
        if not enrollment:
            # Student was removed from this section, redirect to dashboard
            flash('You are no longer enrolled in the section you were viewing.', 'warning')
            session.pop('current_section_id', None)
            return redirect(url_for('student.dashboard'))
            
        current_section = next((s for s in active_sections if s.id == current_section_id), None)
    
    if not current_section:
        current_section = active_sections[0]
        session['current_section_id'] = current_section.id
    
    # Check if this assignment is assigned to the student's section
    section_assignment = SectionAssignment.query.filter_by(
        section_id=current_section.id,
        assignment_id=assignment.id
    ).first()
    
    if not section_assignment:
        flash('This assignment is not available for your current classroom.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Check if the assignment is past due
    now = datetime.now()
    is_past_due = assignment.due_date and assignment.due_date < now
    
    # If assignment is past due, redirect to dashboard with message
    if is_past_due:
        flash('This assignment has passed its due date. You can no longer view or submit solutions.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Get the question from the assignment to ensure it belongs to the assignment
    assignment_question = AssignmentQuestion.query.filter_by(
        assignment_id=assignment_id,
        question_id=question_id
    ).first_or_404()
    
    # Get the most recent submission for this question, if any
    submission = Submission.query.filter_by(
        student_id=current_user.id,
        assignment_id=assignment_id,
        question_id=question_id
    ).order_by(Submission.submitted_at.desc()).first()
    
    return render_template(
        'student/view_question.html',
        question=question,
        assignment=assignment,
        assignment_id=assignment_id,
        submission=submission,
        section=current_section,
        active_sections=active_sections,
        is_past_due=is_past_due,
        now=now,
        assignment_question=assignment_question
    )

def get_student_db_connection(question):
    """Create a restricted database connection for student query execution"""
    if not question:
        raise ValueError("Invalid question")
        
    if question.db_type == 'imported_schema':
        if not question.schema_import or not question.schema_import.active_schema_name:
            raise ValueError("Question's imported schema is not properly configured")
            
        # Connect to the sql_classroom database using root user
        conn = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', 'admin'),
            port=int(os.environ.get('MYSQL_PORT', 3306)),
            database='sql_classroom',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        return conn
        
    elif question.db_type == 'mysql':
        if not question.mysql_db_name:
            raise ValueError("Invalid question or missing database name")
            
        try:
            # Get database prefixes from environment
            assignments_prefix = os.environ.get('ASSIGNMENTS_DB_PREFIX', 'student_assignment_')
            template_prefix = os.environ.get('TEMPLATE_DB_PREFIX', 'template_assignment_')
            
            # Connect using root user
            conn = pymysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', 'admin'),
                port=int(os.environ.get('MYSQL_PORT', 3306)),
                cursorclass=pymysql.cursors.DictCursor
            )
            
            with conn.cursor() as cursor:
                # Check if database exists
                cursor.execute("SHOW DATABASES")
                databases = [row['Database'] for row in cursor.fetchall()]
                
                # Check both with and without prefixes
                possible_names = [
                    question.mysql_db_name,
                    f"{assignments_prefix}{question.mysql_db_name}",
                    f"{template_prefix}{question.mysql_db_name}"
                ]
                
                db_name = None
                for name in possible_names:
                    if name in databases:
                        db_name = name
                        break
                        
                if not db_name:
                    raise ValueError(f"Database '{question.mysql_db_name}' (or its prefixed versions) does not exist")
                
                # Use the found database
                cursor.execute(f"USE {db_name}")
            
            return conn
            
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            if "Access denied" in str(e):
                raise ValueError(f"Access denied to database. Please contact your teacher.")
            raise
    else:
        raise ValueError(f"Unsupported database type: {question.db_type}")

def validate_student_query(query):
    """Validate student query for potential harmful operations - DEPRECATED
    
    This function is deprecated. Use validate_dql_only_query from app.utils instead.
    """
    from app.utils import validate_dql_only_query
    return validate_dql_only_query(query)

@student.route('/api/execute-query', methods=['POST'])
@login_required
@csrf.exempt
def execute_query():
    data = request.json
    if not data or 'query' not in data or 'question_id' not in data or 'assignment_id' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    query = data['query'].strip()
    question_id = data['question_id']
    assignment_id = data['assignment_id']
    
    # Get the question
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    # Get the assignment to check due date
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Check if assignment is past due
    now = datetime.now()
    is_past_due = assignment.due_date and assignment.due_date < now
    
    # If assignment is past due, return error
    if is_past_due:
        return jsonify({'error': 'This assignment has passed its due date. You can no longer execute queries or submit solutions.'}), 403
    
    # For imported schemas, modify the query to use prefixed table names
    if question.db_type == 'imported_schema':
        table_prefix = question.get_table_prefix()
        if table_prefix:
            # Get all table names from the schema content
            schema_content = question.schema_import.schema_content
            table_names = []
            for line in schema_content.split('\n'):
                if 'CREATE TABLE' in line.upper():
                    # Extract table name
                    table_name = line[line.find('TABLE') + 5:].strip().split()[0].strip('`')
                    table_names.append(table_name)
            
            # Replace table names with prefixed versions in the query
            modified_query = query
            for table_name in table_names:
                modified_query = modified_query.replace(table_name, f"{table_prefix}{table_name}")
            query = modified_query
    
    try:
        # Handle different database types
        if question.uses_mysql():  # This covers both 'mysql' and 'imported_schema'
            try:
                # Validate the query first
                validate_student_query(query)
                
                print(f"Executing MySQL query: {query}")
                
                # Get restricted connection
                conn = get_student_db_connection(question)
                
                # Execute query and fetch results
                with conn.cursor() as cursor:
                    # Execute the query
                    cursor.execute(query)
                    
                    # Check if this is a SELECT query by looking for a result set
                    if cursor.description:
                        # For SELECT queries, get the results
                        data = cursor.fetchall()
                        
                        # Get column names directly from cursor description
                        columns = [col[0] for col in cursor.description]
                        
                        # Convert dictionary data to lists for JSON response
                        rows = []
                        for row in data:
                            # Convert any non-JSON serializable objects to strings
                            serializable_row = {}
                            for key, value in row.items():
                                if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                                    serializable_row[key] = value
                                else:
                                    serializable_row[key] = str(value)
                            
                            # Ensure values are in the same order as columns
                            row_values = [serializable_row.get(col) for col in columns]
                            rows.append(row_values)
                        
                        result = {
                            'columns': columns,
                            'data': rows
                        }
                    else:
                        # This shouldn't happen due to validation, but just in case
                        return jsonify({'error': 'Only SELECT queries are allowed'}), 400
                
                conn.close()
                return jsonify(result)
                
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except pymysql.err.ProgrammingError as e:
                error_code, error_message = e.args
                clean_message = error_message.replace('\n', ' ')
                return jsonify({'error': f'SQL Error: {clean_message}'}), 400
            except Exception as e:
                print(f"MySQL query error: {str(e)}")
                return jsonify({'error': str(e)}), 400
            
        elif question.db_type == 'sqlite':
            # SQLite - Create a fresh in-memory database for each query execution
            try:
                print(f"Creating fresh SQLite in-memory database for query execution")
                # Create SQLAlchemy in-memory engine with thread safety settings
                engine = create_engine('sqlite:///:memory:', 
                                       connect_args={'check_same_thread': False})
                
                # Create a new connection and load the schema
                with engine.connect() as conn:
                    # Load schema
                    print(f"Loading schema: {question.sample_db_schema[:100]}...")
                    schema_statements = question.sample_db_schema.split(';')
                    trans = conn.begin()
                    try:
                        for statement in schema_statements:
                            if statement.strip():
                                try:
                                    conn.execute(text(statement))
                                except Exception as e:
                                    print(f"Error executing schema statement: {statement}\nError: {str(e)}")
                                    trans.rollback()
                                    return jsonify({'error': f'Error in schema: {str(e)}'}), 500
                        trans.commit()
                    except Exception as e:
                        trans.rollback()
                        print(f"Error in schema transaction: {str(e)}")
                        return jsonify({'error': f'Error in schema: {str(e)}'}), 500
                
                    # Execute the query in a separate transaction
                    print(f"Executing SQLite query: {query}")
                    
                    # Check if it's a PRAGMA query
                    is_pragma = query.strip().upper().startswith('PRAGMA')
                    # Check if it's a SELECT query
                    is_select = query.strip().upper().startswith('SELECT')
                    
                    try:
                        result_set = conn.execute(text(query))
                        
                        if is_pragma or is_select:
                            # For PRAGMA and SELECT queries, return the result set
                            columns = list(result_set.keys())
                            data = [list(row) for row in result_set]
                            
                            result = {
                                'columns': columns,
                                'data': data
                            }
                            print(f"Query returned {len(data)} rows with {len(columns)} columns")
                            return jsonify(result)
                        else:
                            # Execute non-SELECT query
                            trans = conn.begin()
                            try:
                                result_proxy = conn.execute(text(query))
                                rowcount = result_proxy.rowcount
                                trans.commit()
                                result = {
                                    'columns': ['Result'],
                                    'data': [[f"{rowcount} row(s) affected"]]
                                }
                                print(f"Non-SELECT query affected {rowcount} rows")
                                return jsonify(result)
                            except Exception as e:
                                trans.rollback()
                                raise e
                    except Exception as e:
                        print(f"Error executing query: {str(e)}")
                        raise e
                    
            except sqlite3.OperationalError as e:
                error_msg = str(e).replace('\n', ' ')
                print(f"SQLite operational error: {error_msg}")
                if "syntax error" in error_msg.lower():
                    return jsonify({'error': 'SQL Syntax Error: Please check your query syntax'}), 400
                elif "no such column" in error_msg.lower():
                    return jsonify({'error': 'Unknown Column: The column name you specified does not exist'}), 400
                elif "no such table" in error_msg.lower():
                    return jsonify({'error': 'Table Not Found: The table you referenced does not exist'}), 400
                else:
                    return jsonify({'error': f'SQL Error: {error_msg}'}), 400
            except Exception as e:
                error_msg = str(e).replace('\n', ' ')
                print(f"General SQLite error: {error_msg}")
                # Look for common SQLAlchemy error patterns
                if "syntax error" in error_msg.lower():
                    return jsonify({'error': 'SQL Syntax Error: Please check your query syntax'}), 400
                elif "no such column" in error_msg.lower() or "invalid column" in error_msg.lower():
                    return jsonify({'error': 'Unknown Column: The column name you specified does not exist'}), 400
                elif "no such table" in error_msg.lower() or "table not found" in error_msg.lower():
                    return jsonify({'error': 'Table Not Found: The table you referenced does not exist'}), 400
                else:
                    return jsonify({'error': f'Database error: {error_msg}'}), 400
        else:
            return jsonify({'error': f'Unsupported database type: {question.db_type}'}), 400
    except Exception as e:
        print(f"Unexpected error in execute_query: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@student.route('/api/submit-answer', methods=['POST'])
@login_required
@csrf.exempt
def submit_answer():
    data = request.json
    query = data.get('query')
    question_id = data.get('question_id')
    assignment_id = data.get('assignment_id')
    
    if not query or not question_id or not assignment_id:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get the question and assignment
    question = Question.query.get_or_404(question_id)
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Check if assignment is past due
    now = datetime.now()
    if assignment.due_date and assignment.due_date < now:
        return jsonify({'error': 'This assignment has passed its due date. You can no longer submit solutions.'}), 403
    
    try:
        # Different handling based on database type
        if question.uses_mysql():  # This covers both 'mysql' and 'imported_schema'
            try:
                # Validate the query first
                validate_student_query(query)
                
                # Get restricted connection
                conn = get_student_db_connection(question)
                
                # Execute student query
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    student_data = cursor.fetchall()
                
                # Execute teacher's correct query
                with conn.cursor() as cursor:
                    cursor.execute(question.correct_answer)
                    teacher_data = cursor.fetchall()
                
                # Convert data to JSON-serializable format
                def ensure_serializable(data_list):
                    result = []
                    for item in data_list:
                        serializable_item = {}
                        for key, value in item.items():
                            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                                serializable_item[key] = value
                            else:
                                serializable_item[key] = str(value)
                        result.append(serializable_item)
                    return result
                
                student_data = ensure_serializable(student_data)
                teacher_data = ensure_serializable(teacher_data)
                
                # Convert to DataFrames for comparison
                student_result = pd.DataFrame(student_data) if student_data else pd.DataFrame()
                teacher_result = pd.DataFrame(teacher_data) if teacher_data else pd.DataFrame()
                
                # Compare results
                is_correct = student_result.equals(teacher_result)
                
                # Generate feedback
                if is_correct:
                    feedback = "Correct! Your query produces the expected result."
                else:
                    feedback = "Incorrect. Your query does not produce the expected result."
                    if student_result.shape != teacher_result.shape:
                        feedback += f" Expected result has {teacher_result.shape[0]} rows and {teacher_result.shape[1]} columns, but your query returned {student_result.shape[0]} rows and {student_result.shape[1]} columns."
                    elif len(student_result.columns) > 0 and len(teacher_result.columns) > 0 and set(student_result.columns) != set(teacher_result.columns):
                        missing = set(teacher_result.columns) - set(student_result.columns)
                        extra = set(student_result.columns) - set(teacher_result.columns)
                        if missing:
                            feedback += f" Missing columns: {', '.join(missing)}."
                        if extra:
                            feedback += f" Extra columns: {', '.join(extra)}."
                
                conn.close()
                
                # Save submission
                try:
                    # Get existing submission if any
                    submission = Submission.query.filter_by(
                        question_id=question_id,
                        student_id=current_user.id,
                        assignment_id=assignment_id
                    ).first()
                    
                    if submission:
                        # Update existing submission
                        submission.submitted_answer = query
                        submission.is_correct = is_correct
                        submission.feedback = feedback
                        submission.submitted_at = datetime.utcnow()
                    else:
                        # Create new submission
                        submission = Submission(
                            student_id=current_user.id,
                            question_id=question_id,
                            assignment_id=assignment_id,
                            submitted_answer=query,
                            is_correct=is_correct,
                            feedback=feedback
                        )
                        db.session.add(submission)
                    
                    db.session.commit()
                    
                    # Return response with success status
                    return jsonify({
                        'success': True,
                        'is_correct': is_correct,
                        'feedback': feedback
                    })
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"Database error when saving submission: {str(e)}")
                    return jsonify({'error': f'Error saving your submission: {str(e)}'}), 500
                
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                print(f"MySQL grading error: {str(e)}")
                return jsonify({'error': str(e)}), 400
                
        elif question.db_type == 'sqlite':
            # SQLite grading using SQLAlchemy
            try:
                print(f"Grading SQLite query: student={query[:50]}..., teacher={question.correct_answer[:50]}...")
                engine = create_engine('sqlite:///:memory:', 
                                     connect_args={'check_same_thread': False})
                
                with engine.connect() as conn:
                    # Load schema with transaction handling
                    trans = conn.begin()
                    try:
                        schema_statements = question.sample_db_schema.split(';')
                        for statement in schema_statements:
                            if statement.strip():
                                try:
                                    conn.execute(text(statement))
                                except Exception as e:
                                    print(f"Error in schema: {statement}\nError: {str(e)}")
                                    trans.rollback()
                                    return jsonify({'error': f'Error in database schema: {str(e)}'}), 400
                        trans.commit()
                    except Exception as e:
                        trans.rollback()
                        print(f"Error in schema transaction: {str(e)}")
                        return jsonify({'error': f'Error in database schema: {str(e)}'}), 400
                    
                    # Execute student query
                    student_result_proxy = conn.execute(text(query))
                    student_columns = list(student_result_proxy.keys())
                    student_data = [list(row) for row in student_result_proxy]
                    
                    # Execute teacher's query
                    teacher_result_proxy = conn.execute(text(question.correct_answer))
                    teacher_columns = list(teacher_result_proxy.keys())
                    teacher_data = [list(row) for row in teacher_result_proxy]
                    
                    # Compare results
                    columns_match = student_columns == teacher_columns
                    
                    # Sort data for proper comparison regardless of order
                    sorted_student_data = sorted([tuple(row) for row in student_data])
                    sorted_teacher_data = sorted([tuple(row) for row in teacher_data])
                    data_match = sorted_student_data == sorted_teacher_data
                    
                    is_correct = columns_match and data_match
                    
                    # Generate feedback
                    if is_correct:
                        feedback = "Correct! Your query produces the expected result."
                    else:
                        feedback = "Incorrect. Your query does not produce the expected result."
                        if len(student_columns) != len(teacher_columns) or len(student_data) != len(teacher_data):
                            feedback += f" Expected result has {len(teacher_data)} rows and {len(teacher_columns)} columns, but your query returned {len(student_data)} rows and {len(student_columns)} columns."
                        elif not columns_match:
                            missing = set(teacher_columns) - set(student_columns)
                            extra = set(student_columns) - set(teacher_columns)
                            if missing:
                                feedback += f" Missing columns: {', '.join(missing)}."
                            if extra:
                                feedback += f" Extra columns: {', '.join(extra)}."
                    
                    # Save submission
                    try:
                        # Get existing submission if any
                        submission = Submission.query.filter_by(
                            question_id=question_id,
                            student_id=current_user.id,
                            assignment_id=assignment_id
                        ).first()
                        
                        if submission:
                            # Update existing submission
                            submission.submitted_answer = query
                            submission.is_correct = is_correct
                            submission.feedback = feedback
                            submission.submitted_at = datetime.utcnow()
                        else:
                            # Create new submission
                            submission = Submission(
                                student_id=current_user.id,
                                question_id=question_id,
                                assignment_id=assignment_id,
                                submitted_answer=query,
                                is_correct=is_correct,
                                feedback=feedback
                            )
                            db.session.add(submission)
                        
                        db.session.commit()
                        
                        # Return response with success status
                        return jsonify({
                            'success': True,
                            'is_correct': is_correct,
                            'feedback': feedback
                        })
                        
                    except Exception as e:
                        db.session.rollback()
                        print(f"Database error when saving submission: {str(e)}")
                        return jsonify({'error': f'Error saving your submission: {str(e)}'}), 500
                        
            except Exception as e:
                print(f"SQLite grading error: {str(e)}")
                return jsonify({'error': f'Database error: {str(e)}'}), 400
        else:
            return jsonify({'error': f'Unsupported database type: {question.db_type}'}), 400
    
    except Exception as e:
        print(f"Unexpected error in submit_answer: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@student.route('/api/check-assignment-status/<int:assignment_id>', methods=['GET'])
@login_required
def check_assignment_status(assignment_id):
    """Check if an assignment is still active for the current section."""
    # Get current section from session
    current_section_id = session.get('current_section_id')
    
    # If no section ID in session, assignment is inaccessible
    if not current_section_id:
        return jsonify({'active': False, 'message': 'No active section'})
    
    # Check if assignment exists and is active
    section_assignment = SectionAssignment.query.filter_by(
        section_id=current_section_id,
        assignment_id=assignment_id
    ).first()
    
    if not section_assignment:
        return jsonify({'active': False, 'message': 'Assignment not found for this section'})
    
    # Check if the assignment is still active
    if not section_assignment.is_active:
        return jsonify({'active': False, 'message': 'Assignment has been disabled by your teacher'})
    
    # Check if assignment is past due
    assignment = Assignment.query.get_or_404(assignment_id)
    now = datetime.now()
    if assignment.due_date and assignment.due_date < now:
        return jsonify({'active': False, 'message': 'Assignment has passed its due date'})
    
    return jsonify({'active': True})

@student.route('/api/active-assignments', methods=['GET'])
@login_required
def get_active_assignments():
    """Get all active assignments for the student's current section."""
    # Get current section from session
    current_section_id = session.get('current_section_id')
    
    # If no section ID in session, return empty list
    if not current_section_id:
        return jsonify({'assignments': [], 'stats': {}, 'message': 'No active section', 'now': datetime.now().isoformat()})
    
    try:
        # First, check if the student is still enrolled in this section
        enrollment = StudentEnrollment.query.filter_by(
            student_id=current_user.id,
            section_id=current_section_id,
            is_active=True
        ).first()
        
        if not enrollment:
            # Student has been removed from this section, clear the session
            session.pop('current_section_id', None)
            
            # Try to find another active section for this student
            active_sections = current_user.get_active_sections()
            if active_sections:
                # Set the first available active section as current
                session['current_section_id'] = active_sections[0].id
                current_section_id = active_sections[0].id
            else:
                # No active sections available
                return jsonify({'assignments': [], 'stats': {}, 'message': 'No active section', 'now': datetime.now().isoformat()})
        
        # Get all active assignments for this section
        section_assignments = SectionAssignment.query.filter_by(
            section_id=current_section_id, 
            is_active=True
        ).all()
        
        assignment_ids = [sa.assignment_id for sa in section_assignments]
        
        # Make sure assignments have questions
        valid_assignment_ids = db.session.query(AssignmentQuestion.assignment_id)\
            .filter(AssignmentQuestion.assignment_id.in_(assignment_ids))\
            .distinct() if assignment_ids else []
        
        # Get the assignments
        if not assignment_ids:
            return jsonify({'assignments': [], 'stats': {}, 'now': datetime.now().isoformat()})
            
        assignments = Assignment.query.filter(Assignment.id.in_(valid_assignment_ids)).all()
        
        # Collect all necessary data for frontend rendering
        assignment_data = []
        assignment_stats = {}
        
        for assignment in assignments:
            # Find all questions in the assignment
            assignment_questions = AssignmentQuestion.query.filter_by(assignment_id=assignment.id).all()
            question_count = len(assignment_questions)
            question_ids = [aq.question_id for aq in assignment_questions]
            
            # Find all submissions by this student for this assignment
            submissions = Submission.query.filter_by(
                student_id=current_user.id, 
                assignment_id=assignment.id
            ).all()
            
            # Only count submissions for questions that are still part of the assignment
            valid_submissions = [s for s in submissions if s.question_id in question_ids]
            
            # For each question, keep only the most recent submission
            latest_submissions_by_question = {}
            for submission in valid_submissions:
                question_id = submission.question_id
                if question_id not in latest_submissions_by_question or submission.submitted_at > latest_submissions_by_question[question_id].submitted_at:
                    latest_submissions_by_question[question_id] = submission
            
            # Get unique questions that have been submitted with the latest submission
            submitted_question_ids = set(latest_submissions_by_question.keys())
            
            # Count correct submissions
            correct_count = sum(1 for s in latest_submissions_by_question.values() if s.is_correct)
            
            # Store the stats
            stats = {
                'question_count': question_count,
                'submitted_count': len(submitted_question_ids),
                'correct_count': correct_count
            }
            
            # Add to results
            assignment_stats[assignment.id] = stats
            
            # Format assignment data
            assignment_data.append({
                'id': assignment.id,
                'title': assignment.title,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'question_count': question_count
            })
        
        return jsonify({
            'assignments': assignment_data,
            'stats': assignment_stats,
            'now': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error fetching active assignments: {str(e)}")
        return jsonify({'error': str(e)}), 500

@student.route('/switch_section/<int:section_id>')
@login_required
def switch_section(section_id):
    # Get active sections for this student
    active_sections = current_user.get_active_sections()
    active_section_ids = [section.id for section in active_sections]
    
    # Check if the requested section is valid
    if section_id not in active_section_ids:
        flash('You are not enrolled in this section or it does not exist.', 'danger')
        return redirect(url_for('student.dashboard'))
    
    # Set the current section ID in the session
    session['current_section_id'] = section_id
    
    # Get the section name for the flash message
    section = Section.query.get(section_id)
    flash(f'Switched to {section.name}', 'success')
    
    return redirect(url_for('student.dashboard')) 

@student.route('/sql-playground', methods=['GET'])
@login_required
def sql_playground():
    """Display the SQL Playground page where students can practice SQL queries."""
    # Get current section from session or active sections
    current_section_id = session.get('current_section_id')
    active_sections = current_user.get_active_sections()
    
    if not active_sections:
        flash('You are not enrolled in any classroom yet. Please contact your teacher.', 'warning')
        return redirect(url_for('student.dashboard'))
    
    # If no current section or not valid, use first active section
    current_section = None
    if current_section_id:
        # First, verify the student is still enrolled in this section
        enrollment = StudentEnrollment.query.filter_by(
            student_id=current_user.id,
            section_id=current_section_id,
            is_active=True
        ).first()
        
        if not enrollment:
            # Student was removed from this section, redirect to dashboard
            flash('You are no longer enrolled in the section you were viewing.', 'warning')
            session.pop('current_section_id', None)
            return redirect(url_for('student.dashboard'))
            
        current_section = next((s for s in active_sections if s.id == current_section_id), None)
    
    if not current_section:
        current_section = active_sections[0]
        session['current_section_id'] = current_section.id
    
    return render_template(
        'student/sql_playground.html',
        section=current_section,
        active_sections=active_sections
    )

@student.route('/api/playground-execute', methods=['POST'])
@login_required
@csrf.exempt
def playground_execute():
    """API endpoint to execute SQL queries in the playground."""
    data = request.json
    if not data or 'query' not in data or 'database_name' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    query = data['query'].strip()
    database_name = data['database_name'].strip()
    
    try:
        # Validate the query for security
        validate_student_query(query)
        
        try:
            # Connect to MySQL using the provided database name
            conn = pymysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', 'admin'),
                port=int(os.environ.get('MYSQL_PORT', 3306)),
                database=database_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            
            # Execute query and fetch results
            with conn.cursor() as cursor:
                # Execute the query
                cursor.execute(query)
                
                # Check if this is a SELECT query by looking for a result set
                if cursor.description:
                    # For SELECT queries, get the results
                    data = cursor.fetchall()
                    
                    # Get column names directly from cursor description
                    columns = [col[0] for col in cursor.description]
                    
                    # Convert dictionary data to lists for JSON response
                    rows = []
                    for row in data:
                        # Convert any non-JSON serializable objects to strings
                        serializable_row = {}
                        for key, value in row.items():
                            if isinstance(value, (dict, list, str, int, float, bool, type(None))):
                                serializable_row[key] = value
                            else:
                                serializable_row[key] = str(value)
                        
                        # Ensure values are in the same order as columns
                        row_values = [serializable_row.get(col) for col in columns]
                        rows.append(row_values)
                    
                    result = {
                        'columns': columns,
                        'data': rows
                    }
                else:
                    # This shouldn't happen due to validation, but just in case
                    return jsonify({'error': 'Only SELECT queries are allowed'}), 400
            
            conn.close()
            return jsonify(result)
            
        except pymysql.err.OperationalError as e:
            error_code, error_message = e.args
            if error_code == 1049:  # Unknown database
                return jsonify({'error': f'Database "{database_name}" does not exist'}), 404
            elif error_code == 1045:  # Access denied
                return jsonify({'error': 'Access denied. Check your database credentials.'}), 403
            clean_message = error_message.replace('\n', ' ')
            return jsonify({'error': f'Database Error: {clean_message}'}), 400
        except pymysql.err.ProgrammingError as e:
            error_code, error_message = e.args
            clean_message = error_message.replace('\n', ' ')
            return jsonify({'error': f'SQL Error: {clean_message}'}), 400
        except Exception as e:
            print(f"MySQL query error: {str(e)}")
            return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
            
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Unexpected error in playground_execute: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500 

@student.route('/api/get-available-databases', methods=['GET'])
@login_required
def get_available_databases():
    """API endpoint to get a list of available MySQL databases."""
    try:
        # Connect to MySQL using root credentials
        conn = pymysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', 'admin'),
            port=int(os.environ.get('MYSQL_PORT', 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # Execute query to get databases
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            all_databases = [db['Database'] for db in cursor.fetchall()]
            
            # Filter out system databases that students shouldn't access
            system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
            user_databases = [db for db in all_databases if db not in system_dbs]
            
            # Sort alphabetically
            user_databases.sort()
        
        conn.close()
        return jsonify({'databases': user_databases})
        
    except Exception as e:
        print(f"Error fetching databases: {str(e)}")
        return jsonify({'error': str(e), 'databases': []}), 500 