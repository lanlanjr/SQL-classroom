# Database Management in SQL Classroom

## Overview

SQL Classroom is designed to work with SQL servers that have database creation limitations. Instead of creating new databases for each imported schema, the application uses a **table prefixing strategy** within a single shared database.

## How It Works

### Single Database Architecture

All imported schemas are deployed to the main `sql_classroom` database using unique table prefixes. This approach:

- **Complies with server restrictions** that limit database creation
- **Maintains isolation** between different teachers' schemas
- **Simplifies permission management** 
- **Reduces resource overhead**

### Table Prefixing System

When you import a schema, tables are created with unique prefixes:

```
Original table: customers
Prefixed table: schema_1_5_customers
```

Where:
- `1` = Teacher ID
- `5` = Schema ID  
- `customers` = Original table name

### Database Types Supported

1. **In-Memory SQLite** (`sample_db_schema`)
   - Creates temporary SQLite databases for simple exercises
   - Ideal for basic SQL learning

2. **Existing MySQL Databases** (`mysql_db_name`)
   - Points to pre-existing databases like `classicmodels`
   - Uses the database name directly

3. **Imported Schemas** (`imported_schema`)
   - Deploys custom schemas to `sql_classroom` database
   - Uses table prefixing for isolation

## Benefits of This Approach

### ✅ Server Compatibility
- Works with hosting providers that restrict database creation
- No need for database creation privileges
- Single database simplifies backup and maintenance

### ✅ Resource Efficiency
- Lower memory footprint
- Reduced connection overhead
- Simplified database administration

### ✅ Security & Isolation
- Each teacher's tables are isolated by prefixes
- Student users get SELECT-only permissions on relevant tables
- No cross-contamination between schemas

### ✅ Management Simplicity
- All schemas visible in one database
- Easy to monitor and maintain
- Consistent permission model

## Schema Import Process

1. **Upload SQL File**: Teacher uploads a `.sql` schema file
2. **Parse Statements**: System parses CREATE TABLE and INSERT statements
3. **Apply Prefixes**: Table names get unique prefixes based on teacher/schema IDs
4. **Deploy Tables**: Tables are created in the `sql_classroom` database
5. **Set Permissions**: Student users get SELECT permissions on new tables
6. **Update References**: All foreign key and INSERT references are updated

## Example Schema Transformation

### Original Schema:
```sql
CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    id INT PRIMARY KEY,
    title VARCHAR(100)
);

INSERT INTO students VALUES (1, 'John Doe');
```

### After Import (Teacher ID: 1, Schema ID: 5):
```sql
CREATE TABLE `schema_1_5_students` (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE `schema_1_5_courses` (
    id INT PRIMARY KEY,
    title VARCHAR(100)
);

INSERT INTO `schema_1_5_students` VALUES (1, 'John Doe');
```

## Best Practices

### For Teachers:
1. **Use descriptive schema names** to easily identify your imports
2. **Keep schemas focused** - one topic per schema for better organization
3. **Test your schemas** after import to ensure all references work correctly
4. **Clean up unused schemas** to keep the database tidy

### For System Administrators:
1. **Monitor table count** in the `sql_classroom` database
2. **Set up regular cleanup** for abandoned schemas
3. **Monitor disk space** usage
4. **Backup the shared database** regularly

## Troubleshooting

### Common Issues:

**"Schema not found" errors:**
- Ensure the schema was successfully imported and deployed
- Check that the `active_schema_name` field is set in the database

**Permission errors:**
- Verify that the `sql_student` user has SELECT permissions on prefixed tables
- Check MySQL user privileges with `SHOW GRANTS FOR 'sql_student'@'localhost'`

**Table reference errors:**
- Ensure all table references in your SQL file use consistent naming
- Foreign key references must match exactly

### Manual Cleanup:

To manually clean up a schema's tables:

```sql
-- List all tables with a specific prefix
SHOW TABLES LIKE 'schema_1_5_%';

-- Drop tables with prefix (replace with actual prefix)
DROP TABLE IF EXISTS schema_1_5_students;
DROP TABLE IF EXISTS schema_1_5_courses;
```

## Alternative Solutions Considered

### ❌ Multiple Databases
- **Problem**: Server restrictions prevent database creation
- **Issues**: Permission complexity, resource overhead

### ❌ Schema-based Separation
- **Problem**: MySQL's schema = database concept
- **Issues**: Same limitation as multiple databases

### ✅ Table Prefixing (Current Solution)
- **Benefits**: Works within server constraints
- **Advantages**: Simple, efficient, secure

This table prefixing approach provides the best balance of functionality, security, and compatibility with server limitations.
