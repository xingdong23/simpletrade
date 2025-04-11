#!/usr/bin/env python
"""
下载老虎证券历史数据

从老虎证券下载历史数据并保存到数据库中。
"""

import sys
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import HistoryRequest, Exchange, Interval
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database

# 导入老虎证券Gateway
try:
    from vnpy_tiger import TigerGateway
except ImportError:
    print("请先安装vnpy_tiger: pip install -e ./vnpy_tiger")
    sys.exit(1)

# 导入数据管理器
try:
    from simpletrade.core.data import DataManager
except ImportError:
    print("无法导入DataManager，请检查simpletrade.core.data模块")
    sys.exit(1)

# 老虎证券账户配置
TIGER_SETTING = {
    "tiger_id": "",  # 请填写您的老虎证券开放平台ID
    "account": "",   # 请填写您的老虎证券账户
    "private_key": "",  # 请填写您的私钥文件路径
    "server": "模拟",  # 可选: "标准", "环球", "模拟"
    "language": "中文"  # 可选: "中文", "英文"
}

# 要下载的股票列表
SYMBOLS = [
    {"symbol": "AAPL", "exchange": Exchange.NASDAQ},
    {"symbol": "MSFT", "exchange": Exchange.NASDAQ},
    {"symbol": "GOOG", "exchange": Exchange.NASDAQ},
    {"symbol": "AMZN", "exchange": Exchange.NASDAQ},
    {"symbol": "TSLA", "exchange": Exchange.NASDAQ},
]

# 要下载的时间周期
INTERVALS = [
    Interval.MINUTE,
    Interval.HOUR,
    Interval.DAILY,
]

def download_history_data():
    """下载历史数据并保存到数据库"""
    print("正在下载历史数据并保存到数据库...")
    
    # 创建事件引擎和主引擎
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    
    # 添加老虎证券Gateway
    main_engine.add_gateway(TigerGateway)
    
    # 连接老虎证券Gateway
    main_engine.connect(TIGER_SETTING, "TIGER")
    
    # 等待连接成功
    print("等待连接成功...")
    time.sleep(5)
    
    # 创建数据管理器
    data_manager = DataManager()
    
    # 下载不同周期的历史数据
    for interval in INTERVALS:
        # 根据周期设置不同的开始时间
        if interval == Interval.MINUTE:
            start = datetime.now() - timedelta(days=7)  # 分钟数据下载一周
        elif interval == Interval.HOUR:
            start = datetime.now() - timedelta(days=30)  # 小时数据下载一个月
        else:
            start = datetime.now() - timedelta(days=365)  # 日线数据下载一年
        
        end = datetime.now()
        
        # 下载每个股票的历史数据
        for stock in SYMBOLS:
            symbol = stock["symbol"]
            exchange = stock["exchange"]
            
            print(f"正在下载 {symbol} {interval.value} 周期的历史数据...")
            
            # 创建历史数据请求
            req = HistoryRequest(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start=start,
                end=end
            )
            
            # 查询历史数据
            bars = main_engine.query_history(req, "TIGER")
            
            if bars:
                # 保存到数据库
                database = get_database()
                database.save_bar_data(bars)
                
                print(f"成功下载并保存 {len(bars)} 条 {symbol} {interval.value} 周期的历史数据")
            else:
                print(f"未获取到 {symbol} {interval.value} 周期的历史数据")
            
            # 避免请求过于频繁
            time.sleep(1)
    
    # 关闭连接
    main_engine.close()
    
    print("历史数据下载完成")

if __name__ == "__main__":
    # 检查配置是否填写
    if not TIGER_SETTING["tiger_id"] or not TIGER_SETTING["account"] or not TIGER_SETTING["private_key"]:
        print("请先填写老虎证券账户配置")
        sys.exit(1)
    
    # 下载历史数据
    download_history_data()
