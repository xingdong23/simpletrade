"""
数据管理器单元测试
"""

import pytest
from datetime import datetime, timedelta
import os

from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval

from simpletrade.core.data import DataManager

def test_data_manager_init(test_db_path):
    """测试数据管理器初始化"""
    manager = DataManager()
    assert manager is not None
    assert hasattr(manager, 'database_manager')

def test_save_and_load_bar_data(test_db_path):
    """测试保存和加载K线数据"""
    # 创建数据管理器
    manager = DataManager()
    
    # 创建测试数据
    now = datetime.now()
    bar = BarData(
        symbol="TEST",
        exchange=Exchange.NASDAQ,
        datetime=now,
        interval=Interval.DAILY,
        open_price=100.0,
        high_price=110.0,
        low_price=90.0,
        close_price=105.0,
        volume=1000.0,
        open_interest=0.0
    )
    
    # 保存数据
    count = manager.save_bar_data([bar])
    assert count == 1
    
    # 加载数据
    start = now - timedelta(days=1)
    end = now + timedelta(days=1)
    bars = manager.load_bar_data(
        symbol="TEST",
        exchange=Exchange.NASDAQ,
        interval=Interval.DAILY,
        start=start,
        end=end
    )
    
    # 验证数据
    assert len(bars) == 1
    assert bars[0].symbol == "TEST"
    assert bars[0].exchange == Exchange.NASDAQ
    assert bars[0].interval == Interval.DAILY
    assert bars[0].open_price == 100.0
    assert bars[0].high_price == 110.0
    assert bars[0].low_price == 90.0
    assert bars[0].close_price == 105.0
    assert bars[0].volume == 1000.0

def test_get_bar_overview(test_db_path):
    """测试获取K线数据概览"""
    # 创建数据管理器
    manager = DataManager()
    
    # 创建测试数据
    now = datetime.now()
    bar = BarData(
        symbol="TEST",
        exchange=Exchange.NASDAQ,
        datetime=now,
        interval=Interval.DAILY,
        open_price=100.0,
        high_price=110.0,
        low_price=90.0,
        close_price=105.0,
        volume=1000.0,
        open_interest=0.0
    )
    
    # 保存数据
    manager.save_bar_data([bar])
    
    # 获取数据概览
    overviews = manager.get_bar_overview()
    
    # 验证数据概览
    assert len(overviews) > 0
    
    # 找到我们刚刚添加的数据
    found = False
    for overview in overviews:
        if overview['symbol'] == "TEST" and overview['exchange'] == "NASDAQ" and overview['interval'] == "d":
            found = True
            assert overview['count'] == 1
            break
    
    assert found, "未找到刚刚添加的数据概览"

def test_delete_bar_data(test_db_path):
    """测试删除K线数据"""
    # 创建数据管理器
    manager = DataManager()
    
    # 创建测试数据
    now = datetime.now()
    bar = BarData(
        symbol="TEST",
        exchange=Exchange.NASDAQ,
        datetime=now,
        interval=Interval.DAILY,
        open_price=100.0,
        high_price=110.0,
        low_price=90.0,
        close_price=105.0,
        volume=1000.0,
        open_interest=0.0
    )
    
    # 保存数据
    manager.save_bar_data([bar])
    
    # 删除数据
    count = manager.delete_bar_data(
        symbol="TEST",
        exchange=Exchange.NASDAQ,
        interval=Interval.DAILY
    )
    
    # 验证删除结果
    assert count == 1
    
    # 尝试加载已删除的数据
    start = now - timedelta(days=1)
    end = now + timedelta(days=1)
    bars = manager.load_bar_data(
        symbol="TEST",
        exchange=Exchange.NASDAQ,
        interval=Interval.DAILY,
        start=start,
        end=end
    )
    
    # 验证数据已被删除
    assert len(bars) == 0
