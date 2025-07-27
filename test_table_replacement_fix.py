#!/usr/bin/env python3
"""
Test the fixed table name replacement logic
"""

def test_table_replacement():
    print("=== Testing Fixed Table Name Replacement Logic ===\n")
    
    import re
    
    # Simulate the table mappings
    table_mappings = {
        'customers': 'schema_1_18_customers',
        'orders': 'schema_1_18_orders',
        'products': 'schema_1_18_products'
    }
    
    # Test SQL statements that were causing problems
    test_statements = [
        # Backticked table names (was causing double backticks)
        "ALTER TABLE `customers` ADD PRIMARY KEY (`customerNumber`);",
        "INSERT INTO `orders` VALUES (1, 'test');",
        "ALTER TABLE `products` ADD INDEX (`productCode`);",
        
        # Non-backticked table names
        "ALTER TABLE customers ADD PRIMARY KEY (customerNumber);",
        "INSERT INTO orders VALUES (1, 'test');",
        "ALTER TABLE products ADD INDEX (productCode);",
        
        # Mixed scenarios
        "ALTER TABLE `customers` ADD CONSTRAINT FOREIGN KEY (orderID) REFERENCES orders (id);",
        "SELECT * FROM customers c JOIN `orders` o ON c.id = o.customer_id;",
    ]
    
    for i, stmt in enumerate(test_statements, 1):
        print(f"Test {i}:")
        print(f"Original: {stmt}")
        
        # Apply the same logic as in the fixed code
        modified_stmt = stmt
        replacements_made = 0
        
        for original_table, prefixed_table in table_mappings.items():
            # First replace backticked table names: `tablename`
            backticked_pattern = r'`' + re.escape(original_table) + r'`'
            old_stmt = modified_stmt
            modified_stmt = re.sub(backticked_pattern, f"`{prefixed_table}`", modified_stmt, flags=re.IGNORECASE)
            if old_stmt != modified_stmt:
                replacements_made += 1
            
            # Then replace non-backticked table names with word boundaries
            word_boundary_pattern = r'\b' + re.escape(original_table) + r'\b'
            old_stmt = modified_stmt
            modified_stmt = re.sub(word_boundary_pattern, f"`{prefixed_table}`", modified_stmt, flags=re.IGNORECASE)
            if old_stmt != modified_stmt:
                replacements_made += 1
        
        print(f"Modified: {modified_stmt}")
        print(f"Replacements: {replacements_made}")
        
        # Check for double backticks (the bug we're fixing)
        if '``' in modified_stmt:
            print("❌ ISSUE: Double backticks detected!")
        else:
            print("✅ SUCCESS: No double backticks")
        print("-" * 60)
    
    print("\n🎯 SUMMARY:")
    print("The fix handles both backticked and non-backticked table names")
    print("without creating double backticks in the SQL syntax.")

if __name__ == "__main__":
    test_table_replacement()
