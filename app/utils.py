"""
Utility functions for the SQL Classroom application.
"""

def validate_dql_only_query(query):
    """
    Validate that the query contains only DQL (Data Query Language) commands.
    This restricts users to SELECT statements and related information queries only.
    
    Forbidden operations:
    - DDL (Data Definition Language): CREATE, DROP, ALTER, TRUNCATE, RENAME
    - DML (Data Manipulation Language): INSERT, UPDATE, DELETE  
    - DCL (Data Control Language): GRANT, REVOKE, CREATE USER, DROP USER
    - TCL (Transaction Control Language): COMMIT, ROLLBACK, SAVEPOINT
    - File operations and other potentially dangerous commands
    
    Args:
        query (str): The SQL query to validate
        
    Returns:
        bool: True if query is valid
        
    Raises:
        ValueError: If query contains forbidden operations
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    query_upper = query.upper().strip()
    
    # Allow specific DQL and information commands only
    allowed_starts = [
        'SELECT', 
        'SHOW TABLES',
        'SHOW COLUMNS',
        'SHOW FIELDS', 
        'SHOW DATABASES',
        'SHOW SCHEMAS',
        'DESCRIBE',
        'DESC',
        'EXPLAIN',
        'SHOW CREATE TABLE',
        'SHOW INDEX',
        'SHOW INDEXES',
        'SHOW KEYS'
    ]
    
    # Check if query starts with any allowed command
    is_allowed = any(query_upper.startswith(cmd) for cmd in allowed_starts)
    if not is_allowed:
        raise ValueError("Only SELECT and information queries are allowed. DDL, DML, DCL, and TCL operations are forbidden.")
    
    # Comprehensive list of forbidden keywords
    # DDL - Data Definition Language
    ddl_keywords = [
        'CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'RENAME'
    ]
    
    # DML - Data Manipulation Language  
    dml_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'REPLACE', 'MERGE'
    ]
    
    # DCL - Data Control Language
    dcl_keywords = [
        'GRANT', 'REVOKE', 'DENY'
    ]
    
    # TCL - Transaction Control Language
    tcl_keywords = [
        'COMMIT', 'ROLLBACK', 'SAVEPOINT', 'SET TRANSACTION', 'BEGIN', 'START TRANSACTION'
    ]
    
    # Administrative and system commands
    admin_keywords = [
        'USE', 'SET', 'RESET', 'FLUSH', 'KILL', 'SHUTDOWN', 'RESTART'
    ]
    
    # User and security management
    user_keywords = [
        'CREATE USER', 'DROP USER', 'ALTER USER', 'RENAME USER', 'SET PASSWORD'
    ]
    
    # Stored procedures, functions, triggers
    procedure_keywords = [
        'PROCEDURE', 'FUNCTION', 'TRIGGER', 'EVENT', 'CALL'
    ]
    
    # Locking and file operations
    lock_file_keywords = [
        'LOCK', 'UNLOCK', 'LOAD', 'LOAD DATA', 'SELECT INTO OUTFILE', 
        'INTO OUTFILE', 'INTO DUMPFILE', 'LOAD_FILE'
    ]
    
    # Database and schema operations
    schema_keywords = [
        'CREATE DATABASE', 'CREATE SCHEMA', 'DROP DATABASE', 'DROP SCHEMA',
        'ALTER DATABASE', 'ALTER SCHEMA'
    ]
    
    # Combine all forbidden keywords
    forbidden_keywords = (
        ddl_keywords + dml_keywords + dcl_keywords + tcl_keywords + 
        admin_keywords + user_keywords + procedure_keywords + 
        lock_file_keywords + schema_keywords
    )
    
    # Split query into words and check for forbidden keywords
    query_words = set(query_upper.split())
    for keyword in forbidden_keywords:
        if keyword in query_words:
            # Make exception for 'CREATE' in 'SHOW CREATE TABLE'
            if keyword == 'CREATE' and 'SHOW CREATE TABLE' in query_upper:
                continue
            raise ValueError(f"Query contains forbidden keyword: {keyword}. Only DQL (SELECT and information queries) are allowed.")
    
    # Check for multi-word forbidden phrases
    forbidden_phrases = [
        'INTO OUTFILE', 'INTO DUMPFILE', 'LOAD DATA', 'SELECT INTO OUTFILE',
        'CREATE USER', 'DROP USER', 'ALTER USER', 'RENAME USER', 'SET PASSWORD',
        'CREATE DATABASE', 'CREATE SCHEMA', 'DROP DATABASE', 'DROP SCHEMA', 
        'ALTER DATABASE', 'ALTER SCHEMA', 'START TRANSACTION', 'SET TRANSACTION'
    ]
    
    for phrase in forbidden_phrases:
        if phrase in query_upper:
            # Make exception for 'CREATE' in 'SHOW CREATE TABLE'
            if phrase == 'CREATE TABLE' and 'SHOW CREATE TABLE' in query_upper:
                continue
            raise ValueError(f"Query contains forbidden operation: {phrase}. Only DQL (SELECT and information queries) are allowed.")
    
    # Additional security checks
    if '--' in query:
        raise ValueError("SQL comments (--) are not allowed for security reasons")
    
    if '#' in query:
        raise ValueError("SQL comments (#) are not allowed for security reasons")
    
    if '/*' in query or '*/' in query:
        raise ValueError("Multi-line SQL comments (/* */) are not allowed for security reasons")
    
    # Check for semicolon followed by more commands (prevent command injection)
    semicolon_parts = query.split(';')
    if len(semicolon_parts) > 2:  # Allow one semicolon at the end
        raise ValueError("Multiple SQL statements are not allowed")
    
    # If there are two parts, the second should be empty or whitespace (trailing semicolon)
    if len(semicolon_parts) == 2 and semicolon_parts[1].strip():
        raise ValueError("Multiple SQL statements are not allowed")
    
    # Prevent access to sensitive system schemas
    sensitive_schemas = [
        'INFORMATION_SCHEMA', 'PERFORMANCE_SCHEMA', 'SYS', 'MYSQL'
    ]
    
    for schema in sensitive_schemas:
        if schema in query_upper and 'FROM ' + schema in query_upper:
            raise ValueError(f"Access to {schema} is restricted for security reasons")
    
    return True
