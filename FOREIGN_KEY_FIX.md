# Foreign Key Reference Fix Documentation

## Problem

When importing schemas with foreign key constraints (like `test_schema.sql`), the system was encountering errors:

1. **Error creating table**: `(1824, "Failed to open the referenced table 'students'")`
2. **Table not found errors**: `(1146, "Table 'sql_classroom.schema_1_21_enrollmentsxyx' doesn't exist")`

## Root Causes

### 1. Foreign Key References Not Prefixed
The `modify_create_table_statement()` function was only modifying the table name in the `CREATE TABLE` part, but not updating the foreign key references within the table definition.

**Before:**
```sql
CREATE TABLE `schema_1_21_enrollments` (
    student_id INT,
    course_id INT,
    grade VARCHAR(2),
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id),      -- ❌ Not prefixed
    FOREIGN KEY (course_id) REFERENCES courses(id)        -- ❌ Not prefixed
);
```

**After:**
```sql
CREATE TABLE `schema_1_21_enrollments` (
    student_id INT,
    course_id INT,
    grade VARCHAR(2),
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES `schema_1_21_students` (id),  -- ✅ Prefixed
    FOREIGN KEY (course_id) REFERENCES `schema_1_21_courses` (id)     -- ✅ Prefixed
);
```

### 2. Foreign Key Constraints Preventing Table Drops
When dropping tables during schema cleanup, foreign key constraints prevented proper cleanup because MySQL requires dropping child tables before parent tables.

## Solutions Implemented

### 1. Enhanced CREATE TABLE Statement Modification
**File:** `app/utils.py` - `modify_create_table_statement()` function

```python
def modify_create_table_statement(statement, table_prefix):
    """
    Modify a CREATE TABLE statement to use a prefixed table name and update foreign key references.
    """
    # ... existing table name modification logic ...
    
    # NEW: Also update foreign key references to use prefixed table names
    # Pattern for FOREIGN KEY ... REFERENCES table_name(column)
    fk_pattern = r'REFERENCES\s+`?([^`\s(]+)`?\s*\('
    
    def replace_fk_reference(match):
        referenced_table = match.group(1)
        prefixed_referenced_table = f"{table_prefix}{referenced_table}"
        return f'REFERENCES `{prefixed_referenced_table}` ('
    
    new_statement = re.sub(fk_pattern, replace_fk_reference, new_statement, flags=re.IGNORECASE)
    
    return new_statement
```

### 2. Improved Table Dropping with Foreign Key Handling
**File:** `app/routes/teacher.py` - `use_schema()` and `delete_schema()` functions

```python
# Before dropping tables, disable foreign key checks
if tables_to_drop:
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
# Drop tables in any order
for table in tables_to_drop:
    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
    
# Re-enable foreign key checks
if tables_to_drop:
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
```

## Benefits

1. **Complete Foreign Key Support**: Schemas with foreign key relationships now import correctly
2. **Proper Table Cleanup**: All tables drop successfully regardless of foreign key constraints
3. **Maintains Data Integrity**: Foreign key checks are only temporarily disabled during cleanup
4. **Performance Optimization**: Foreign key checks are only disabled when needed

## Test Case

The `test_schema.sql` file now imports successfully:
- `students` table is created with prefix: `schema_1_21_students`
- `courses` table is created with prefix: `schema_1_21_courses`  
- `enrollments` table is created with prefix: `schema_1_21_enrollments`
- Foreign keys properly reference the prefixed table names
- All data inserts work correctly

## Usage

1. Import the `test_schema.sql` file through the teacher interface
2. Deploy the schema using the "Use Schema" button
3. All tables should be created successfully with proper foreign key relationships
4. Schema deletion will now cleanly remove all tables

## Files Modified

1. `app/utils.py` - Enhanced `modify_create_table_statement()`
2. `app/routes/teacher.py` - Updated `use_schema()` and `delete_schema()` functions

The fix ensures that complex schemas with foreign key relationships work seamlessly in the SQL Classroom system.
