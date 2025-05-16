"""
测试回测服务
"""

import sys
import os
import json
from datetime import datetime, date
import pandas as pd
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入需要测试的模块
from simpletrade.apps.st_backtest.service import BacktestService

def test_backtest_service():
    """测试回测服务"""
    # 创建回测服务实例
    backtest_service = BacktestService()

    # 回测参数
    strategy_id = 5
    symbol = "AAPL"
    exchange = "NASDAQ"
    interval = "1d"
    start_date = date(2020, 1, 1)
    end_date = date(2020, 12, 31)
    initial_capital = 1000000.0
    rate = 0.0001
    slippage = 0.0
    parameters = {
        "initial_grid": 2,
        "grid_min": 1,
        "grid_max": 4,
        "flip_threshold_factor": 0.2,
        "position_scale_factor": 0.2,
        "min_trade_amount": 20,
        "min_position_percent": 0.05,
        "max_position_percent": 0.15,
        "cooldown": 60,
        "safety_margin": 0.95,
        "max_drawdown": -0.15,
        "daily_loss_limit": -0.05,
        "max_position_ratio": 0.9,
        "min_position_ratio": 0.1,
        "volatility_window": 20,
        "s1_lookback": 52,
        "s1_sell_target_pct": 0.5,
        "s1_buy_target_pct": 0.7
    }
    user_id = 1

    # 运行回测
    result = backtest_service.run_backtest(
        strategy_id=strategy_id,
        symbol=symbol,
        exchange=exchange,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        rate=rate,
        slippage=slippage,
        parameters=parameters,
        user_id=user_id
    )

    # 打印结果
    # 处理不可序列化的对象
    def process_result(obj):
        if isinstance(obj, dict):
            return {k: process_result(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [process_result(item) for item in obj]
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        else:
            return obj

    processed_result = process_result(result)
    print(json.dumps(processed_result, indent=4))

    # 检查结果
    if result["success"]:
        print("\n回测成功！")

        # 检查统计指标
        if "statistics" in result and result["statistics"]:
            print("\n统计指标:")
            for key, value in result["statistics"].items():
                print(f"  {key}: {value}")
        else:
            print("\n没有统计指标")

        # 检查每日结果
        if "daily_results" in result and result["daily_results"]:
            print(f"\n每日结果 (共 {len(result['daily_results'])} 条):")
            for i, day in enumerate(result["daily_results"][:5]):  # 只打印前5条
                print(f"  {i+1}. {day}")
            if len(result["daily_results"]) > 5:
                print(f"  ... 还有 {len(result['daily_results']) - 5} 条")
        else:
            print("\n没有每日结果")

        # 检查交易记录
        if "trades" in result and result["trades"]:
            print(f"\n交易记录 (共 {len(result['trades'])} 条):")
            for i, trade in enumerate(result["trades"][:5]):  # 只打印前5条
                print(f"  {i+1}. {trade}")
            if len(result["trades"]) > 5:
                print(f"  ... 还有 {len(result['trades']) - 5} 条")
        else:
            print("\n没有交易记录")
    else:
        print(f"\n回测失败: {result.get('error', '未知错误')}")

    return result

if __name__ == "__main__":
    test_backtest_service()
