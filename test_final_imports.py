import sys
sys.path.append('.')

try:
    from app.utils import rewrite_query_for_schema, process_show_tables_result_for_schema, is_show_tables_query
    print('✅ All imports successful - query rewriting functionality ready')
    print('✅ Function rewrite_query_for_schema imported')
    print('✅ Function process_show_tables_result_for_schema imported')  
    print('✅ Function is_show_tables_query imported')
except ImportError as e:
    print(f'❌ Import error: {e}')
except SyntaxError as e:
    print(f'❌ Syntax error: {e}')
