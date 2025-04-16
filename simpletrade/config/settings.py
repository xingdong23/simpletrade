"""
SimpleTrade 配置文件

存储应用程序的全局配置参数。
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

# 数据库配置
DB_CONFIG = {
    # 数据库连接参数
    "DB_USER": os.environ.get("SIMPLETRADE_DB_USER", "root"),
    "DB_PASSWORD": os.environ.get("SIMPLETRADE_DB_PASSWORD", "Cz159csa"),
    "DB_HOST": os.environ.get("SIMPLETRADE_DB_HOST", "localhost"),
    "DB_PORT": os.environ.get("SIMPLETRADE_DB_PORT", "3306"),
    "DB_NAME": os.environ.get("SIMPLETRADE_DB_NAME", "simpletrade"),
    
    # 数据库连接池配置
    "POOL_SIZE": int(os.environ.get("SIMPLETRADE_DB_POOL_SIZE", "5")),
    "MAX_OVERFLOW": int(os.environ.get("SIMPLETRADE_DB_MAX_OVERFLOW", "10")),
    "POOL_RECYCLE": int(os.environ.get("SIMPLETRADE_DB_POOL_RECYCLE", "3600")),
    "ECHO": os.environ.get("SIMPLETRADE_DB_ECHO", "False").lower() == "true",
}

# API 配置
API_CONFIG = {
    "HOST": os.environ.get("SIMPLETRADE_API_HOST", "0.0.0.0"),
    "PORT": int(os.environ.get("SIMPLETRADE_API_PORT", "8003")),
    "DEBUG": os.environ.get("SIMPLETRADE_API_DEBUG", "True").lower() == "true",
}

# 日志配置
LOG_CONFIG = {
    "LEVEL": os.environ.get("SIMPLETRADE_LOG_LEVEL", "INFO"),
    "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}
