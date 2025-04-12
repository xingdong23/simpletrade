"""
测试Tiger Gateway的导入和使用
"""

import sys
import os
from pathlib import Path

# 确保vnpy_tiger在Python路径中
project_root = str(Path(__file__).parent.absolute())
vnpy_tiger_path = os.path.join(project_root, 'vnpy_tiger')
if os.path.exists(vnpy_tiger_path) and vnpy_tiger_path not in sys.path:
    print(f"Adding vnpy_tiger path to sys.path: {vnpy_tiger_path}")
    sys.path.insert(0, vnpy_tiger_path)

# 显示Python搜索路径
print("Python search paths:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

try:
    print("Attempting to import vnpy_tiger...")
    from vnpy_tiger import TigerGateway
    print("vnpy_tiger imported successfully.")
    print(f"TigerGateway class: {TigerGateway}")
except ImportError as e:
    print(f"Warning: vnpy_tiger not found. Error: {e}")
    print("Please install it first.")
