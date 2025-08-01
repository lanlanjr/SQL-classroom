# SQL Classroom

SQL Classroom is a web-based application designed for teaching and learning SQL through interactive exercises. It provides tools for teachers to create SQL questions and for students to practice SQL queries with immediate feedback.

## Recent Improvements

### 1. Enhanced Security
- Improved logout functionality with prevention of back-button access
- Added cache control headers for authenticated pages
- Implemented restricted MySQL user (sql_student) with limited permissions
- **NEW: Comprehensive DQL-only restrictions** - Both teachers and students are now restricted to Data Query Language (DQL) operations only:
  - **Allowed**: SELECT statements, SHOW commands, DESCRIBE, EXPLAIN
  - **Forbidden**: DDL (CREATE, DROP, ALTER), DML (INSERT, UPDATE, DELETE), DCL (GRANT, REVOKE), TCL (COMMIT, ROLLBACK)
  - Added robust query validation to prevent any database modification operations
  - File operations and system schema access are blocked for security

### 2. Multiple Classroom Support
Students can now be enrolled in multiple classrooms simultaneously:
- Switch between classrooms using the navigation bar dropdown
- View assignments from different classrooms
- Track progress separately for each classroom

### 3. Database Exploration Features
- Added tips section in SQL terminal showing available commands
- MySQL-specific commands: SHOW TABLES, DESCRIBE, SHOW COLUMNS
- SQLite-specific commands: SELECT from sqlite_master, PRAGMA table_info
- Improved PRAGMA query result display

### 4. Submission System Improvements
- Fixed submission status consistency between pages
- Enhanced transaction handling for both MySQL and SQLite
- Improved error management and feedback
- Added proper page reloads after submissions

## Features

### For Teachers
- Create SQL query exercises with varying difficulty levels
- Define correct answers and sample database schemas
- Use either in-memory SQLite databases with custom schemas or connect to existing MySQL databases
- Organize questions into assignments
- View student submissions with automated grading
- Track student progress

### For Students
- View assigned SQL questions
- Use an integrated SQL terminal to practice queries
- Submit solutions and receive immediate feedback
- Review past submissions and performance
- Switch between multiple enrolled classrooms

## Technology Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: 
  - Application: SQLite (default), extensible to PostgreSQL or MySQL
  - Exercise databases: In-memory SQLite or existing MySQL databases
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **SQL Terminal**: In-memory SQLite or MySQL connection
- **Automation**: Pandas for result comparison and grading

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- MySQL Server (required for both application and sample databases)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/sql-classroom.git
cd sql-classroom
```

2. **Create a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create a .env file in the project root**

```
SECRET_KEY=your_secure_secret_key
DATABASE_URI=mysql+pymysql://root:admin@localhost:3306/sql_classroom

# MySQL connection for assignment databases
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=admin
MYSQL_PORT=3306

# Student-specific MySQL credentials
MYSQL_STUDENT_USER=sql_student
MYSQL_STUDENT_PASSWORD=student_password
```

Note: The application uses MySQL as the default database. Make sure you have MySQL server installed and running with the credentials specified above.

5. **Initialize the database**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Import Sample Database**

The application comes with a sample database named 'classicmodels' that contains tables for:
- Products and Product Lines
- Offices and Employees
- Customers and Payments
- Orders and Order Details

To import the sample database:

```bash
# On Windows
mysql -u root -padmin < classicmodels_db.sql

# On macOS/Linux
mysql -u root -padmin < classicmodels_db.sql
```

Note: If you get a MySQL access error, try:
```bash
# On Windows
mysql -h localhost -u root -padmin < classicmodels_db.sql

# On macOS/Linux
sudo mysql -u root -padmin < classicmodels_db.sql
```

7. **Create Student MySQL User**

After importing the database, create the restricted student user:

```sql
CREATE USER 'sql_student'@'localhost' IDENTIFIED BY 'student_password';
GRANT SELECT ON *.* TO 'sql_student'@'localhost';
FLUSH PRIVILEGES;
```

## Initial Setup

### Create Admin Account

After setting up the database, you'll need to create an admin account to manage the application:

1. **Using the Flask shell**:
```bash
flask shell
```

2. **Create an admin user**:
```python
from app.models import User
from app import db

admin = User(
    username="admin",
    email="admin@yourschool.com",
    first_name="Admin",
    last_name="User",
    role="teacher"  # Admin users should have teacher role
)
admin.set_password("your_secure_password")
db.session.add(admin)
db.session.commit()
exit()
```

### Running the Application

**For Development:**
```bash
python run.py
```

**For Production (using wsgi.py):**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```
Or configure your web server (Apache, Nginx) to use the `wsgi.py` file.

The application will be available at http://localhost:5000 (development) or your configured port (production).

## Security Considerations

- Passwords are hashed using bcrypt
- SQL queries are executed in isolated environments
- Restricted MySQL user permissions for student queries (using sql_student account)
- **Comprehensive DQL-only restrictions**: Both teachers and students are limited to Data Query Language operations only
  - Only SELECT, SHOW, DESCRIBE, EXPLAIN commands are allowed
  - All DDL (CREATE, DROP, ALTER), DML (INSERT, UPDATE, DELETE), DCL (GRANT, REVOKE), and TCL (COMMIT, ROLLBACK) operations are forbidden
  - File operations (INTO OUTFILE, LOAD DATA) are blocked
  - System schema access (INFORMATION_SCHEMA, mysql) is restricted
  - SQL comments and multiple statements are prevented to avoid injection attacks
- Cache control headers prevent authenticated page access after logout
- Form validation protects against common vulnerabilities

## Troubleshooting

- If you encounter database errors, check your MySQL connection settings in `.env`
- For permissions errors, ensure both root and sql_student users have appropriate permissions
- If the MySQL connection fails, verify that your MySQL server is running on port 3306
- For submission issues, check the browser console and server logs
- Clear browser cache if experiencing caching-related issues

## License

This project is licensed under the MIT License - see the LICENSE file for details. 