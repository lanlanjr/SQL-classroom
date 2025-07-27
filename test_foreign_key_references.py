#!/usr/bin/env python3
"""
Test the foreign key reference fix in modify_create_table_statement
"""

import sys
import os

# Add the app directory to the path so we can import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils import modify_create_table_statement

def test_foreign_key_fix():
    print("=== Testing Foreign Key Reference Fix ===\n")
    
    # Test the enrollments table from the test schema
    original_statement = """CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    grade VARCHAR(2),
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
)"""
    
    table_prefix = "schema_1_21_"
    
    print("Original CREATE TABLE statement:")
    print(original_statement)
    print("\n" + "="*60 + "\n")
    
    # Test the modified function
    modified_statement = modify_create_table_statement(original_statement, table_prefix)
    
    print("Modified CREATE TABLE statement:")
    print(modified_statement)
    print("\n" + "="*60 + "\n")
    
    # Check what changed
    print("Changes made:")
    print(f"• Table name: enrollments -> {table_prefix}enrollments")
    print(f"• Foreign key reference: students(id) -> {table_prefix}students(id)")
    print(f"• Foreign key reference: courses(id) -> {table_prefix}courses(id)")
    
    # Verify the changes
    expected_changes = [
        f"CREATE TABLE `{table_prefix}enrollments`",
        f"REFERENCES `{table_prefix}students` (",
        f"REFERENCES `{table_prefix}courses` ("
    ]
    
    print(f"\n✅ VERIFICATION:")
    all_good = True
    for expected in expected_changes:
        if expected in modified_statement:
            print(f"   ✅ Found: {expected}")
        else:
            print(f"   ❌ Missing: {expected}")
            all_good = False
    
    if all_good:
        print(f"\n🎉 SUCCESS: All foreign key references properly prefixed!")
        print("This should resolve the 'Failed to open the referenced table' error.")
    else:
        print(f"\n❌ ISSUES FOUND: Some foreign key references not properly modified.")
    
    return all_good

if __name__ == "__main__":
    success = test_foreign_key_fix()
    sys.exit(0 if success else 1)
