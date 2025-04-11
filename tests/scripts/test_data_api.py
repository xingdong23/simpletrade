#!/usr/bin/env python
"""
数据管理API测试脚本

用于测试数据管理API的功能。
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI
import uvicorn

from simpletrade.api.data import router as data_router
from simpletrade.core.data import DataManager, BarData, Exchange, Interval

def generate_test_data():
    """生成测试数据"""
    # 创建数据管理器
    db_path = os.path.join(ROOT_DIR, "test_data.db")
    
    # 如果文件已存在，则删除
    if os.path.exists(db_path):
        os.remove(db_path)
    
    manager = DataManager(db_path)
    
    # 生成K线数据
    bars = []
    
    # 使用当前时间作为基准
    now = datetime.now()
    
    # 生成过去30天的日线数据
    for i in range(30):
        dt = now - timedelta(days=i)
        
        # 生成随机价格
        close_price = random.uniform(100, 200)
        open_price = close_price * random.uniform(0.98, 1.02)
        high_price = max(open_price, close_price) * random.uniform(1.0, 1.05)
        low_price = min(open_price, close_price) * random.uniform(0.95, 1.0)
        
        # 生成随机成交量
        volume = random.uniform(1000, 10000)
        
        # 创建K线数据
        bar = BarData(
            symbol="AAPL",
            exchange=Exchange.NASDAQ,
            datetime=dt,
            interval=Interval.DAILY,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            close_price=close_price,
            volume=volume,
            open_interest=0
        )
        
        bars.append(bar)
    
    # 保存数据
    manager.save_bar_data(bars)
    
    print(f"生成了 {len(bars)} 条测试数据")
    
    return db_path

def test_api():
    """测试API功能"""
    print("测试API功能")
    
    # 生成测试数据
    db_path = generate_test_data()
    
    # 创建FastAPI应用
    app = FastAPI(title="SimpleTrade API Test")
    
    # 添加路由
    app.include_router(data_router)
    
    # 启动服务
    print("API服务已启动，访问 http://localhost:8000/docs 查看API文档")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    # 清理临时文件
    if os.path.exists(db_path):
        os.remove(db_path)

def test_message():
    """测试消息指令功能"""
    print("测试消息指令功能")
    
    # 生成测试数据
    db_path = generate_test_data()
    
    # 创建数据管理器
    manager = DataManager(db_path)
    
    # 创建消息处理器
    from simpletrade.core.message import MessageProcessor
    from simpletrade.core.message.data_processor import DataCommandProcessor
    
    message_processor = MessageProcessor()
    data_processor = DataCommandProcessor(manager)
    message_processor.register_processor(data_processor)
    
    # 交互式测试
    print("输入消息指令进行测试，输入'exit'退出")
    print("示例: /data query")
    
    while True:
        message = input("> ")
        if message.lower() == "exit":
            break
        
        result = message_processor.process(message)
        print(result or "无响应")
    
    # 清理临时文件
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "api":
            test_api()
        elif sys.argv[1] == "message":
            test_message()
        else:
            print(f"未知的测试类型: {sys.argv[1]}")
            print("可用的测试类型: api, message")
    else:
        print("请指定测试类型: api 或 message")
        print("示例: python scripts/test_data_api.py api")
        print("示例: python scripts/test_data_api.py message")
