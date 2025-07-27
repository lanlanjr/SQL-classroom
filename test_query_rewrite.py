#!/usr/bin/env python3
"""
Test script for the query rewriting functionality
"""

import re

def test_query_rewriting():
    """Test the query rewriting logic"""
    
    # Mock data
    table_names = ['customers', 'employees', 'offices', 'orderdetails', 'orders', 'payments', 'productlines', 'products']
    table_prefix = 'schema_1_23_'
    
    test_queries = [
        'SELECT * FROM customers',
        'select * from customers;',
        'SELECT * FROM `customers`',
        'SELECT c.name, o.total FROM customers c JOIN orders o ON c.id = o.customer_id',
        'SELECT COUNT(*) FROM orders WHERE customer_id IN (SELECT id FROM customers)',
        'DESCRIBE customers',
        'SHOW CREATE TABLE products',
        'SELECT * FROM customers, orders, products'
    ]
    
    def rewrite_query(query, table_names, table_prefix):
        """Apply the same rewriting logic as in the code"""
        modified_query = query
        for table_name in table_names:
            # First replace backticked table names: `tablename`
            backticked_pattern = r'`' + re.escape(table_name) + r'`'
            prefixed_table = f"{table_prefix}{table_name}"
            old_query = modified_query
            modified_query = re.sub(backticked_pattern, f"`{prefixed_table}`", modified_query, flags=re.IGNORECASE)
            if old_query != modified_query:
                print(f"  ✓ Replaced backticked '{table_name}' with '{prefixed_table}'")
            
            # Then replace non-backticked table names with word boundaries
            word_boundary_pattern = r'\b' + re.escape(table_name) + r'\b'
            old_query = modified_query
            modified_query = re.sub(word_boundary_pattern, f"`{prefixed_table}`", modified_query, flags=re.IGNORECASE)
            if old_query != modified_query:
                print(f"  ✓ Replaced non-backticked '{table_name}' with '{prefixed_table}'")
        
        return modified_query
    
    print("Testing Query Rewriting Logic")
    print("=" * 50)
    print(f"Table prefix: {table_prefix}")
    print(f"Available tables: {table_names}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}:")
        print(f"  Original: {query}")
        rewritten = rewrite_query(query, table_names, table_prefix)
        print(f"  Rewritten: {rewritten}")
        print()

if __name__ == "__main__":
    test_query_rewriting()
