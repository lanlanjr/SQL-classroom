from flask import Blueprint, render_template, redirect, url_for, flash, request, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import db
from app.models import User, Section, StudentEnrollment
from flask_login import user_logged_in
from flask import current_app, jsonify
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



auth = Blueprint('auth', __name__)

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Access denied. Your account has been deactivated. Please contact an administrator.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=request.form.get('remember_me'))
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                if user.is_admin():
                    next_page = url_for('admin.dashboard')
                elif user.is_teacher():
                    next_page = url_for('teacher.dashboard')
                else:
                    next_page = url_for('student.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    # Clear the user's session
    session.clear()
    
    # Logout the user
    logout_user()
    
    login_url = url_for('auth.login')
    # Create response with JavaScript to clear history
    response = make_response(f"""
        <script>
            // Clear history and prevent back navigation
            window.history.pushState(null, '', window.location.href);
            window.onpopstate = function () {{
                window.history.pushState(null, '', window.location.href);
            }};
            // Redirect to login page
            window.location.href = '{login_url}';
        </script>
    """)
    
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Content-Type'] = 'text/html'
    
    # Add security headers
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
    
    return response

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        # Validate required fields
        if not username or not email or not first_name or not last_name or not password or not role:
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already in use', 'danger')
            return redirect(url_for('auth.register'))
        
        new_user = User(
            username=username, 
            email=email, 
            first_name=first_name, 
            last_name=last_name, 
            role=role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/register/token/', methods=['GET', 'POST'])
def register_token_missing():
    flash('Invalid invitation link. The token is missing.', 'danger')
    return redirect(url_for('auth.register'))

@auth.route('/register/token/<token>', methods=['GET', 'POST'])
def register_with_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Debug output
    logging.debug(f"Token received: '{token}'")

    # Find section by token
    section = Section.find_by_token(token)
    if not section:
        flash('Invalid or expired invitation link.', 'danger')
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # Force student role for token registrations
        role = 'student'
        
        # Validate required fields
        if not username or not email or not first_name or not last_name or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.register_with_token', token=token))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register_with_token', token=token))
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already in use', 'danger')
            return redirect(url_for('auth.register_with_token', token=token))
        
        # Create new student without section_id
        new_user = User(
            username=username, 
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        new_user.set_password(password)
        
        # Add the user first to get an ID
        db.session.add(new_user)
        db.session.flush()
        
        # Create enrollment in the section
        enrollment = StudentEnrollment(
            student_id=new_user.id,
            section_id=section.id,
            is_active=True
        )
        db.session.add(enrollment)
        db.session.commit()
        
        flash(f'Registration successful! You have been added to the {section.name} section.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_with_token.html', section=section, token=token)

@auth.route('/join/')
def join_section_form():
    """Display a form for students to enter an invitation token"""
    if not current_user.is_authenticated:
        flash('Please log in to join a classroom.', 'info')
        return redirect(url_for('auth.login'))
    
    # Check if user is a student
    if not current_user.is_student():
        flash('Only students can join classrooms.', 'warning')
        return redirect(url_for('main.index'))
    
    return render_template('auth/join_section.html')

@auth.route('/join/<token>')
def join_section(token):
    """For existing users to join a section using a token"""
    logging.debug(f"Join section token received: '{token}'")

    if not current_user.is_authenticated:
        # Store the token in session and redirect to login
        session['invitation_token'] = token
        flash('Please log in to join this section.', 'info')
        return redirect(url_for('auth.login'))
    
    # Check if user is a student
    if not current_user.is_student():
        flash('Only students can join sections.', 'warning')
        return redirect(url_for('main.index'))
    
    # Find section by token
    section = Section.find_by_token(token)
    if not section:
        flash('Invalid or expired invitation link.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if student is already in this section
    existing_enrollment = StudentEnrollment.query.filter_by(
        student_id=current_user.id,
        section_id=section.id
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.is_active:
            flash(f'You are already enrolled in the {section.name} section.', 'info')
        else:
            # Reactivate the enrollment
            existing_enrollment.is_active = True
            db.session.commit()
            flash(f'Your enrollment in the {section.name} section has been reactivated!', 'success')
    else:
        # Create new enrollment
        enrollment = StudentEnrollment(
            student_id=current_user.id,
            section_id=section.id,
            is_active=True
        )
        db.session.add(enrollment)
        db.session.commit()
        flash(f'You have successfully joined the {section.name} section!', 'success')
    
    return redirect(url_for('student.dashboard'))

@auth.route('/join/submit', methods=['POST'])
def join_token_submit():
    """Handle token submission from the join_section form"""
    if not current_user.is_authenticated:
        flash('Please log in to join a classroom.', 'info')
        return redirect(url_for('auth.login'))
    
    # Check if user is a student
    if not current_user.is_student():
        flash('Only students can join classrooms.', 'warning')
        return redirect(url_for('main.index'))
    
    token = request.form.get('token')
    if not token:
        flash('Please enter a valid invitation token.', 'warning')
        return redirect(url_for('auth.join_section_form'))
    
    # Redirect to the token-specific route
    return redirect(url_for('auth.join_section', token=token))

# Process invitation token after login
def process_invitation(sender, user):
    token = session.pop('invitation_token', None)
    if token and user.is_student():
        section = Section.find_by_token(token)
        if section:
            # Check if student is already in this section
            existing_enrollment = StudentEnrollment.query.filter_by(
                student_id=user.id,
                section_id=section.id
            ).first()
            
            if existing_enrollment:
                if existing_enrollment.is_active:
                    flash(f'You are already enrolled in the {section.name} section.', 'info')
                else:
                    # Reactivate the enrollment
                    existing_enrollment.is_active = True
                    db.session.commit()
                    flash(f'Your enrollment in the {section.name} section has been reactivated!', 'success')
            else:
                # Create new enrollment
                enrollment = StudentEnrollment(
                    student_id=user.id,
                    section_id=section.id,
                    is_active=True
                )
                db.session.add(enrollment)
                db.session.commit()
                flash(f'You have successfully joined the {section.name} section!', 'success')

# Register the callback with Flask-Login
user_logged_in.connect(process_invitation) 

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Validate new password
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password updated successfully!', 'success')
        return redirect(url_for('auth.change_password'))
    
    return render_template('auth/change_password.html') 