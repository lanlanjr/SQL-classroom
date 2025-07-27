import sys
sys.path.append('.')

try:
    from app.utils import process_show_tables_result_for_schema, _find_matching_schema_tables, _format_show_tables_result
    print('✅ All imports successful - no syntax errors')
    print('✅ Function process_show_tables_result_for_schema imported')
    print('✅ Helper function _find_matching_schema_tables imported')  
    print('✅ Helper function _format_show_tables_result imported')
except ImportError as e:
    print(f'❌ Import error: {e}')
except SyntaxError as e:
    print(f'❌ Syntax error: {e}')
