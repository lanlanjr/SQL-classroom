import os
import sys
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

# Add the current directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the application components
from app import create_app, db
from app.models import User, Section, StudentEnrollment, Assignment, AssignmentQuestion, Question, SectionAssignment

# Create the Flask application
app = create_app()

# List of subject areas for section names
SUBJECTS = [
    "Database Fundamentals", "SQL Basics", "Advanced SQL",
    "Data Analysis", "Query Optimization", "SQL Reporting"
]

# Teacher and student data
TEACHERS = [
    {
        "username": "teacher1",
        "email": "teacher1@example.com",
        "first_name": "John",
        "last_name": "Smith",
        "password": "password" 
    },
    {
        "username": "teacher2",
        "email": "teacher2@example.com",
        "first_name": "Emily",
        "last_name": "Johnson",
        "password": "password"
    },
    {
        "username": "teacher3",
        "email": "teacher3@example.com",
        "first_name": "Michael",
        "last_name": "Davis",
        "password": "password"
    },
    {
        "username": "teacher4",
        "email": "teacher4@example.com",
        "first_name": "Sarah",
        "last_name": "Wilson",
        "password": "password"
    }
]

# Student first and last names for generating random students
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", 
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

# Sample SQL questions by category
SQL_QUESTIONS = {
    "Database Fundamentals": [
        {
            "title": "Basic SELECT Query",
            "description": "Write a SQL query to select all customers from the customers table.\n\nSolution: `SELECT * FROM customers;`",
            "question_type": "free_response",
            "difficulty": 1,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT * FROM customers;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        },
        {
            "title": "SELECT with WHERE Clause",
            "description": "Write a SQL query to find all customers from the USA.\n\nSolution: `SELECT * FROM customers WHERE country = 'USA';`",
            "question_type": "free_response",
            "difficulty": 1,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT * FROM customers WHERE country = 'USA';",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        },
        {
            "title": "SELECT with COUNT",
            "description": "Write a SQL query to count the total number of orders.\n\nSolution: `SELECT COUNT(*) as total_orders FROM orders;`",
            "question_type": "free_response",
            "difficulty": 1,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT COUNT(*) as total_orders FROM orders;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        }
    ],
    "SQL Basics": [
        {
            "title": "Simple JOIN Query",
            "description": "Write a SQL query to show customer names and their order numbers.\n\nSolution: `SELECT customers.customerName, orders.orderNumber FROM customers JOIN orders ON customers.customerNumber = orders.customerNumber;`",
            "question_type": "free_response",
            "difficulty": 2,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT customers.customerName, orders.orderNumber FROM customers JOIN orders ON customers.customerNumber = orders.customerNumber;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        },
        {
            "title": "Aggregate with GROUP BY",
            "description": "Write a SQL query to find the total amount of payments received from each customer.\n\nSolution: `SELECT customerNumber, SUM(amount) as total_payments FROM payments GROUP BY customerNumber;`",
            "question_type": "free_response",
            "difficulty": 2,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT customerNumber, SUM(amount) as total_payments FROM payments GROUP BY customerNumber;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        },
        {
            "title": "SELECT with ORDER BY",
            "description": "Write a SQL query to list all products ordered by price (MSRP) in descending order.\n\nSolution: `SELECT productName, MSRP FROM products ORDER BY MSRP DESC;`",
            "question_type": "free_response",
            "difficulty": 2,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT productName, MSRP FROM products ORDER BY MSRP DESC;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        }
    ],
    "Advanced SQL": [
        {
            "title": "Subquery in WHERE Clause",
            "description": "Write a SQL query to find all customers who have placed orders with a total amount greater than the average order amount.\n\nSolution: `SELECT DISTINCT c.customerName FROM customers c JOIN orders o ON c.customerNumber = o.customerNumber JOIN orderdetails od ON o.orderNumber = od.orderNumber WHERE (SELECT SUM(quantityOrdered * priceEach) FROM orderdetails WHERE orderNumber = o.orderNumber) > (SELECT AVG(total) FROM (SELECT SUM(quantityOrdered * priceEach) as total FROM orderdetails GROUP BY orderNumber) as avg_totals);`",
            "question_type": "free_response",
            "difficulty": 3,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT DISTINCT c.customerName FROM customers c JOIN orders o ON c.customerNumber = o.customerNumber JOIN orderdetails od ON o.orderNumber = od.orderNumber WHERE (SELECT SUM(quantityOrdered * priceEach) FROM orderdetails WHERE orderNumber = o.orderNumber) > (SELECT AVG(total) FROM (SELECT SUM(quantityOrdered * priceEach) as total FROM orderdetails GROUP BY orderNumber) as avg_totals);",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        },
        {
            "title": "Complex JOIN with Multiple Tables",
            "description": "Write a SQL query to show customer names, their orders, and the products in each order.\n\nSolution: `SELECT c.customerName, o.orderNumber, p.productName, od.quantityOrdered, od.priceEach FROM customers c JOIN orders o ON c.customerNumber = o.customerNumber JOIN orderdetails od ON o.orderNumber = od.orderNumber JOIN products p ON od.productCode = p.productCode;`",
            "question_type": "free_response",
            "difficulty": 3,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT c.customerName, o.orderNumber, p.productName, od.quantityOrdered, od.priceEach FROM customers c JOIN orders o ON c.customerNumber = o.customerNumber JOIN orderdetails od ON o.orderNumber = od.orderNumber JOIN products p ON od.productCode = p.productCode;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        },
        {
            "title": "Window Function Query",
            "description": "Write a SQL query to rank customers by their total payment amounts.\n\nSolution: `SELECT customerName, total_payment, RANK() OVER (ORDER BY total_payment DESC) as payment_rank FROM (SELECT c.customerName, SUM(p.amount) as total_payment FROM customers c JOIN payments p ON c.customerNumber = p.customerNumber GROUP BY c.customerName) as customer_payments;`",
            "question_type": "free_response",
            "difficulty": 3,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT customerName, total_payment, RANK() OVER (ORDER BY total_payment DESC) as payment_rank FROM (SELECT c.customerName, SUM(p.amount) as total_payment FROM customers c JOIN payments p ON c.customerNumber = p.customerNumber GROUP BY c.customerName) as customer_payments;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        }
    ],
    "Query Optimization": [
        {
            "title": "Efficient Product Sales Analysis",
            "description": "Write an optimized SQL query to find the top 5 best-selling products by total revenue.\n\nSolution: `SELECT p.productCode, p.productName, SUM(od.quantityOrdered * od.priceEach) as total_revenue FROM products p JOIN orderdetails od ON p.productCode = od.productCode GROUP BY p.productCode, p.productName ORDER BY total_revenue DESC LIMIT 5;`",
            "question_type": "free_response",
            "difficulty": 3,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT p.productCode, p.productName, SUM(od.quantityOrdered * od.priceEach) as total_revenue FROM products p JOIN orderdetails od ON p.productCode = od.productCode GROUP BY p.productCode, p.productName ORDER BY total_revenue DESC LIMIT 5;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        },
        {
            "title": "Customer Order History",
            "description": "Write an optimized SQL query to get a summary of each customer's order history including total orders and total value.\n\nSolution: `SELECT c.customerName, COUNT(DISTINCT o.orderNumber) as order_count, SUM(od.quantityOrdered * od.priceEach) as total_value FROM customers c LEFT JOIN orders o ON c.customerNumber = o.customerNumber LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber GROUP BY c.customerNumber, c.customerName;`",
            "question_type": "free_response",
            "difficulty": 3,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT c.customerName, COUNT(DISTINCT o.orderNumber) as order_count, SUM(od.quantityOrdered * od.priceEach) as total_value FROM customers c LEFT JOIN orders o ON c.customerNumber = o.customerNumber LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber GROUP BY c.customerNumber, c.customerName;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        }
    ],
    "SQL Reporting": [
        {
            "title": "Monthly Sales Report",
            "description": "Write a SQL query to generate a monthly sales report showing total sales amount per month.\n\nSolution: `SELECT DATE_FORMAT(o.orderDate, '%Y-%m') as month, SUM(od.quantityOrdered * od.priceEach) as total_sales FROM orders o JOIN orderdetails od ON o.orderNumber = od.orderNumber GROUP BY month ORDER BY month;`",
            "question_type": "free_response",
            "difficulty": 3,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT DATE_FORMAT(o.orderDate, '%Y-%m') as month, SUM(od.quantityOrdered * od.priceEach) as total_sales FROM orders o JOIN orderdetails od ON o.orderNumber = od.orderNumber GROUP BY month ORDER BY month;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        },
        {
            "title": "Employee Sales Performance",
            "description": "Write a SQL query to create a report showing each employee's sales performance including number of customers, orders, and total sales.\n\nSolution: `SELECT e.employeeNumber, CONCAT(e.firstName, ' ', e.lastName) as employee_name, COUNT(DISTINCT c.customerNumber) as total_customers, COUNT(DISTINCT o.orderNumber) as total_orders, SUM(od.quantityOrdered * od.priceEach) as total_sales FROM employees e LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber LEFT JOIN orders o ON c.customerNumber = o.customerNumber LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber GROUP BY e.employeeNumber, employee_name ORDER BY total_sales DESC;`",
            "question_type": "free_response",
            "difficulty": 3,
            "db_type": "mysql",
            "mysql_db_name": "classicmodels",
            "correct_answer": "SELECT e.employeeNumber, CONCAT(e.firstName, ' ', e.lastName) as employee_name, COUNT(DISTINCT c.customerNumber) as total_customers, COUNT(DISTINCT o.orderNumber) as total_orders, SUM(od.quantityOrdered * od.priceEach) as total_sales FROM employees e LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber LEFT JOIN orders o ON c.customerNumber = o.customerNumber LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber GROUP BY e.employeeNumber, employee_name ORDER BY total_sales DESC;",
            "sample_db_schema": "Using classicmodels database with tables: customers, orders, products, employees, payments, orderdetails"
        }
    ]
}

def create_dummy_data():
    """Create dummy data in the database"""
    with app.app_context():
        print("Creating dummy data...")
        
        # Check if there's existing data
        user_count = User.query.count()
        if user_count > 1:  # Allow for the admin account
            print(f"Database already has {user_count} users. Do you want to proceed? This will add more users but not delete existing ones.")
            response = input("Enter 'yes' to continue: ")
            if response.lower() != "yes":
                print("Operation canceled.")
                return
        
        # Create teachers
        teachers = []
        for teacher_data in TEACHERS:
            # Check if teacher already exists
            existing_teacher = User.query.filter_by(email=teacher_data["email"]).first()
            if existing_teacher:
                print(f"Teacher {teacher_data['first_name']} {teacher_data['last_name']} already exists.")
                teachers.append(existing_teacher)
                continue
                
            teacher = User(
                username=teacher_data["username"],
                email=teacher_data["email"],
                first_name=teacher_data["first_name"],
                last_name=teacher_data["last_name"],
                role="teacher",
                created_at=datetime.utcnow()
            )
            teacher.set_password(teacher_data["password"])
            db.session.add(teacher)
            try:
                db.session.commit()
                teachers.append(teacher)
                print(f"Created teacher: {teacher.first_name} {teacher.last_name}")
            except IntegrityError:
                db.session.rollback()
                print(f"Couldn't create teacher {teacher_data['first_name']} {teacher_data['last_name']} - already exists")
        
        # Create sections (classrooms) for each teacher
        sections = []
        for teacher in teachers:
            # Generate 3 random sections for this teacher
            for i in range(3):
                # Choose a random subject that hasn't been used by this teacher
                subject = random.choice(SUBJECTS)
                level = random.choice(["Beginner", "Intermediate", "Advanced"])
                section_name = f"{subject} - {level}"
                
                section = Section(
                    name=section_name,
                    description=f"A course covering {subject} topics for {level.lower()} students.",
                    creator_id=teacher.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(section)
                try:
                    db.session.commit()
                    sections.append(section)
                    print(f"Created section: {section.name} (Teacher: {teacher.first_name} {teacher.last_name})")
                except IntegrityError:
                    db.session.rollback()
                    print(f"Couldn't create section {section_name} - already exists")
        
        # Create students and enroll them in sections
        students = []
        student_count = 0
        
        # First, create all students
        for i in range(20):  # Create 20 students total instead of 5 per section
            # Generate a random student
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            username = f"student_{i+1}"
            email = f"{username}@example.com"
            
            # Check if student already exists
            existing_student = User.query.filter_by(email=email).first()
            if existing_student:
                student = existing_student
                print(f"Student {first_name} {last_name} already exists.")
                students.append(student)
            else:
                student = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role="student",
                    created_at=datetime.utcnow()
                )
                student.set_password("password")
                db.session.add(student)
                try:
                    db.session.commit()
                    student_count += 1
                    students.append(student)
                    print(f"Created student: {student.first_name} {student.last_name}")
                except IntegrityError:
                    db.session.rollback()
                    print(f"Couldn't create student {username} - already exists")
                    continue
        
        # Now enroll each student in 3 different sections
        enrollments_created = 0
        for student in students:
            # Randomly select 3 different sections for this student
            # Make sure to pick sections from different teachers if possible
            teacher_sections = {}
            for teacher in teachers:
                teacher_sections[teacher.id] = [s for s in sections if s.creator_id == teacher.id]
            
            selected_sections = []
            
            # Try to pick one section from each of three different teachers
            available_teachers = list(teacher_sections.keys())
            random.shuffle(available_teachers)
            
            for teacher_id in available_teachers[:3]:  # Take up to 3 teachers
                if teacher_sections[teacher_id]:
                    selected_section = random.choice(teacher_sections[teacher_id])
                    selected_sections.append(selected_section)
                    # Remove this section to avoid duplicates
                    teacher_sections[teacher_id].remove(selected_section)
            
            # If we don't have 3 sections yet, fill in with random sections
            while len(selected_sections) < 3 and sections:
                remaining_sections = [s for s in sections if s not in selected_sections]
                if not remaining_sections:
                    break
                selected_sections.append(random.choice(remaining_sections))
            
            # Enroll the student in each selected section
            for section in selected_sections:
                enrollment = StudentEnrollment(
                    student_id=student.id,
                    section_id=section.id,
                    is_active=True
                )
                db.session.add(enrollment)
                try:
                    db.session.commit()
                    enrollments_created += 1
                    print(f"Enrolled student: {student.first_name} {student.last_name} in {section.name}")
                except IntegrityError:
                    db.session.rollback()
                    print(f"Couldn't enroll student {student.first_name} {student.last_name} in {section.name} - already enrolled")
        
        # Create assignments and questions
        print("\nCreating assignments and questions...")
        section_assignments = create_assignments_and_questions(sections, teachers)
        
        # Print summary
        assignment_count = sum(len(assignments) for assignments in section_assignments.values())
        question_count = AssignmentQuestion.query.count()
        
        print(f"\nCreated {len(teachers)} teachers")
        print(f"Created {len(sections)} sections")
        print(f"Created {student_count} students")
        print(f"Created {assignment_count} assignments")
        print(f"Added {question_count} questions to assignments")
        print(f"Created {enrollments_created} enrollments (approx. 3 sections per student)")
        print(f"Each student is enrolled in approximately 3 different sections")

def create_assignments_and_questions(sections, teachers):
    """Create assignments and questions for each section"""
    section_assignments = {}
    
    # Choose a subset of subjects that match our sections
    section_topics = {section.name.split(' - ')[0]: section for section in sections}
    
    # For each section, create 3 assignments
    for section in sections:
        print(f"\nCreating assignments for section: {section.name}")
        section_topic = section.name.split(' - ')[0]
        
        # Get the teacher for this section
        teacher = next((t for t in teachers if t.id == section.creator_id), None)
        if not teacher:
            print(f"  Error: Could not find teacher for section {section.name}")
            continue
        
        # Get questions for this topic or use Database Fundamentals as fallback
        topic_questions = SQL_QUESTIONS.get(section_topic, SQL_QUESTIONS["Database Fundamentals"])
        
        # Create 3 assignments for this section
        section_assignments[section.id] = []
        for i in range(3):
            # Make assignment name unique for each teacher
            assignment_name = f"Assignment {i+1}: {section_topic} Practice (by {teacher.first_name} {teacher.last_name})"
            
            # Create the assignment
            assignment = Assignment(
                title=assignment_name,
                description=f"Practice your {section_topic} skills with these questions. Created by {teacher.first_name} {teacher.last_name}.",
                creator_id=teacher.id,
                due_date=datetime.utcnow() + timedelta(days=14 + i*7)  # Due in 2-4 weeks
            )
            db.session.add(assignment)
            
            try:
                db.session.commit()
                print(f"  Created assignment: {assignment.title}")
                section_assignments[section.id].append(assignment)
                
                # Create the section assignment link
                section_assignment = SectionAssignment(
                    section_id=section.id,
                    assignment_id=assignment.id
                )
                db.session.add(section_assignment)
                db.session.commit()
                
                # Create 3 questions for this assignment
                # Use modulo to cycle through the available questions if we need more than are available
                for j in range(3):
                    question_data = topic_questions[j % len(topic_questions)].copy()  # Create a copy to modify
                    
                    # Make the question unique by adding assignment, question numbers, and teacher name
                    unique_suffix = f" (Assignment {i+1}.{j+1} by {teacher.first_name} {teacher.last_name})"
                    question_data["title"] = question_data["title"] + unique_suffix
                    question_data["description"] = question_data["description"] + f"\n\nQuestion {j+1} of Assignment {i+1}. Created by {teacher.first_name} {teacher.last_name}."
                    
                    # Create the question (now it will always be unique due to unique title)
                    question = Question(
                        title=question_data["title"],
                        description=question_data["description"],
                        question_type=question_data["question_type"],
                        difficulty=question_data["difficulty"],
                        correct_answer=question_data["correct_answer"],
                        sample_db_schema=question_data["sample_db_schema"],
                        db_type=question_data["db_type"],
                mysql_db_name=question_data.get("mysql_db_name"),
                        author_id=teacher.id
                    )
                    db.session.add(question)
                    db.session.commit()
                    print(f"    Created question: {question.title}")
                    
                    # Link question to assignment with a score
                    assignment_question = AssignmentQuestion(
                        assignment_id=assignment.id,
                        question_id=question.id,
                        order=j+1,
                        score=10 * (j+1)  # Questions worth 10, 20, 30 points respectively
                    )
                    db.session.add(assignment_question)
                    db.session.commit()
                    print(f"    Added question to assignment with score: {assignment_question.score}")
                
            except IntegrityError as e:
                db.session.rollback()
                print(f"  Error creating assignment: {str(e)}")
                continue
    
    return section_assignments

if __name__ == "__main__":
    create_dummy_data() 