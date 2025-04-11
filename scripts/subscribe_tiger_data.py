#!/usr/bin/env python
"""
订阅老虎证券实时行情

订阅老虎证券实时行情并保存到数据库中。
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.object import SubscribeRequest, TickData
from vnpy.trader.constant import Exchange
from vnpy.trader.database import get_database

# 导入老虎证券Gateway
try:
    from vnpy_tiger import TigerGateway
except ImportError:
    print("请先安装vnpy_tiger: pip install -e ./vnpy_tiger")
    sys.exit(1)

# 老虎证券账户配置
TIGER_SETTING = {
    "tiger_id": "",  # 请填写您的老虎证券开放平台ID
    "account": "",   # 请填写您的老虎证券账户
    "private_key": "",  # 请填写您的私钥文件路径
    "server": "模拟",  # 可选: "标准", "环球", "模拟"
    "language": "中文"  # 可选: "中文", "英文"
}

# 要订阅的股票列表
SYMBOLS = [
    {"symbol": "AAPL", "exchange": Exchange.NASDAQ},
    {"symbol": "MSFT", "exchange": Exchange.NASDAQ},
    {"symbol": "GOOG", "exchange": Exchange.NASDAQ},
    {"symbol": "AMZN", "exchange": Exchange.NASDAQ},
    {"symbol": "TSLA", "exchange": Exchange.NASDAQ},
]

class TickRecorder:
    """Tick数据记录器"""
    
    def __init__(self):
        """初始化"""
        self.database = get_database()
        self.ticks = []
        self.tick_count = 0
        self.last_save_time = datetime.now()
        
        # 创建事件引擎和主引擎
        self.event_engine = EventEngine()
        self.main_engine = MainEngine(self.event_engine)
        
        # 添加老虎证券Gateway
        self.main_engine.add_gateway(TigerGateway)
        
        # 注册行情回调函数
        self.event_engine.register("TICK", self.process_tick_event)
    
    def start(self):
        """启动记录器"""
        # 连接老虎证券Gateway
        self.main_engine.connect(TIGER_SETTING, "TIGER")
        
        # 等待连接成功
        print("等待连接成功...")
        time.sleep(5)
        
        # 订阅行情
        for stock in SYMBOLS:
            symbol = stock["symbol"]
            exchange = stock["exchange"]
            
            req = SubscribeRequest(
                symbol=symbol,
                exchange=exchange
            )
            self.main_engine.subscribe(req, "TIGER")
            print(f"已订阅 {symbol} 的实时行情")
        
        print("所有股票订阅完成，正在接收实时行情...")
        print("按Ctrl+C退出")
        
        # 主循环
        try:
            while True:
                # 每隔10秒保存一次数据
                if (datetime.now() - self.last_save_time).total_seconds() >= 10:
                    self.save_ticks()
                    self.last_save_time = datetime.now()
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("用户中断，正在退出...")
            self.save_ticks()  # 保存剩余的Tick数据
            self.main_engine.close()
    
    def process_tick_event(self, event):
        """处理Tick事件"""
        tick = event.data
        self.ticks.append(tick)
        self.tick_count += 1
        
        # 打印Tick数据
        print(f"收到Tick数据: {tick.symbol} {tick.datetime} 最新价: {tick.last_price}")
    
    def save_ticks(self):
        """保存Tick数据到数据库"""
        if not self.ticks:
            return
        
        # 保存到数据库
        self.database.save_tick_data(self.ticks)
        
        print(f"已保存 {len(self.ticks)} 条Tick数据到数据库，总计: {self.tick_count}")
        
        # 清空缓存
        self.ticks = []

if __name__ == "__main__":
    # 检查配置是否填写
    if not TIGER_SETTING["tiger_id"] or not TIGER_SETTING["account"] or not TIGER_SETTING["private_key"]:
        print("请先填写老虎证券账户配置")
        sys.exit(1)
    
    # 启动Tick记录器
    recorder = TickRecorder()
    recorder.start()
