#!/usr/bin/env python
"""
分析功能测试脚本

用于测试数据分析功能。
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
from simpletrade.core.analysis import calculate_indicators, backtest_strategy

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
    
    # 生成过去100天的日线数据
    for i in range(100):
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
    
    return db_path, bars

def test_indicators():
    """测试技术指标计算"""
    print("测试技术指标计算")
    
    # 生成测试数据
    db_path, bars = generate_test_data()
    
    # 定义技术指标
    indicators = [
        {"name": "SMA", "params": {"period": 5}},
        {"name": "SMA", "params": {"period": 20}},
        {"name": "EMA", "params": {"period": 5}},
        {"name": "EMA", "params": {"period": 20}},
        {"name": "MACD", "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        {"name": "RSI", "params": {"period": 14}},
        {"name": "BOLL", "params": {"period": 20, "std_dev": 2}}
    ]
    
    # 计算技术指标
    df = calculate_indicators(bars, indicators)
    
    # 打印结果
    print("\n技术指标计算结果:")
    print(df.tail())
    
    # 清理临时文件
    if os.path.exists(db_path):
        os.remove(db_path)

def test_backtest():
    """测试策略回测"""
    print("测试策略回测")
    
    # 生成测试数据
    db_path, bars = generate_test_data()
    
    # 定义策略
    strategies = [
        {
            "name": "MovingAverageCrossover",
            "params": {"fast_period": 5, "slow_period": 20}
        },
        {
            "name": "RSIStrategy",
            "params": {"period": 14, "overbought": 70, "oversold": 30}
        },
        {
            "name": "BollingerBandsStrategy",
            "params": {"period": 20, "std_dev": 2}
        }
    ]
    
    # 运行回测
    for strategy in strategies:
        print(f"\n回测策略: {strategy['name']}")
        
        result = backtest_strategy(
            bars=bars,
            strategy_name=strategy["name"],
            strategy_params=strategy["params"],
            initial_capital=100000.0
        )
        
        # 打印回测结果
        print("回测结果:")
        for key, value in result.to_dict().items():
            print(f"{key}: {value}")
    
    # 清理临时文件
    if os.path.exists(db_path):
        os.remove(db_path)

def test_api():
    """测试API功能"""
    print("测试API功能")
    
    # 生成测试数据
    db_path, bars = generate_test_data()
    
    # 创建FastAPI应用
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="SimpleTrade Analysis API Test")
    
    # 添加路由
    from simpletrade.api.analysis import router as analysis_router
    app.include_router(analysis_router)
    
    # 启动服务
    print("API服务已启动，访问 http://localhost:8000/docs 查看API文档")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    # 清理临时文件
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "indicators":
            test_indicators()
        elif sys.argv[1] == "backtest":
            test_backtest()
        elif sys.argv[1] == "api":
            test_api()
        else:
            print(f"未知的测试类型: {sys.argv[1]}")
            print("可用的测试类型: indicators, backtest, api")
    else:
        print("请指定测试类型: indicators, backtest 或 api")
        print("示例: python scripts/test_analysis.py indicators")
        print("示例: python scripts/test_analysis.py backtest")
        print("示例: python scripts/test_analysis.py api")
