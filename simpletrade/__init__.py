"""
SimpleTrade - 一个简单的交易系统
"""

# 设置版本号
__version__ = "0.1.0"

# 添加vnpy源码路径
import sys
from pathlib import Path

# 添加vnpy源码目录到Python路径
VNPY_CUSTOM_DIR = Path(__file__).parent.parent / "vnpy_custom"
if VNPY_CUSTOM_DIR.exists() and str(VNPY_CUSTOM_DIR) not in sys.path:
    sys.path.insert(0, str(VNPY_CUSTOM_DIR))
    print(f"Added vnpy_custom to sys.path: {VNPY_CUSTOM_DIR}")

# 设置日志格式
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
