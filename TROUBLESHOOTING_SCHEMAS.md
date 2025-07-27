# Troubleshooting Imported Schemas - SQL Classroom

## Common Issue: "Error executing query: Server error: 400"

If you're getting a 400 error when creating questions with imported schemas, follow this step-by-step troubleshooting guide:

### Step 1: Verify Schema Import Status

1. **Go to Import Schema page** (`/teacher/import_schema`)
2. **Check your imported schemas table**:
   - Look for your schema in the list
   - Check if it shows "Use" button or if tables are created

### Step 2: Deploy Your Schema

If you see a "Use" button next to your schema:

1. **Click the "Use" button** - This deploys your schema to the database
2. **Wait for success message** - Should show "Schema deployed successfully!"
3. **Verify deployment** - The button should change or show deployment status

### Step 3: Verify Tables Were Created

After deployment, check that tables exist:

1. **Go to Schema Monitor** (if you're an admin): `/teacher/admin/schema-monitor`
2. **Or use debug route**: `/teacher/debug/question/[QUESTION_ID]` (after creating the question)

### Step 4: Create Question with Deployed Schema

1. **Go to New Question page**
2. **Select "Imported Schema" as database type**
3. **Choose your schema from dropdown** - Should NOT show "⚠️ Not Deployed"
4. **Test your query** using the preview feature

### Step 5: Test Query Format

When testing queries with imported schemas, remember:

#### ✅ Correct Format:
```sql
-- Use original table names (system will automatically add prefixes)
SELECT * FROM students;
SELECT * FROM courses;
```

#### ❌ Incorrect Format:
```sql
-- Don't use prefixed names manually
SELECT * FROM schema_1_5_students;  -- Wrong!
```

The system automatically converts `students` to `schema_1_5_students` internally.

## Detailed Troubleshooting Steps

### Check 1: Schema Import Record
```sql
-- Admin can check in database
SELECT id, name, active_schema_name, created_by 
FROM schema_imports 
WHERE created_by = [YOUR_USER_ID];
```

### Check 2: Tables in Database
```sql
-- Admin can check actual tables
SHOW TABLES LIKE 'schema_%';
```

### Check 3: Question Configuration
Use the debug route: `/teacher/debug/question/[QUESTION_ID]`

This returns JSON with:
- Question details
- Schema import status  
- Database table information
- Any errors

### Check 4: Permissions
```sql
-- Check student user permissions
SHOW GRANTS FOR 'sql_student'@'localhost';
```

## Common Causes and Solutions

### Cause 1: Schema Not Deployed
**Symptoms**: Schema exists in import list but no "Use" button clicked
**Solution**: Click "Use" button to deploy schema

### Cause 2: Import Failed Silently
**Symptoms**: Schema shows as imported but no tables created
**Solution**: Re-import the schema file, check for SQL syntax errors

### Cause 3: Table Name Conflicts
**Symptoms**: Some tables created but not all
**Solution**: Check SQL file for reserved words or special characters

### Cause 4: Permission Issues
**Symptoms**: Query works for teacher but fails for students
**Solution**: Check if sql_student user has SELECT permissions on prefixed tables

### Cause 5: Connection Issues
**Symptoms**: Database connection errors
**Solution**: Verify MySQL credentials in environment variables

## Debug Information to Collect

When reporting issues, please provide:

1. **Schema Import Details**:
   - Schema name
   - Import timestamp
   - File size/content preview

2. **Question Details**:
   - Question ID
   - Database type selection
   - Selected schema

3. **Error Details**:
   - Full error message
   - Browser console errors
   - Server logs if available

4. **Test Query**:
   - The SQL query being tested
   - Expected vs actual behavior

## Environment Check

Verify these environment variables are set correctly:
```bash
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=admin
MYSQL_PORT=3306
```

## Quick Fix Commands (Admin)

### Reset Schema Deployment:
```python
# In Python console
from app import db
from app.models.schema_import import SchemaImport

schema = SchemaImport.query.filter_by(name='YOUR_SCHEMA_NAME').first()
schema.active_schema_name = None
db.session.commit()
```

### Clean Up Tables:
```sql
-- Drop all tables for a specific schema
DROP TABLE IF EXISTS schema_1_5_students;
DROP TABLE IF EXISTS schema_1_5_courses;
-- Replace with actual table names
```

### Grant Permissions:
```sql
-- Grant permissions to student user
GRANT SELECT ON sql_classroom.* TO 'sql_student'@'localhost';
FLUSH PRIVILEGES;
```

## Prevention Tips

1. **Always test schemas** after import using "Use" button
2. **Verify table creation** before creating questions
3. **Use simple table names** without special characters
4. **Test queries** using the preview feature
5. **Keep schema files clean** with proper SQL syntax

## Still Having Issues?

If none of these steps resolve the issue:

1. **Check server logs** for detailed error messages
2. **Try with a simple test schema** (single table)
3. **Verify MySQL service is running** and accessible
4. **Contact system administrator** with debug information

Remember: The table prefixing system is designed to work transparently. You should write queries as if the tables have their original names, and the system handles the prefixing automatically.
