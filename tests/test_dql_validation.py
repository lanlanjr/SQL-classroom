#!/usr/bin/env python3
"""
Test script to validate the DQL-only query restrictions.
This script tests the validate_dql_only_query function to ensure
it properly restricts SQL queries to only DQL operations.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the validation function
from app.utils import validate_dql_only_query

def test_valid_queries():
    """Test queries that should be allowed."""
    valid_queries = [
        "SELECT * FROM users",
        "SELECT id, name FROM customers WHERE age > 18",
        "SELECT COUNT(*) FROM orders",
        "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id",
        "SHOW TABLES",
        "SHOW DATABASES", 
        "SHOW COLUMNS FROM users",
        "DESCRIBE users",
        "DESC orders",
        "EXPLAIN SELECT * FROM users",
        "SHOW CREATE TABLE customers",
        "SHOW INDEX FROM users",
        "SHOW INDEXES FROM orders",
        "SHOW KEYS FROM products"
    ]
    
    print("Testing valid queries:")
    for query in valid_queries:
        try:
            validate_dql_only_query(query)
            print(f"✓ PASS: {query}")
        except Exception as e:
            print(f"✗ FAIL: {query} - {e}")
    print()

def test_invalid_queries():
    """Test queries that should be blocked."""
    invalid_queries = [
        # DDL - Data Definition Language
        "CREATE TABLE test (id INT)",
        "DROP TABLE users",
        "ALTER TABLE users ADD COLUMN email VARCHAR(100)",
        "TRUNCATE TABLE orders",
        "RENAME TABLE old_name TO new_name",
        
        # DML - Data Manipulation Language
        "INSERT INTO users (name) VALUES ('John')",
        "UPDATE users SET name = 'Jane' WHERE id = 1",
        "DELETE FROM users WHERE id = 1",
        "REPLACE INTO users (id, name) VALUES (1, 'Bob')",
        
        # DCL - Data Control Language
        "GRANT SELECT ON users TO student",
        "REVOKE SELECT ON users FROM student",
        "DENY SELECT ON users TO guest",
        
        # TCL - Transaction Control Language
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT sp1",
        "BEGIN TRANSACTION",
        "START TRANSACTION",
        
        # Administrative commands
        "USE database_name",
        "SET @var = 1",
        "FLUSH PRIVILEGES",
        "KILL 123",
        
        # File operations
        "SELECT * FROM users INTO OUTFILE '/tmp/users.txt'",
        "LOAD DATA INFILE '/tmp/data.csv' INTO TABLE users",
        
        # Stored procedures and functions
        "CALL procedure_name()",
        "CREATE PROCEDURE test() BEGIN SELECT 1; END",
        "CREATE FUNCTION test() RETURNS INT RETURN 1",
        
        # Comments (security risk)
        "SELECT * FROM users -- comment",
        "SELECT * FROM users # comment",
        "SELECT * FROM users /* comment */",
        
        # Multiple statements
        "SELECT * FROM users; DROP TABLE users;",
        
        # System schema access
        "SELECT * FROM INFORMATION_SCHEMA.TABLES",
        "SELECT * FROM mysql.user"
    ]
    
    print("Testing invalid queries (should be blocked):")
    for query in invalid_queries:
        try:
            validate_dql_only_query(query)
            print(f"✗ FAIL: Query should have been blocked: {query}")
        except Exception as e:
            print(f"✓ PASS: Correctly blocked: {query[:50]}{'...' if len(query) > 50 else ''}")
    print()

def test_edge_cases():
    """Test edge cases and special scenarios."""
    edge_cases = [
        ("", "Empty query"),
        ("   ", "Whitespace only"),
        ("SHOW CREATE TABLE users", "Should allow SHOW CREATE TABLE"),
        ("select * from users", "Lowercase should work"),
        ("SELECT * FROM users;", "Trailing semicolon should be allowed"),
    ]
    
    print("Testing edge cases:")
    for query, description in edge_cases:
        try:
            if query.strip() == "" or query.strip() == "   ":
                # These should fail
                validate_dql_only_query(query)
                print(f"✗ FAIL: {description} - should have been rejected")
            else:
                validate_dql_only_query(query)
                print(f"✓ PASS: {description}")
        except Exception as e:
            if query.strip() == "" or query.strip() == "   ":
                print(f"✓ PASS: {description} - correctly rejected")
            else:
                print(f"✗ FAIL: {description} - {e}")
    print()

if __name__ == "__main__":
    print("SQL Classroom - DQL Validation Test")
    print("=" * 50)
    
    test_valid_queries()
    test_invalid_queries()
    test_edge_cases()
    
    print("Test completed!")
