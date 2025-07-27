"""
Utility functions for the SQL Classroom application.
"""

import logging

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
    
    # for schema in sensitive_schemas:
    #     if schema in query_upper and 'FROM ' + schema in query_upper:
    #         raise ValueError(f"Access to {schema} is restricted for security reasons")
    
    return True


def generate_schema_prefix(user_id, schema_id):
    """
    Generate a consistent table prefix for imported schemas.
    
    Args:
        user_id (int): The ID of the user who owns the schema
        schema_id (int): The ID of the schema
        
    Returns:
        str: A unique table prefix for this user's schema
    """
    return f"schema_{user_id}_{schema_id}_"


def get_prefixed_table_name(prefix, table_name):
    """
    Get the full prefixed table name.
    
    Args:
        prefix (str): The table prefix
        table_name (str): The original table name
        
    Returns:
        str: The prefixed table name
    """
    # Remove backticks if present
    clean_table_name = table_name.strip('`')
    return f"{prefix}{clean_table_name}"


def parse_schema_statements(schema_content):
    """
    Parse SQL schema content into individual statements.
    Handles phpMyAdmin dumps and complex SQL files with comments.
    
    Args:
        schema_content (str): The raw SQL schema content
        
    Returns:
        list: List of SQL statements
    """
    if not schema_content:
        return []
    
    # Remove MySQL-specific commands that we don't need
    lines = schema_content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Skip comments and MySQL-specific commands
        if (stripped.startswith('--') or 
            stripped.startswith('/*') or
            stripped.startswith('*/') or
            stripped.startswith('SET ') or
            stripped.startswith('START TRANSACTION') or
            stripped.startswith('COMMIT') or
            stripped.startswith('USE ') or
            stripped.startswith('/*!') or
            stripped == '' or
            'phpMyAdmin' in stripped):
            continue
            
        cleaned_lines.append(line)
    
    # Join back and split by semicolons
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Split by semicolon but be smarter about it
    statements = []
    current_statement = ""
    in_string = False
    
    i = 0
    while i < len(cleaned_content):
        char = cleaned_content[i]
        
        if char == "'" and (i == 0 or cleaned_content[i-1] != '\\'):
            in_string = not in_string
        elif char == ';' and not in_string:
            # End of statement
            stmt = current_statement.strip()
            if stmt and not stmt.startswith('--'):
                # Filter out CREATE DATABASE and USE statements
                stmt_upper = stmt.upper().strip()
                if (not stmt_upper.startswith('CREATE DATABASE') and 
                    not stmt_upper.startswith('CREATE SCHEMA') and
                    not stmt_upper.startswith('USE ')):
                    statements.append(stmt)
            current_statement = ""
            i += 1
            continue
            
        current_statement += char
        i += 1
    
    # Add final statement if it doesn't end with semicolon
    final_stmt = current_statement.strip()
    if final_stmt and not final_stmt.startswith('--'):
        # Filter out CREATE DATABASE and USE statements for final statement too
        stmt_upper = final_stmt.upper().strip()
        if (not stmt_upper.startswith('CREATE DATABASE') and 
            not stmt_upper.startswith('CREATE SCHEMA') and
            not stmt_upper.startswith('USE ')):
            statements.append(final_stmt)
    
    return statements


def modify_create_table_statement(statement, table_prefix):
    """
    Modify a CREATE TABLE statement to use a prefixed table name and update foreign key references.
    
    Args:
        statement (str): The original CREATE TABLE statement
        table_prefix (str): The prefix to add to the table name
        
    Returns:
        str: The modified statement with prefixed table name and foreign key references
    """
    if not statement.upper().strip().startswith('CREATE TABLE'):
        return statement
    
    import re
    
    # Use regex to find and replace the table name after CREATE TABLE
    pattern = r'CREATE\s+TABLE\s+`?([^`\s(]+)`?'
    match = re.search(pattern, statement, re.IGNORECASE)
    
    if match:
        original_table = match.group(1)
        prefixed_table = f"{table_prefix}{original_table}"
        
        # Replace the table name in the original statement
        new_statement = re.sub(
            pattern,
            f'CREATE TABLE `{prefixed_table}`',
            statement,
            flags=re.IGNORECASE
        )
        
        # Also update foreign key references to use prefixed table names
        # Pattern for FOREIGN KEY ... REFERENCES table_name(column)
        fk_pattern = r'REFERENCES\s+`?([^`\s(]+)`?\s*\('
        
        def replace_fk_reference(match):
            referenced_table = match.group(1)
            prefixed_referenced_table = f"{table_prefix}{referenced_table}"
            return f'REFERENCES `{prefixed_referenced_table}` ('
        
        new_statement = re.sub(fk_pattern, replace_fk_reference, new_statement, flags=re.IGNORECASE)
        
        return new_statement
    
    return statement


def process_show_tables_result_for_schema(columns, data, database_name, user_id, section_id=None):
    """
    Process SHOW TABLES result when executed on an imported schema database.
    Filters and cleans up table names to show only the imported schema tables
    without their prefixes.
    
    Args:
        columns (list): Column names from the SHOW TABLES query
        data (list): Data rows from the SHOW TABLES query  
        database_name (str): The database name being queried
        user_id (int): The user ID (for finding their schemas)
        section_id (int, optional): The section ID for student context
        
    Returns:
        tuple: (modified_columns, modified_data) or (columns, data) if no schema match
    """
    # Only process if database is sql_classroom (where imported schemas are stored)
    if database_name != 'sql_classroom':
        return columns, data
    
    # Import here to avoid circular imports
    from app.models.schema_import import SchemaImport
    from app.models.section import Section
    from app.models.user import User
    
    # Extract table names from the data
    table_names = [row[0] for row in data]
    
    # If section_id is provided, this is a student query - find schemas from the section's teacher
    if section_id:
        try:
            section = Section.query.get(section_id)
            if section and section.creator_id:
                # Get schemas created by the section's teacher
                teacher_schemas = SchemaImport.query.filter_by(created_by=section.creator_id).filter(
                    SchemaImport.active_schema_name.isnot(None)
                ).all()
                
                # Find matching schema tables
                matching_schema, matching_tables = _find_matching_schema_tables(teacher_schemas, table_names)
                
                if matching_schema and matching_tables:
                    return _format_show_tables_result(matching_schema, matching_tables)
        except Exception as e:
            logging.error(f"Error processing student schema context: {e}")
    
    # Fall back to user-based lookup (for teachers)
    active_schemas = SchemaImport.query.filter_by(created_by=user_id).filter(
        SchemaImport.active_schema_name.isnot(None)
    ).all()
    
    if not active_schemas:
        return columns, data
    
    # Find matching schema tables
    matching_schema, matching_tables = _find_matching_schema_tables(active_schemas, table_names)
    
    if matching_schema and matching_tables:
        return _format_show_tables_result(matching_schema, matching_tables)
    
    # If no schema match found, return original results
    return columns, data


def _find_matching_schema_tables(schemas, table_names):
    """
    Helper function to find matching schema tables from a list of schemas.
    
    Args:
        schemas (list): List of SchemaImport objects
        table_names (list): List of table names from SHOW TABLES
        
    Returns:
        tuple: (matching_schema, matching_tables) or (None, [])
    """
    for schema in schemas:
        prefix = schema.active_schema_name
        if prefix:
            schema_tables = [table for table in table_names if table.startswith(prefix)]
            if schema_tables:
                return schema, schema_tables
    return None, []


def _format_show_tables_result(matching_schema, matching_tables):
    """
    Helper function to format the SHOW TABLES result for a matching schema.
    
    Args:
        matching_schema: The SchemaImport object that matched
        matching_tables (list): List of table names with prefixes
        
    Returns:
        tuple: (formatted_columns, formatted_data)
    """
    # Remove prefix from table names
    clean_table_names = []
    prefix = matching_schema.active_schema_name
    
    for table in matching_tables:
        if table.startswith(prefix):
            # Remove the prefix (e.g., "schema_1_7_" from "schema_1_7_authors")
            clean_name = table[len(prefix):]
            clean_table_names.append(clean_name)
        else:
            clean_table_names.append(table)
    
    # Create new column header - use simple "Tables" for cleaner output
    new_column_name = "Tables"
    
    # Create new data with clean table names
    new_data = [[table] for table in clean_table_names]
    
    return [new_column_name], new_data


def is_show_tables_query(query):
    """
    Check if a query is a SHOW TABLES command.
    
    Args:
        query (str): The SQL query to check
        
    Returns:
        bool: True if this is a SHOW TABLES query
    """
    if not query:
        return False
    
    query_upper = query.upper().strip()
    return query_upper.startswith('SHOW TABLES')


def rewrite_query_for_schema(query, schema_content, table_prefix):
    """
    Rewrite a SQL query to use prefixed table names for imported schemas.
    
    Args:
        query (str): The original SQL query
        schema_content (str): The schema content to extract table names from
        table_prefix (str): The prefix to add to table names (e.g., "schema_1_23_")
        
    Returns:
        str: The rewritten query with prefixed table names
    """
    if not query or not schema_content or not table_prefix:
        return query
    
    # Extract table names from schema content
    table_names = []
    statements = parse_schema_statements(schema_content)
    
    for stmt in statements:
        if stmt.upper().strip().startswith('CREATE TABLE'):
            # Extract table name using the same logic as in import
            table_start = stmt.upper().find('TABLE') + 5
            table_part = stmt[table_start:].strip()
            table_name = table_part.split()[0].strip('`').rstrip('(').strip('`')
            table_names.append(table_name)
    
    logging.debug(f"Query rewriting - Found table names: {table_names}")
    logging.debug(f"Query rewriting - Original query: {query}")
    
    
    # Apply query rewriting
    import re
    modified_query = query
    for table_name in table_names:
        # First replace backticked table names: `tablename`
        backticked_pattern = r'`' + re.escape(table_name) + r'`'
        prefixed_table = f"{table_prefix}{table_name}"
        old_query = modified_query
        modified_query = re.sub(backticked_pattern, f"`{prefixed_table}`", modified_query, flags=re.IGNORECASE)
        if old_query != modified_query:
            logging.debug(f"Query rewriting - Replaced backticked '{table_name}' with '{prefixed_table}'")

        # Then replace non-backticked table names with word boundaries
        word_boundary_pattern = r'\b' + re.escape(table_name) + r'\b'
        old_query = modified_query
        modified_query = re.sub(word_boundary_pattern, f"`{prefixed_table}`", modified_query, flags=re.IGNORECASE)
        if old_query != modified_query:
            logging.debug(f"Query rewriting - Replaced non-backticked '{table_name}' with '{prefixed_table}'")

    logging.debug(f"Query rewriting - Final query: {modified_query}")
    return modified_query


def is_show_databases_query(query):
    """Check if the query is a SHOW DATABASES or SHOW SCHEMAS query."""
    query_upper = query.strip().upper()
    return query_upper.startswith('SHOW DATABASES') or query_upper.startswith('SHOW SCHEMAS')


def filter_show_databases_result(columns, rows):
    """Filter SHOW DATABASES result to only include allowed databases when configured."""
    from app.models import AllowedDatabase
    
    # Get allowed databases
    allowed_databases = AllowedDatabase.get_active_database_names()
    
    # If no allowed databases configured, return original results
    if not allowed_databases:
        return columns, rows
    
    # Filter the rows to only include allowed databases
    filtered_rows = []
    for row in rows:
        if row and len(row) > 0:
            database_name = row[0]  # Database name is typically the first column
            if database_name in allowed_databases:
                filtered_rows.append(row)
    
    return columns, filtered_rows


def filter_show_databases_result_for_user(columns, rows, user):
    """Filter SHOW DATABASES result to include allowed databases and user's imported schemas."""
    from app.models import AllowedDatabase
    from app.models.schema_import import SchemaImport
    
    available_databases = []
    
    # Get admin-allowed databases
    allowed_databases = AllowedDatabase.get_active_database_names()
    if allowed_databases:
        available_databases.extend(allowed_databases)
    
    # Add user's accessible schemas
    try:
        if user.role == 'teacher':
            # Teachers can access their own schemas
            user_schemas = SchemaImport.query.filter_by(created_by=user.id).filter(
                SchemaImport.active_schema_name.isnot(None)
            ).all()
        else:
            # Students can access schemas from their teachers (sections they're enrolled in)
            from app.models.user import StudentEnrollment
            from app.models.section import Section
            
            user_schemas = []
            # Get all sections the student is enrolled in
            enrollments = StudentEnrollment.query.filter_by(
                student_id=user.id, 
                is_active=True
            ).all()
            
            # Get all teachers from those sections
            teacher_ids = set()
            for enrollment in enrollments:
                section = Section.query.get(enrollment.section_id)
                if section:
                    teacher_ids.add(section.creator_id)
            
            # Get schemas from all those teachers
            if teacher_ids:
                user_schemas = SchemaImport.query.filter(
                    SchemaImport.created_by.in_(teacher_ids)
                ).filter(SchemaImport.active_schema_name.isnot(None)).all()
        
        # Add each schema's name as an available database option
        for schema in user_schemas:
            schema_name = schema.name
            if schema_name not in available_databases:
                available_databases.append(schema_name)
    except Exception as e:
        logging.error(f"Error checking user schemas: {e}")
    
    # If no databases are available, return original results (fallback)
    if not available_databases:
        return columns, rows
    
    # Filter the rows to only include available databases
    filtered_rows = []
    for row in rows:
        if row and len(row) > 0:
            database_name = row[0]  # Database name is typically the first column
            if database_name in available_databases:
                filtered_rows.append(row)
    
    # Also add schema names that aren't actual databases (they appear as virtual databases)
    for schema_name in available_databases:
        # Check if this schema name is not already in the results
        schema_already_exists = any(
            row and len(row) > 0 and row[0] == schema_name 
            for row in filtered_rows
        )
        if not schema_already_exists:
            # Add the schema name as a virtual database
            filtered_rows.append([schema_name])
    
    return columns, filtered_rows


def ensure_six_digit_auto_increment(table_name, engine):
    """
    Utility function to ensure a table has AUTO_INCREMENT starting from 100000
    for 6-digit IDs. This should be called after creating new tables.
    
    Args:
        table_name (str): Name of the table to update
        engine: SQLAlchemy engine instance
    """
    try:
        with engine.connect() as conn:
            # Get current max ID
            result = conn.execute(f"SELECT MAX(id) FROM {table_name}")
            max_id = result.scalar() or 0
            
            # Set AUTO_INCREMENT to the higher of current max+1 or 100000
            new_auto_increment = max(max_id + 1, 100000)
            
            # Update AUTO_INCREMENT
            conn.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = {new_auto_increment}")
            conn.commit()
            
            logging.info(f"Updated {table_name} AUTO_INCREMENT to {new_auto_increment}")
            
    except Exception as e:
        logging.error(f"Error updating {table_name} AUTO_INCREMENT: {str(e)}")


def get_six_digit_table_args():
    """
    Returns the standard table arguments for ensuring 6-digit IDs in new models.
    
    Returns:
        dict: Table arguments with mysql_auto_increment set to 100000
    """
    return {'mysql_auto_increment': 100000}
