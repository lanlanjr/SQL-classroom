-- Simple test schema for SQL Classroom (without CREATE DATABASE/USE)
-- This version is compatible with the SQL Classroom import system

CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INT
);

CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    credits INT DEFAULT 3
);

CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    grade VARCHAR(2),
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

INSERT INTO students (name, email, age) VALUES
('John Doe', 'john@example.com', 20),
('Jane Smith', 'jane@example.com', 19),
('Bob Johnson', 'bob@example.com', 21);

INSERT INTO courses (title, credits) VALUES
('Introduction to Programming', 4),
('Database Systems', 3),
('Web Development', 3);

INSERT INTO enrollments (student_id, course_id, grade) VALUES
(1, 1, 'A'),
(1, 2, 'B+'),
(2, 1, 'A-'),
(2, 3, 'A'),
(3, 2, 'B');
