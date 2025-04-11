#!/usr/bin/env python
"""
微信小程序API测试脚本

用于测试微信小程序API接口。
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random
import json

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

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
    print("测试微信小程序API功能")
    
    # 生成测试数据
    db_path = generate_test_data()
    
    # 创建FastAPI应用
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="SimpleTrade WeChat API Test")
    
    # 添加路由
    from simpletrade.api.wechat import auth_router, data_router
    app.include_router(auth_router)
    app.include_router(data_router)
    
    # 启动服务
    print("API服务已启动，访问 http://localhost:8000/docs 查看API文档")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    # 清理临时文件
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    test_api()
