#!/usr/bin/env python
"""
数据管理模块测试脚本

用于测试数据管理模块的功能。
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

from simpletrade.core.data import DataManager, BarData, TickData, Exchange, Interval

def generate_test_data():
    """生成测试数据"""
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
    
    return bars

def test_data_manager():
    """测试数据管理器"""
    print("测试数据管理器")
    
    # 创建临时数据库文件
    db_path = os.path.join(ROOT_DIR, "test_data.db")
    
    # 如果文件已存在，则删除
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 创建数据管理器
    manager = DataManager(db_path)
    
    # 生成测试数据
    bars = generate_test_data()
    
    # 保存数据
    count = manager.save_bar_data(bars)
    print(f"保存了 {count} 条K线数据")
    
    # 查询数据概览
    overviews = manager.get_bar_overview()
    print("\n数据概览:")
    for overview in overviews:
        print(f"{overview.symbol}.{overview.exchange} - {overview.interval}: {overview.count}条 ({overview.start} 至 {overview.end})")
    
    # 查询数据
    start = datetime.now() - timedelta(days=10)
    end = datetime.now()
    
    query_bars = manager.load_bar_data("AAPL", Exchange.NASDAQ, Interval.DAILY, start, end)
    print(f"\n查询到 {len(query_bars)} 条K线数据:")
    for i, bar in enumerate(query_bars[:5]):
        print(f"{i+1}. {bar.datetime}: 开{bar.open_price:.2f} 高{bar.high_price:.2f} 低{bar.low_price:.2f} 收{bar.close_price:.2f} 量{bar.volume:.2f}")
    
    # 导出数据到CSV
    csv_path = os.path.join(ROOT_DIR, "test_data.csv")
    success, msg, count = manager.export_bar_data_to_csv(
        csv_path, "AAPL", Exchange.NASDAQ, Interval.DAILY, start, end
    )
    print(f"\n导出数据: {msg}")
    
    # 删除数据
    count = manager.delete_bar_data("AAPL", Exchange.NASDAQ, Interval.DAILY)
    print(f"\n删除了 {count} 条K线数据")
    
    # 再次查询数据概览
    overviews = manager.get_bar_overview()
    print("\n删除后的数据概览:")
    if overviews:
        for overview in overviews:
            print(f"{overview.symbol}.{overview.exchange} - {overview.interval}: {overview.count}条 ({overview.start} 至 {overview.end})")
    else:
        print("没有数据")
    
    # 导入数据
    success, msg, count = manager.import_bar_data_from_csv(
        csv_path, "AAPL", Exchange.NASDAQ, Interval.DAILY
    )
    print(f"\n导入数据: {msg}")
    
    # 再次查询数据概览
    overviews = manager.get_bar_overview()
    print("\n导入后的数据概览:")
    for overview in overviews:
        print(f"{overview.symbol}.{overview.exchange} - {overview.interval}: {overview.count}条 ({overview.start} 至 {overview.end})")
    
    # 清理临时文件
    if os.path.exists(db_path):
        os.remove(db_path)
    
    if os.path.exists(csv_path):
        os.remove(csv_path)
    
    print("\n测试完成")

if __name__ == "__main__":
    test_data_manager()
