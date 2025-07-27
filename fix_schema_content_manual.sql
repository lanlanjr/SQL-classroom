-- Fix for "Data too long for column 'schema_content'" error
-- This upgrades the schema_content column from TEXT (65KB) to LONGTEXT (4GB)

-- Check current column type
DESCRIBE schema_imports;

-- Upgrade the column to LONGTEXT
ALTER TABLE schema_imports MODIFY COLUMN schema_content LONGTEXT NOT NULL;

-- Verify the change
DESCRIBE schema_imports;

-- You should now see schema_content as 'longtext' instead of 'text'
