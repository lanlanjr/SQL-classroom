# SQL Classroom

SQL Classroom is a web-based application designed for teaching and learning SQL through interactive exercises. It provides tools for teachers to create SQL questions and for students to practice SQL queries with immediate feedback.

## Recent Improvements

### 1. Enhanced Security
- Improved logout functionality with prevention of back-button access
- Added cache control headers for authenticated pages
- Implemented restricted MySQL user (sql_student) with limited permissions
- Added validation for student SQL queries

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

## Testing the Application

### Using the Reset Script

We provide two scripts for testing the application with dummy data:

1. **Reset the application to a clean state**:
```bash
python reset_app.py
```
This will:
- Reset the database to a clean state
- Create core tables and apply migrations
- Create an admin user (username: admin, password: password)

2. **Create dummy data for testing**:
```bash
python create_dummy_data.py
```
This will generate:
- Sample teachers and students
- Multiple classrooms with assignments
- Practice questions with varying difficulty levels
- Student enrollments across different classrooms

### Testing Accounts

After running the scripts, you can use these accounts:

**Admin/Teacher Account**:
- Username: admin
- Password: password

**Sample Teacher Accounts**:
- Username: teacher1 through teacher4
- Password: password

**Sample Student Accounts**:
- Username: student_1 through student_20
- Password: password

### Running the Application

```bash
python run.py
flask run --host=0.0.0.0 --debug
```

The application will be available at http://localhost:5000

## Security Considerations

- Passwords are hashed using bcrypt
- SQL queries are executed in isolated environments
- Restricted MySQL user permissions for student queries (using sql_student account)
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