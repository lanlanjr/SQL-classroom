#!/usr/bin/env python3
import os
import re

# Files to fix
files_to_fix = [
    'app/routes/teacher.py',
    'app/routes/student.py', 
    'app/routes/admin.py',
    'migrations/update_auto_increment_to_six_digits.py'
]

# Pattern to find and replace
pattern = r"port=os\.getenv\('MYSQL_PORT', 3306\)"
replacement = "port=int(os.getenv('MYSQL_PORT', 3306))"

for file_path in files_to_fix:
    if os.path.exists(file_path):
        print(f"Processing {file_path}...")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count occurrences before replacement
        count_before = len(re.findall(pattern, content))
        
        # Replace all occurrences
        new_content = re.sub(pattern, replacement, content)
        
        # Count occurrences after replacement
        count_after = len(re.findall(pattern, new_content))
        
        if count_before > 0:
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  Fixed {count_before} occurrences in {file_path}")
        else:
            print(f"  No occurrences found in {file_path}")
    else:
        print(f"File not found: {file_path}")

print("Done!")
