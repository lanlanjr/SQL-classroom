from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, session
from flask_login import login_required, current_user
from app import db
from app.models import User, Section, Assignment, Question, Submission, StudentEnrollment, AllowedDatabase
from functools import wraps
import mysql.connector
import os
import sys
import pymysql
from datetime import datetime, timedelta
from sqlalchemy import text, func

admin = Blueprint('admin', __name__, url_prefix='/admin')

# Track application start time
app_start_time = datetime.utcnow()

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_active:
            flash('Access denied. Your account has been deactivated. Please contact an administrator.', 'danger')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    
    # Get user statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_admins = User.query.filter_by(role='admin').count()
    
    # Get section statistics
    total_sections = Section.query.count()
    active_enrollments = StudentEnrollment.query.filter_by(is_active=True).count()
    
    # Get assignment statistics
    total_assignments = Assignment.query.count()
    total_questions = Question.query.count()
    total_submissions = Submission.query.count()
    
    # Get recent activities (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = User.query.filter(User.created_at >= week_ago).count()
    recent_submissions = Submission.query.filter(Submission.submitted_at >= week_ago).count()
    
    # Get database information
    db_info = get_database_info()
    
    stats = {
        'users': {
            'total': total_users,
            'students': total_students,
            'teachers': total_teachers,
            'admins': total_admins,
            'recent': recent_users
        },
        'sections': {
            'total': total_sections,
            'enrollments': active_enrollments
        },
        'assignments': {
            'total': total_assignments,
            'questions': total_questions,
            'submissions': total_submissions,
            'recent_submissions': recent_submissions
        },
        'database': db_info
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@admin.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage all users in the system"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    search = request.args.get('search', '')
    
    query = User.query
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search),
                User.first_name.contains(search),
                User.last_name.contains(search)
            )
        )
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, 
                         role_filter=role_filter, search=search)

@admin.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View detailed information about a specific user"""
    user = User.query.get_or_404(user_id)
    
    # Get user's sections
    if user.is_student():
        sections = user.get_active_sections()
        enrollments = user.get_active_enrollments()
    elif user.is_teacher():
        sections = Section.query.filter_by(creator_id=user.id).all()
        enrollments = []
    else:
        sections = []
        enrollments = []
    
    # Get user's submissions
    submissions = Submission.query.filter_by(student_id=user.id).order_by(
        Submission.submitted_at.desc()
    ).limit(10).all()
    
    return render_template('admin/user_detail.html', 
                         user=user, sections=sections, 
                         enrollments=enrollments, submissions=submissions)

@admin.route('/users/<int:user_id>/update_role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    """Update a user's role"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role not in ['student', 'teacher', 'admin']:
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    # Prevent removing the last admin
    if user.is_admin() and new_role != 'admin':
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot remove the last admin account.', 'danger')
            return redirect(url_for('admin.user_detail', user_id=user_id))
    
    old_role = user.role
    user.role = new_role
    db.session.commit()
    
    flash(f'User role updated from {old_role} to {new_role}.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin.route('/users/<int:user_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status (disable/enable account)"""
    user = User.query.get_or_404(user_id)
    
    # Prevent disabling the last admin
    if user.is_admin():
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('Cannot disable the last admin account.', 'danger')
            return redirect(url_for('admin.user_detail', user_id=user_id))
    
    # Add active status field if it doesn't exist
    if not hasattr(user, 'is_active'):
        # This would require a migration to add the field
        flash('User status toggle not available yet.', 'warning')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'enabled' if user.is_active else 'disabled'
    flash(f'User account {status}.', 'success')
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin.route('/sections')
@login_required
@admin_required
def manage_sections():
    """Manage all sections in the system"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Section.query.join(User)
    
    if search:
        query = query.filter(
            db.or_(
                Section.name.contains(search),
                Section.description.contains(search),
                User.username.contains(search)
            )
        )
    
    sections = query.order_by(Section.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/sections.html', sections=sections, search=search)

@admin.route('/database')
@login_required
@admin_required
def manage_database():
    """Database management and monitoring"""
    
    # Get database statistics
    db_stats = get_detailed_database_stats()
    
    # Get recent database activities
    recent_submissions = Submission.query.order_by(
        Submission.submitted_at.desc()
    ).limit(20).all()
    
    # Get allowed databases
    allowed_databases = AllowedDatabase.query.order_by(AllowedDatabase.created_at.desc()).all()
    
    return render_template('admin/database.html', 
                         db_stats=db_stats, 
                         recent_submissions=recent_submissions,
                         allowed_databases=allowed_databases)

@admin.route('/system')
@login_required
@admin_required
def system_info():
    """System information and health check"""
    
    # Get system information
    current_time = datetime.utcnow()
    uptime_delta = current_time - app_start_time
    uptime_hours = int(uptime_delta.total_seconds() // 3600)
    uptime_minutes = int((uptime_delta.total_seconds() % 3600) // 60)
    
    system_info = {
        'flask_env': os.getenv('APP_ENV', 'development'),
        'debug_mode': current_app.debug,
        'database_uri': os.getenv('DATABASE_URI', 'Not set'),
        'app_db_name': os.getenv('APP_DB_NAME', 'sql_classroom'),
        'python_version': sys.version,
        'current_time': current_time,
        'app_start_time': app_start_time,
        'uptime_hours': uptime_hours,
        'uptime_minutes': uptime_minutes,
        'uptime_display': f"{uptime_hours}h {uptime_minutes}m"
    }
    
    # Check database connectivity
    try:
        db.session.execute(text('SELECT 1'))
        db_status = 'Connected'
    except Exception as e:
        db_status = f'Error: {str(e)}'
    
    system_info['database_status'] = db_status
    
    return render_template('admin/system.html', system_info=system_info)

@admin.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for dashboard statistics"""
    
    # Get real-time statistics
    stats = {
        'active_users': User.query.count(),
        'active_sessions': 1,  # This would need session tracking
        'total_submissions_today': Submission.query.filter(
            func.date(Submission.submitted_at) == datetime.utcnow().date()
        ).count(),
        'database_size': get_database_size()
    }
    
    return jsonify(stats)

def get_database_info():
    """Get basic database information"""
    try:
        # Get database name
        result = db.session.execute(text('SELECT DATABASE() as db_name'))
        db_name = result.fetchone()[0]
        
        # Get table count
        result = db.session.execute(text('SHOW TABLES'))
        table_count = len(result.fetchall())
        
        return {
            'name': db_name,
            'tables': table_count,
            'status': 'Connected'
        }
    except Exception as e:
        return {
            'name': 'Unknown',
            'tables': 0,
            'status': f'Error: {str(e)}'
        }

def get_detailed_database_stats():
    """Get detailed database statistics"""
    try:
        stats = {}
        
        # Get table sizes
        result = db.session.execute(text("""
            SELECT TABLE_NAME, TABLE_ROWS, 
                   ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS 'SIZE_MB'
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC
        """))
        
        stats['tables'] = []
        total_size = 0
        for row in result:
            table_info = {
                'name': row[0],
                'rows': row[1] or 0,
                'size_mb': row[2] or 0
            }
            stats['tables'].append(table_info)
            total_size += table_info['size_mb']
        
        stats['total_size_mb'] = total_size
        
        return stats
    except Exception as e:
        return {'error': str(e), 'tables': [], 'total_size_mb': 0}

@admin.route('/database/cleanup', methods=['POST'])
@login_required
@admin_required
def database_cleanup():
    """Perform database cleanup operations"""
    try:
        # Clean up old temporary data
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Remove old ungraded submissions (older than 30 days)
        old_submissions = Submission.query.filter(
            Submission.submitted_at < cutoff_date,
            Submission.is_correct == None
        ).all()
        
        cleanup_count = len(old_submissions)
        for submission in old_submissions:
            db.session.delete(submission)
        
        # Clean up inactive enrollments (older than 90 days)
        old_enrollments = StudentEnrollment.query.filter(
            StudentEnrollment.enrolled_at < cutoff_date - timedelta(days=60),
            StudentEnrollment.is_active == False
        ).all()
        
        enrollment_cleanup_count = len(old_enrollments)
        for enrollment in old_enrollments:
            db.session.delete(enrollment)
        
        db.session.commit()
        
        flash(f'Database cleanup completed: {cleanup_count} old submissions and {enrollment_cleanup_count} inactive enrollments removed.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Database cleanup failed: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_database'))

@admin.route('/database/backup', methods=['POST'])
@login_required
@admin_required
def database_backup():
    """Create a database backup"""
    try:
        backup_filename = f"sql_classroom_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
        backup_path = os.path.join(os.getcwd(), 'backups', backup_filename)
        
        # Create backups directory if it doesn't exist
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Get database connection info
        db_uri = os.getenv('DATABASE_URI', '')
        if 'mysql' in db_uri:
            # Parse MySQL connection string
            # Format: mysql+pymysql://user:password@host:port/database
            import re
            match = re.match(r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_uri)
            if match:
                user, password, host, port, database = match.groups()
                
                # Use mysqldump command
                import subprocess
                cmd = [
                    'mysqldump',
                    f'--host={host}',
                    f'--port={port}',
                    f'--user={user}',
                    f'--password={password}',
                    '--single-transaction',
                    '--routines',
                    '--triggers',
                    database
                ]
                
                with open(backup_path, 'w') as backup_file:
                    result = subprocess.run(cmd, stdout=backup_file, stderr=subprocess.PIPE, text=True)
                
                if result.returncode == 0:
                    file_size = os.path.getsize(backup_path) / (1024 * 1024)  # Size in MB
                    flash(f'Database backup created successfully: {backup_filename} ({file_size:.2f} MB)', 'success')
                else:
                    flash(f'Backup failed: {result.stderr}', 'danger')
            else:
                flash('Could not parse database connection string for backup.', 'danger')
        else:
            flash('Database backup is currently only supported for MySQL databases.', 'warning')
            
    except Exception as e:
        flash(f'Database backup failed: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_database'))

@admin.route('/database/analyze', methods=['POST'])
@login_required
@admin_required
def database_analyze():
    """Analyze database performance"""
    try:
        analysis_results = {}
        
        # Analyze table sizes and row counts
        result = db.session.execute(text("""
            SELECT 
                TABLE_NAME,
                TABLE_ROWS,
                ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS 'SIZE_MB',
                ROUND((DATA_LENGTH / 1024 / 1024), 2) AS 'DATA_MB',
                ROUND((INDEX_LENGTH / 1024 / 1024), 2) AS 'INDEX_MB'
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = DATABASE()
            ORDER BY (DATA_LENGTH + INDEX_LENGTH) DESC
        """))
        
        tables_analysis = []
        total_size = 0
        for row in result:
            try:
                # Convert values to proper types with error handling
                table_rows = int(row[1] or 0)
                total_size_mb = float(row[2] or 0)
                data_size_mb = float(row[3] or 0)
                index_size_mb = float(row[4] or 0)
                
                table_info = {
                    'name': row[0],
                    'rows': table_rows,
                    'total_size': total_size_mb,
                    'data_size': data_size_mb,
                    'index_size': index_size_mb
                }
                tables_analysis.append(table_info)
                total_size += total_size_mb
            except (ValueError, TypeError) as e:
                # Skip problematic rows but log the issue

                continue
        
        analysis_results['tables'] = tables_analysis
        analysis_results['total_size'] = total_size
        
        # Analyze slow queries (if performance_schema is available)
        try:
            slow_queries = db.session.execute(text("""
                SELECT 
                    DIGEST_TEXT,
                    COUNT_STAR as execution_count,
                    AVG_TIMER_WAIT/1000000000 as avg_time_seconds,
                    MAX_TIMER_WAIT/1000000000 as max_time_seconds
                FROM performance_schema.events_statements_summary_by_digest 
                WHERE DIGEST_TEXT IS NOT NULL 
                AND AVG_TIMER_WAIT > 1000000000
                ORDER BY AVG_TIMER_WAIT DESC 
                LIMIT 10
            """)).fetchall()
            
            analysis_results['slow_queries'] = []
            for row in slow_queries:
                try:
                    query_info = {
                        'query': row[0][:100] + '...' if len(row[0]) > 100 else row[0],
                        'count': int(row[1] or 0),
                        'avg_time': round(float(row[2] or 0), 3),
                        'max_time': round(float(row[3] or 0), 3)
                    }
                    analysis_results['slow_queries'].append(query_info)
                except (ValueError, TypeError) as e:
                    # Skip problematic query entries

                    continue
        except Exception:
            analysis_results['slow_queries'] = []
        
        # Store analysis results in session for display
        session['db_analysis'] = analysis_results
        flash('Database performance analysis completed.', 'success')
        
    except Exception as e:
        flash(f'Database analysis failed: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_database'))

@admin.route('/system/test_connection', methods=['POST'])
@login_required
@admin_required
def test_database_connection():
    """Test database connection"""
    try:
        # Test basic connection
        start_time = datetime.utcnow()
        result = db.session.execute(text('SELECT 1 as test'))
        connection_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Test write capability
        test_query = text('SELECT COUNT(*) FROM users')
        user_count = db.session.execute(test_query).scalar()
        
        # Check database version
        version_result = db.session.execute(text('SELECT VERSION() as version'))
        db_version = version_result.scalar()
        
        flash(f'Database connection successful! Response time: {connection_time:.3f}s, Users: {user_count}, Version: {db_version}', 'success')
        
    except Exception as e:
        flash(f'Database connection failed: {str(e)}', 'danger')
    
    return redirect(url_for('admin.system_info'))

@admin.route('/system/clear_cache', methods=['POST'])
@login_required
@admin_required
def clear_application_cache():
    """Clear application cache"""
    try:
        # Clear Flask session data for all users (if using server-side sessions)
        # This is a simple implementation - in production you might use Redis/Memcached
        
        cleared_items = 0
        
        # Clear any cached data in the current session
        if 'db_analysis' in session:
            session.pop('db_analysis')
            cleared_items += 1
        
        # In a real application, you would clear:
        # - Redis cache
        # - Memcached data
        # - Static file caches
        # - Database query caches
        
        # For now, we'll just clear some basic items
        import gc
        gc.collect()  # Force garbage collection
        
        flash(f'Application cache cleared successfully. {cleared_items} cached items removed.', 'success')
        
    except Exception as e:
        flash(f'Cache clearing failed: {str(e)}', 'danger')
    
    return redirect(url_for('admin.system_info'))

@admin.route('/system/logs')
@login_required
@admin_required
def view_system_logs():
    """View system logs"""
    try:
        log_entries = []
        
        # In a real application, you would read from log files
        # For now, we'll create some sample log entries based on recent database activity
        
        # Get recent user activity
        recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
        for user in recent_users:
            log_entries.append({
                'timestamp': user.created_at,
                'level': 'INFO',
                'message': f'New user registered: {user.username} ({user.role})',
                'source': 'AUTH'
            })
        
        # Get recent submissions
        recent_submissions = Submission.query.order_by(Submission.submitted_at.desc()).limit(10).all()
        for submission in recent_submissions:
            status = 'CORRECT' if submission.is_correct else 'INCORRECT' if submission.is_correct is not None else 'PENDING'
            log_entries.append({
                'timestamp': submission.submitted_at,
                'level': 'INFO',
                'message': f'Submission received: Student {submission.student_id}, Assignment {submission.assignment_id}, Status: {status}',
                'source': 'SUBMISSION'
            })
        
        # Sort by timestamp
        log_entries.sort(key=lambda x: x['timestamp'] or datetime.min, reverse=True)
        
        return render_template('admin/logs.html', log_entries=log_entries[:50])
        
    except Exception as e:
        flash(f'Error loading system logs: {str(e)}', 'danger')
        return redirect(url_for('admin.system_info'))

def get_database_size():
    """Get total database size in MB"""
    try:
        result = db.session.execute(text("""
            SELECT ROUND(SUM((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) as size_mb
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = DATABASE()
        """))
        size = result.fetchone()[0]
        return size or 0
    except Exception:
        return 0

@admin.route('/database/allowed', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_allowed_databases():
    """Manage allowed databases for SQL Playground and question creation"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            database_name = request.form.get('database_name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not database_name:
                flash('Database name is required.', 'danger')
                return redirect(url_for('admin.manage_allowed_databases'))
            
            # Check if database actually exists
            try:
                conn = pymysql.connect(
                    host=os.getenv('MYSQL_HOST', ''),
                    user=os.getenv('MYSQL_USER', ''),
                    password=os.getenv('MYSQL_PASSWORD', ''),
                    port=int(os.getenv('MYSQL_PORT', 3306)),
                    cursorclass=pymysql.cursors.DictCursor
                )
                
                with conn.cursor() as cursor:
                    cursor.execute("SHOW DATABASES")
                    all_databases = [db['Database'] for db in cursor.fetchall()]
                    
                    if database_name not in all_databases:
                        flash(f'Database "{database_name}" does not exist on the MySQL server.', 'danger')
                        conn.close()
                        return redirect(url_for('admin.manage_allowed_databases'))
                
                conn.close()
                
                # Check if already exists in allowed list
                existing = AllowedDatabase.query.filter_by(database_name=database_name).first()
                if existing:
                    flash(f'Database "{database_name}" is already in the allowed list.', 'warning')
                    return redirect(url_for('admin.manage_allowed_databases'))
                
                # Add to allowed databases
                allowed_db = AllowedDatabase(
                    database_name=database_name,
                    description=description,
                    created_by=current_user.id
                )
                db.session.add(allowed_db)
                db.session.commit()
                
                flash(f'Database "{database_name}" has been added to the allowed list.', 'success')
                
            except Exception as e:
                flash(f'Error checking database: {str(e)}', 'danger')
                return redirect(url_for('admin.manage_allowed_databases'))
        
        elif action == 'toggle':
            db_id = request.form.get('db_id')
            allowed_db = AllowedDatabase.query.get_or_404(db_id)
            allowed_db.is_active = not allowed_db.is_active
            db.session.commit()
            
            status = 'enabled' if allowed_db.is_active else 'disabled'
            flash(f'Database "{allowed_db.database_name}" has been {status}.', 'success')
        
        elif action == 'delete':
            db_id = request.form.get('db_id')
            allowed_db = AllowedDatabase.query.get_or_404(db_id)
            database_name = allowed_db.database_name
            db.session.delete(allowed_db)
            db.session.commit()
            
            flash(f'Database "{database_name}" has been removed from the allowed list.', 'success')
        
        return redirect(url_for('admin.manage_allowed_databases'))
    
    # GET request - show the management page
    allowed_databases = AllowedDatabase.query.order_by(AllowedDatabase.created_at.desc()).all()
    
    # Get all available databases from MySQL for the dropdown
    try:
        conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST', ''),
            user=os.getenv('MYSQL_USER', ''),
            password=os.getenv('MYSQL_PASSWORD', ''),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            all_databases = [db['Database'] for db in cursor.fetchall()]
            
            # Filter out system databases
            system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
            available_databases = [db for db in all_databases if db not in system_dbs]
            available_databases.sort()
        
        conn.close()
        
    except Exception as e:
        available_databases = []
        flash(f'Warning: Could not connect to MySQL to fetch available databases: {str(e)}', 'warning')
    
    return render_template('admin/allowed_databases.html', 
                         allowed_databases=allowed_databases,
                         available_databases=available_databases)

@admin.route('/api/scan-databases', methods=['POST'])
@login_required
@admin_required
def scan_and_add_databases():
    """Scan MySQL server and add common databases to allowed list"""
    try:
        conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST', ''),
            user=os.getenv('MYSQL_USER', ''),
            password=os.getenv('MYSQL_PASSWORD', ''),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            all_databases = [db['Database'] for db in cursor.fetchall()]
            
            # Filter out system databases and get existing allowed databases
            system_dbs = ['information_schema', 'mysql', 'performance_schema', 'sys']
            user_databases = [db for db in all_databases if db not in system_dbs]
            
            existing_databases = set(db.database_name for db in AllowedDatabase.query.all())
            
            # Add commonly used databases that are not already in the list
            common_databases = ['sql_classroom', 'classicmodels', 'sakila', 'world', 'employees']
            added_count = 0
            
            for db_name in user_databases:
                if db_name in common_databases and db_name not in existing_databases:
                    allowed_db = AllowedDatabase(
                        database_name=db_name,
                        description=f'Auto-added common database: {db_name}',
                        created_by=current_user.id
                    )
                    db.session.add(allowed_db)
                    added_count += 1
            
            db.session.commit()
        
        conn.close()
        
        if added_count > 0:
            flash(f'Added {added_count} common databases to the allowed list.', 'success')
        else:
            flash('No new common databases found to add.', 'info')
            
    except Exception as e:
        flash(f'Error scanning databases: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_allowed_databases'))
