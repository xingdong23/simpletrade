"""
SimpleTrade测试配置

为测试提供共享的fixture和配置。
"""

import os
import sys
import pytest
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# 测试数据库路径
TEST_DB_PATH = os.path.join(ROOT_DIR, "tests", "data", "test_data.db")

@pytest.fixture
def test_db_path():
    """返回测试数据库路径"""
    # 确保测试数据目录存在
    os.makedirs(os.path.dirname(TEST_DB_PATH), exist_ok=True)
    
    # 如果测试数据库已存在，则删除
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    yield TEST_DB_PATH
    
    # 测试后清理
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
