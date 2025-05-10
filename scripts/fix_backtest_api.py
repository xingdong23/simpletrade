#!/usr/bin/env python
"""
修复回测 API 的脚本

这个脚本会：
1. 添加缺失的字段到 BacktestRecord 表
2. 替换 get_backtest_report_data 函数，使其能够处理缺失的字段
"""

import sys
import os
from pathlib import Path
import logging
import shutil
import traceback

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    logger.info("开始修复回测 API")
    
    # 1. 运行添加缺失字段的脚本
    try:
        logger.info("运行添加缺失字段的脚本")
        from scripts.add_missing_fields import main as add_missing_fields_main
        add_missing_fields_main()
    except Exception as e:
        logger.error(f"运行添加缺失字段的脚本失败: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # 2. 替换 get_backtest_report_data 函数
    try:
        logger.info("替换 get_backtest_report_data 函数")
        service_path = os.path.join(project_root, "simpletrade", "apps", "st_backtest", "service.py")
        fixed_service_path = os.path.join(project_root, "simpletrade", "apps", "st_backtest", "service.py.fixed")
        
        # 备份原文件
        backup_path = service_path + ".bak"
        shutil.copy2(service_path, backup_path)
        logger.info(f"已备份原文件到 {backup_path}")
        
        # 替换文件
        shutil.copy2(fixed_service_path, service_path)
        logger.info(f"已替换文件 {service_path}")
    except Exception as e:
        logger.error(f"替换 get_backtest_report_data 函数失败: {str(e)}")
        logger.debug(traceback.format_exc())
    
    logger.info("修复回测 API 完成")

if __name__ == "__main__":
    main()
