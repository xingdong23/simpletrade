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

# 数据同步目标配置
# 列表中的每个字典定义一个同步目标
# source: 数据源标识符 (需要与 DataSyncService 中的导入器逻辑对应)
# symbol, exchange, interval: VnPy 标准格式
DATA_SYNC_TARGETS = [
    {
        "source": "qlib",        # 数据源为 qlib
        "symbol": "AAPL",       # 品种代码
        "exchange": "NASDAQ",   # 交易所 (使用 VnPy 枚举值对应的字符串)
        "interval": "d"         # K线周期 (日线)
    },
    # {
    #     "source": "qlib",      
    #     "symbol": "600036",    # 招商银行
    #     "exchange": "SSE",      # 上海证券交易所
    #     "interval": "d"
    # },
    # 添加更多目标...
    # {
    #     "source": "csv",       # 示例: 来自 CSV 文件
    #     "symbol": "RBIF",     # 螺纹钢指数 (示例)
    #     "exchange": "LOCAL",  # 本地数据交易所代码 (示例)
    #     "interval": "1h",     # 1小时线
    #     "csv_path": "/data/csv/rbif_1h.csv" # CSV 导入器可能需要的额外参数
    # },
]
