"""
简单的回测API测试脚本
"""

import sys
import os
import json
import requests
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_backtest_api():
    """测试回测API"""
    # 回测参数
    data = {
        "strategy_id": 5,  # 整数类型
        "symbol": "AAPL",
        "exchange": "NASDAQ",
        "interval": "1d",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
        "initial_capital": 1000000.0,  # 浮点数类型
        "rate": 0.0001,  # 浮点数类型
        "slippage": 0.0,  # 浮点数类型
        "parameters": {
            "initial_grid": 2,  # 整数类型
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
        },
        "user_id": 1  # 添加user_id字段
    }

    # 发送请求
    url = "http://localhost:8003/api/strategies/backtest"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # 如果响应状态码不是200，抛出异常

        # 解析响应
        result = response.json()

        # 打印结果
        print(json.dumps(result, indent=4))

        # 检查结果
        if result["success"]:
            print("\n回测成功！")

            # 检查是否有错误
            if "data" in result and "error" in result["data"] and result["data"]["error"]:
                print(f"错误: {result['data']['error']}")

            # 检查统计指标
            if "data" in result and "statistics" in result["data"]:
                stats = result["data"]["statistics"]
                if stats:
                    print("\n统计指标:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                else:
                    print("\n没有统计指标")

            # 检查每日结果
            if "data" in result and "daily_results" in result["data"]:
                daily_results = result["data"]["daily_results"]
                if daily_results:
                    print(f"\n每日结果 (共 {len(daily_results)} 条):")
                    for i, day in enumerate(daily_results[:5]):  # 只打印前5条
                        print(f"  {i+1}. {day}")
                    if len(daily_results) > 5:
                        print(f"  ... 还有 {len(daily_results) - 5} 条")
                else:
                    print("\n没有每日结果")

            # 检查交易记录
            if "data" in result and "trades" in result["data"]:
                trades = result["data"]["trades"]
                if trades:
                    print(f"\n交易记录 (共 {len(trades)} 条):")
                    for i, trade in enumerate(trades[:5]):  # 只打印前5条
                        print(f"  {i+1}. {trade}")
                    if len(trades) > 5:
                        print(f"  ... 还有 {len(trades) - 5} 条")
                else:
                    print("\n没有交易记录")
        else:
            print(f"\n回测失败: {result.get('message', '未知错误')}")

        return result
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

if __name__ == "__main__":
    test_backtest_api()
