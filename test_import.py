import sys
print(sys.path)
try:
    import vnpy_tiger
    print('vnpy_tiger imported successfully')
except ImportError as e:
    print(f'Import error: {e}')
