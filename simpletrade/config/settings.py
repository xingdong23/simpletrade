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
    "DB_HOST": os.environ.get("SIMPLETRADE_DB_HOST", "127.0.0.1"),
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
    "ENABLED": os.environ.get("SIMPLETRADE_API_ENABLED", "True").lower() == "true",
    "HOST": os.environ.get("SIMPLETRADE_API_HOST", "0.0.0.0"),
    "PORT": int(os.environ.get("SIMPLETRADE_API_PORT", "8003")),
    "DEBUG": os.environ.get("SIMPLETRADE_API_DEBUG", "True").lower() == "true",
}

# 日志配置
LOG_CONFIG = {
    "LEVEL": os.environ.get("SIMPLETRADE_LOG_LEVEL", "INFO"),
    "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}

# +++ Qlib 数据路径配置 +++
# 从环境变量读取，如果未设置，则使用默认路径
_default_qlib_path = "/Users/chengzheng/.qlib/qlib_data" # <<< 设置默认路径
QLIB_DATA_PATH = os.environ.get("SIMPLETRADE_QLIB_DATA_PATH", _default_qlib_path)

if QLIB_DATA_PATH == _default_qlib_path and not os.environ.get("SIMPLETRADE_QLIB_DATA_PATH"):
    print(f"[Config] Using default Qlib data path: {QLIB_DATA_PATH}")
    print(f"[Config] (Set SIMPLETRADE_QLIB_DATA_PATH environment variable to override)")
elif QLIB_DATA_PATH != _default_qlib_path:
    print(f"[Config] Qlib data path configured via environment variable: {QLIB_DATA_PATH}")
else: # Path matches default, but was set explicitly by env var
    print(f"[Config] Qlib data path explicitly set to default via environment variable: {QLIB_DATA_PATH}")
    
# 可以在这里添加路径存在性检查（可选）
# if not os.path.exists(QLIB_DATA_PATH):
#     print(f"[Config Warning] Qlib data path does not exist: {QLIB_DATA_PATH}")

# +++ 结束 Qlib 配置 +++

# 数据同步服务配置
DATA_SYNC_CONFIG = {
    "ENABLED": os.environ.get("SIMPLETRADE_DATA_SYNC_ENABLED", "False").lower() == "true",
    "SYNC_ON_STARTUP": os.environ.get("SIMPLETRADE_SYNC_ON_STARTUP", "True").lower() == "true",
    "SYNC_INTERVAL": int(os.environ.get("SIMPLETRADE_SYNC_INTERVAL", "86400")),  # 默认每天同步一次（单位：秒）
    "MAX_RETRIES": int(os.environ.get("SIMPLETRADE_SYNC_MAX_RETRIES", "3")),  # 同步失败最大重试次数
    "PERIODIC_SYNC": os.environ.get("SIMPLETRADE_PERIODIC_SYNC", "False").lower() == "true",  # 是否启用周期性同步
}

# 数据同步目标配置
# 列表中的每个字典定义一个同步目标
DATA_SYNC_TARGETS = [
    {
        "source": "qlib",        # 数据源类型
        "symbol": "AAPL",        # 品种代码
        "exchange": "NASDAQ",    # 交易所 (使用 VnPy 枚举值对应的字符串)
        "interval": "d",         # K线周期 (日线)
        "start_date": "1970-01-01",  # 开始日期 (可选，默认为 "2020-01-01")
        # "end_date": "2022-12-31",  # 结束日期 (可选，默认为当前日期)
        "market": "us",          # 市场标识 (qlib 特有参数)
        "enabled": True          # 是否启用 (可选，默认为 True)
    },
    # {
    #     "source": "qlib",      
    #     "symbol": "600036",    # 招商银行
    #     "exchange": "SSE",     # 上海证券交易所
    #     "interval": "d",       # 日线
    #     "market": "cn",        # 市场标识
    #     "enabled": True        
    # },
    # 其他数据源示例
    # {
    #     "source": "csv",
    #     "symbol": "EURUSD",
    #     "exchange": "OANDA",
    #     "interval": "1h",
    #     "csv_path": "/data/forex/eurusd_1h.csv",  # csv 特有参数
    #     "datetime_format": "%Y-%m-%d %H:%M:%S",   # csv 特有参数
    #     "enabled": False  # 禁用此目标
    # },
]
