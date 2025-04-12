#!/usr/bin/env python
"""
测试vnpy集成

测试SimpleTrade与vnpy的集成。
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# 导入vnpy的数据模型和数据管理功能
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval

# 导入我们的数据管理器
from simpletrade.core.data import DataManager

def test_data_manager():
    """测试数据管理器"""
    print("测试数据管理器")
    
    # 创建数据管理器
    manager = DataManager()
    
    # 生成测试数据
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
    count = manager.save_bar_data(bars)
    print(f"保存了 {count} 条K线数据")
    
    # 查询数据
    start = now - timedelta(days=30)
    end = now
    
    loaded_bars = manager.load_bar_data(
        symbol="AAPL",
        exchange=Exchange.NASDAQ,
        interval=Interval.DAILY,
        start=start,
        end=end
    )
    
    print(f"查询到 {len(loaded_bars)} 条K线数据")
    
    # 打印前5条数据
    for i, bar in enumerate(loaded_bars[:5]):
        print(f"{i+1}. {bar.datetime.strftime('%Y-%m-%d')}: 开{bar.open_price:.2f} 高{bar.high_price:.2f} 低{bar.low_price:.2f} 收{bar.close_price:.2f} 量{bar.volume:.2f}")
    
    # 获取数据概览
    overviews = manager.get_bar_overview()
    
    print("\n数据概览:")
    for i, overview in enumerate(overviews):
        print(f"{i+1}. {overview['symbol']}.{overview['exchange']} - {overview['interval']} - {overview['count']}条 ({overview['start'].strftime('%Y-%m-%d')} 至 {overview['end'].strftime('%Y-%m-%d')})")
    
    # 删除数据
    count = manager.delete_bar_data(
        symbol="AAPL",
        exchange=Exchange.NASDAQ,
        interval=Interval.DAILY
    )
    
    print(f"\n删除了 {count} 条K线数据")
    
    # 再次查询数据
    loaded_bars = manager.load_bar_data(
        symbol="AAPL",
        exchange=Exchange.NASDAQ,
        interval=Interval.DAILY,
        start=start,
        end=end
    )
    
    print(f"查询到 {len(loaded_bars)} 条K线数据")

if __name__ == "__main__":
    test_data_manager()
