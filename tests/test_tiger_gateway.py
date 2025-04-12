#!/usr/bin/env python
"""
测试老虎证券Gateway

测试老虎证券Gateway的历史数据下载和实时数据订阅功能。
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
from vnpy.trader.object import SubscribeRequest, HistoryRequest, Exchange, Interval
from vnpy.trader.constant import Exchange, Interval

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

def test_history_data():
    """测试历史数据下载"""
    print("正在测试历史数据下载...")
    
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
    
    # 创建历史数据请求
    symbol = "AAPL"  # 苹果股票
    exchange = Exchange.NASDAQ
    start = datetime.now() - timedelta(days=10)
    end = datetime.now()
    
    req = HistoryRequest(
        symbol=symbol,
        exchange=exchange,
        interval=Interval.DAILY,
        start=start,
        end=end
    )
    
    # 查询历史数据
    print(f"正在查询 {symbol} 的历史数据...")
    bars = main_engine.query_history(req, "TIGER")
    
    # 打印历史数据
    if bars:
        print(f"成功获取 {len(bars)} 条历史数据:")
        for bar in bars:
            print(f"日期: {bar.datetime}, 开盘: {bar.open_price}, 最高: {bar.high_price}, 最低: {bar.low_price}, 收盘: {bar.close_price}, 成交量: {bar.volume}")
    else:
        print("未获取到历史数据")
    
    # 关闭连接
    main_engine.close()

def test_subscribe():
    """测试实时数据订阅"""
    print("正在测试实时数据订阅...")
    
    # 创建事件引擎和主引擎
    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    
    # 添加老虎证券Gateway
    main_engine.add_gateway(TigerGateway)
    
    # 注册行情回调函数
    def on_tick(tick):
        print(f"收到Tick数据: {tick.symbol} {tick.datetime} 最新价: {tick.last_price}")
    
    event_engine.register("TICK", on_tick)
    
    # 连接老虎证券Gateway
    main_engine.connect(TIGER_SETTING, "TIGER")
    
    # 等待连接成功
    print("等待连接成功...")
    time.sleep(5)
    
    # 创建订阅请求
    symbols = ["AAPL", "MSFT", "GOOG"]  # 苹果、微软、谷歌
    exchange = Exchange.NASDAQ
    
    # 订阅行情
    print(f"正在订阅 {symbols} 的行情...")
    for symbol in symbols:
        req = SubscribeRequest(
            symbol=symbol,
            exchange=exchange
        )
        main_engine.subscribe(req, "TIGER")
    
    # 等待行情推送
    print("等待行情推送，按Ctrl+C退出...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("用户中断，正在退出...")
    
    # 关闭连接
    main_engine.close()

if __name__ == "__main__":
    # 检查配置是否填写
    if not TIGER_SETTING["tiger_id"] or not TIGER_SETTING["account"] or not TIGER_SETTING["private_key"]:
        print("请先填写老虎证券账户配置")
        sys.exit(1)
    
    # 测试历史数据下载
    test_history_data()
    
    # 测试实时数据订阅
    test_subscribe()
