# SQL Classroom - Deployment Guide

## Production Deployment Checklist

### 1. Environment Setup
- [ ] Set `APP_ENV=production` in your environment
- [ ] Configure secure `SECRET_KEY`
- [ ] Set up production database connection in `DATABASE_URI`
- [ ] Configure MySQL credentials for student access
- [ ] Disable Flask debug mode

### 2. Security Configuration
- [ ] Change default admin password immediately after first login
- [ ] Review and configure CORS settings if needed
- [ ] Set up HTTPS in production
- [ ] Configure secure session cookies
- [ ] Review file upload permissions

### 3. Database Setup
1. Create production database
2. Run migrations: `flask db upgrade`
3. Import sample database: `mysql -u root -p < classicmodels_db.sql`
4. Create restricted student user (see README.md)
5. Create admin account (see README.md)

### 4. Web Server Configuration

#### Using Gunicorn (Recommended)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

#### Using Apache with mod_wsgi
Point to `wsgi.py` file in your Apache virtual host configuration.

#### Using Nginx + Gunicorn
Set up Nginx as reverse proxy to Gunicorn.

### 5. Monitoring & Logging
- [ ] Configure application logging
- [ ] Set up error monitoring
- [ ] Monitor database performance
- [ ] Set up backup procedures

### 6. Performance Optimization
- [ ] Configure database connection pooling
- [ ] Enable gzip compression
- [ ] Set up static file serving
- [ ] Configure caching headers

## Files Structure for Deployment

### Required Files:
- `app/` - Main application code
- `migrations/` - Database migrations
- `instance/` - Instance-specific data
- `backups/` - Backup directory
- `wsgi.py` - WSGI entry point
- `run.py` - Development server entry point
- `requirements.txt` - Python dependencies
- `classicmodels_db.sql` - Sample database
- `.env` - Environment configuration
- `README.md` - Setup instructions

### Removed for Production:
- All `test_*.py` files
- Development documentation (`*_FIX.md`, `*_ENHANCEMENT.md`)
- Setup/utility scripts (`reset_app.py`, `create_dummy_data.py`, etc.)
- Debug routes and development-only code

## Environment Variables for Production

```bash
# Required
SECRET_KEY=your_very_secure_secret_key_here
DATABASE_URI=mysql+pymysql://user:password@localhost:3306/sql_classroom
APP_ENV=production

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_PORT=3306

# Student MySQL User
MYSQL_STUDENT_USER=sql_student
MYSQL_STUDENT_PASSWORD=student_secure_password

# Optional
APP_DB_NAME=sql_classroom
```

## Post-Deployment Steps

1. **Test Application**:
   - Verify login functionality
   - Test student/teacher workflows
   - Confirm database connectivity
   - Check SQL execution security

2. **Create Initial Content**:
   - Set up initial classrooms/sections
   - Create sample assignments
   - Test student enrollment process

3. **User Management**:
   - Create teacher accounts
   - Set up invitation system
   - Configure user roles properly

## Security Notes

- The application enforces DQL-only restrictions for SQL queries
- Student MySQL user has read-only permissions
- All user inputs are validated and sanitized
- Session management includes cache control headers
- CSRF protection is enabled on all forms

## Support

For deployment issues, review the main README.md file and check:
- Database connectivity
- File permissions
- Environment variable configuration
- Web server logs
