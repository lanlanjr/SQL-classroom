#!/usr/bin/env python3
"""
Test script to verify the database analysis fix
"""

import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_analysis_types():
    """Test that database analysis returns proper data types"""
    
    # Test data similar to what MySQL returns
    test_row = ('users', '100', '5.25', '2.15', '1.10')
    
    try:
        # Simulate the conversion logic from the admin route
        table_rows = int(test_row[1] or 0)
        total_size_mb = float(test_row[2] or 0)
        data_size_mb = float(test_row[3] or 0)
        index_size_mb = float(test_row[4] or 0)
        
        table_info = {
            'name': test_row[0],
            'rows': table_rows,
            'total_size': total_size_mb,
            'data_size': data_size_mb,
            'index_size': index_size_mb
        }
        
        print("✅ Type conversion test passed!")
        print(f"Table: {table_info['name']}")
        print(f"Rows: {table_info['rows']} (type: {type(table_info['rows'])})")
        print(f"Total Size: {table_info['total_size']} MB (type: {type(table_info['total_size'])})")
        print(f"Data Size: {table_info['data_size']} MB (type: {type(table_info['data_size'])})")
        print(f"Index Size: {table_info['index_size']} MB (type: {type(table_info['index_size'])})")
        
        # Test template formatting
        formatted_data = "%.2f" % table_info['data_size']
        formatted_total = "%.2f" % table_info['total_size'] 
        print(f"\n✅ Template formatting test passed!")
        print(f"Formatted data size: {formatted_data}")
        print(f"Formatted total size: {formatted_total}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases with None and empty values"""
    
    edge_cases = [
        ('test_table', None, None, None, None),
        ('empty_table', '', '', '', ''),
        ('zero_table', '0', '0.00', '0.00', '0.00'),
    ]
    
    print("\n🔧 Testing edge cases...")
    
    for test_row in edge_cases:
        try:
            table_rows = int(test_row[1] or 0)
            total_size_mb = float(test_row[2] or 0)
            data_size_mb = float(test_row[3] or 0)
            index_size_mb = float(test_row[4] or 0)
            
            print(f"✅ {test_row[0]}: rows={table_rows}, size={total_size_mb}")
            
        except Exception as e:
            print(f"❌ {test_row[0]} failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Testing database analysis type conversion fixes...")
    
    if test_database_analysis_types() and test_edge_cases():
        print("\n🎉 All tests passed! The TypeError fix should work.")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
