#!/usr/bin/env python
"""
测试vnpy_tiger导入问题的脚本

此脚本用于诊断vnpy_tiger在应用启动时的导入问题，并尝试通过显式添加路径到sys.path来解决。
"""

import os
import sys
import importlib
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("tiger_import_test")

# 显示当前工作目录
cwd = os.getcwd()
logger.info(f"当前工作目录: {cwd}")

# 显示Python路径
logger.info("Python搜索路径:")
for i, path in enumerate(sys.path):
    logger.info(f"  {i}: {path}")

# 检查vnpy_tiger目录是否存在
tiger_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vnpy_tiger')
logger.info(f"检查vnpy_tiger路径: {tiger_path}")
if os.path.exists(tiger_path):
    logger.info(f"vnpy_tiger目录存在")
    
    # 检查是否已在sys.path中
    if tiger_path not in sys.path:
        logger.info(f"将vnpy_tiger路径添加到sys.path")
        sys.path.insert(0, tiger_path)
    else:
        logger.info(f"vnpy_tiger路径已在sys.path中")
else:
    logger.error(f"vnpy_tiger目录不存在: {tiger_path}")

# 尝试导入vnpy_tiger
try:
    logger.info("尝试导入vnpy_tiger...")
    import vnpy_tiger
    logger.info(f"vnpy_tiger成功导入，版本或路径: {vnpy_tiger.__file__}")
    
    # 尝试导入TigerGateway
    try:
        from vnpy_tiger import TigerGateway
        logger.info("TigerGateway成功导入")
    except ImportError as e:
        logger.error(f"导入TigerGateway失败: {e}")
        
    # 检查tigeropen依赖
    try:
        import tigeropen
        logger.info(f"tigeropen成功导入，版本或路径: {tigeropen.__file__}")
    except ImportError as e:
        logger.error(f"导入tigeropen失败: {e}")
        
except ImportError as e:
    logger.error(f"导入vnpy_tiger失败: {e}")
    
    # 尝试使用importlib动态导入
    try:
        logger.info("尝试使用importlib动态导入...")
        vnpy_tiger_spec = importlib.util.find_spec("vnpy_tiger")
        if vnpy_tiger_spec:
            logger.info(f"找到vnpy_tiger模块规格: {vnpy_tiger_spec}")
            vnpy_tiger_module = importlib.util.module_from_spec(vnpy_tiger_spec)
            vnpy_tiger_spec.loader.exec_module(vnpy_tiger_module)
            logger.info("使用importlib成功导入vnpy_tiger")
        else:
            logger.error("未找到vnpy_tiger模块规格")
    except Exception as e:
        logger.error(f"使用importlib导入失败: {e}")

logger.info("测试完成")