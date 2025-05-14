"""
替换TA-Lib模块

这个脚本用于替换系统中的talib模块，使用pandas-ta作为后端。
在导入vnpy之前执行这个脚本，可以避免vnpy对TA-Lib的依赖。
"""

import sys
import importlib
import logging

def replace_talib():
    """
    替换系统中的talib模块
    
    使用pandas-ta实现的TalibAdapter替换系统中的talib模块。
    这样可以在不修改vnpy代码的情况下使用pandas-ta。
    """
    try:
        # 尝试导入talib
        import talib
        logging.warning("TA-Lib已经安装，不需要替换。")
        return
    except ImportError:
        # 如果talib没有安装，使用我们的适配器
        from simpletrade.utils.talib_adapter import TalibAdapter
        
        # 替换系统中的talib模块
        sys.modules['talib'] = TalibAdapter
        logging.info("已使用pandas-ta替换TA-Lib。")
        
        # 如果vnpy已经导入，需要重新加载相关模块
        if 'vnpy' in sys.modules:
            # 获取所有已导入的vnpy模块
            vnpy_modules = [m for m in sys.modules if m.startswith('vnpy')]
            
            # 重新加载这些模块
            for module_name in vnpy_modules:
                try:
                    module = sys.modules[module_name]
                    importlib.reload(module)
                    logging.info(f"重新加载模块: {module_name}")
                except:
                    logging.warning(f"无法重新加载模块: {module_name}")

# 自动执行替换
replace_talib()
