"""
测试回测API
"""

import sys
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入需要测试的模块
from simpletrade.apps.st_backtest.service import BacktestService
from simpletrade.apps.st_backtest.engine import CTABacktestEngine

# 修复vnpy_custom/vnpy/app/cta_strategy/backtesting.py文件中的load_data方法
def mock_load_data(self):
    """模拟加载数据"""
    from datetime import timedelta
    self.history_bars = []
    for i in range(100):
        bar = MagicMock()
        bar.symbol = self.vt_symbol.split(".")[0]
        bar.exchange = self.vt_symbol.split(".")[1]
        bar.datetime = self.start + timedelta(days=i)
        bar.interval = self.interval
        bar.volume = 1000
        bar.open_price = 100 + i * 0.1
        bar.high_price = 101 + i * 0.1
        bar.low_price = 99 + i * 0.1
        bar.close_price = 100.5 + i * 0.1
        bar.gateway_name = "MOCK"
        self.history_bars.append(bar)

# 修复vnpy_custom/vnpy/app/cta_strategy/backtesting.py文件中的run_backtesting方法
def mock_run_backtesting(self):
    """模拟运行回测"""
    self.strategy.on_init()
    self.strategy.on_start()

    # 遍历所有K线数据
    for bar in self.history_bars:
        self.strategy.on_bar(bar)

    self.strategy.on_stop()

# 修复vnpy_custom/vnpy/app/cta_strategy/backtesting.py文件中的calculate_result方法
def mock_calculate_result(self):
    """模拟计算结果"""
    self.daily_results = []

    # 生成每日结果
    for i, bar in enumerate(self.history_bars):
        daily_result = {
            "date": bar.datetime.date(),
            "close_price": bar.close_price,
            "net_pnl": i * 100,  # 模拟盈亏
            "balance": self.capital + i * 100  # 模拟资金曲线
        }
        self.daily_results.append(daily_result)

    # 生成交易记录
    self.trades = []
    for i in range(10):  # 生成几笔模拟交易
        trade = MagicMock()
        trade.datetime = self.start + timedelta(days=i*10)
        trade.symbol = self.vt_symbol.split(".")[0]
        trade.exchange = MagicMock()
        trade.exchange.value = self.vt_symbol.split(".")[1]
        trade.direction = MagicMock()
        trade.direction.value = "LONG" if i % 2 == 0 else "SHORT"
        trade.offset = MagicMock()
        trade.offset.value = "OPEN" if i % 2 == 0 else "CLOSE"
        trade.price = 100 + i
        trade.volume = 1
        trade.vt_tradeid = f"MOCK-{i}"
        trade.pnl = i * 100
        self.trades.append(trade)

# 修复vnpy_custom/vnpy/app/cta_strategy/backtesting.py文件中的calculate_statistics方法
def mock_calculate_statistics(self):
    """模拟计算统计指标"""
    start_balance = self.capital
    end_balance = self.daily_results[-1]["balance"] if self.daily_results else self.capital

    total_days = len(self.daily_results)
    profit_days = len([result for result in self.daily_results if result["net_pnl"] > 0])
    loss_days = len([result for result in self.daily_results if result["net_pnl"] < 0])

    total_return = (end_balance / start_balance - 1) * 100
    annual_return = total_return / total_days * 365 if total_days > 0 else 0

    return {
        "start_date": self.start.date(),
        "end_date": self.end.date() if self.end else self.start.date(),
        "total_days": total_days,
        "profit_days": profit_days,
        "loss_days": loss_days,
        "capital": self.capital,
        "end_balance": end_balance,
        "max_drawdown": -5.0,  # 模拟最大回撤
        "max_ddpercent": -5.0,  # 模拟最大回撤百分比
        "total_return": total_return,
        "annual_return": annual_return,
        "daily_return": total_return / total_days if total_days > 0 else 0,
        "return_std": 1.0,  # 模拟收益率标准差
        "sharpe_ratio": 2.0,  # 模拟夏普比率
        "return_drawdown_ratio": 2.0,  # 模拟收益回撤比
        "daily_df": self.daily_results,  # 每日结果
        "trades": self.trades  # 交易记录
    }

class TestBacktestAPI(unittest.TestCase):
    """测试回测API"""

    def setUp(self):
        """设置测试环境"""
        self.backtest_service = BacktestService()

        # 模拟参数
        self.strategy_id = 5
        self.symbol = "AAPL"
        self.exchange = "NASDAQ"
        self.interval = "1d"
        self.start_date = "1999-12-31"
        self.end_date = "2020-11-10"
        self.initial_capital = 1000000.0
        self.rate = 0.0001
        self.slippage = 0.0
        self.parameters = {
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

    @patch('simpletrade.apps.st_backtest.engine.CTABacktestEngine.load_data')
    @patch('simpletrade.apps.st_backtest.engine.CTABacktestEngine.run_backtesting')
    @patch('simpletrade.apps.st_backtest.engine.CTABacktestEngine.calculate_result')
    @patch('simpletrade.apps.st_backtest.engine.CTABacktestEngine.calculate_statistics')
    @patch('simpletrade.apps.st_backtest.engine.CTABacktestEngine.get_daily_results')
    @patch('simpletrade.apps.st_backtest.engine.CTABacktestEngine.get_all_trades')
    def test_run_backtest(self, mock_get_all_trades, mock_get_daily_results, mock_calculate_statistics,
                         mock_calculate_result, mock_run_backtesting, mock_load_data):
        """测试运行回测"""
        # 设置模拟函数的返回值
        mock_load_data.side_effect = lambda: None
        mock_run_backtesting.side_effect = lambda: None
        mock_calculate_result.side_effect = lambda: None

        # 模拟每日结果
        daily_results = []
        for i in range(100):
            daily_result = {
                "date": (datetime.strptime(self.start_date, "%Y-%m-%d") + timedelta(days=i)).date(),
                "close_price": 100 + i * 0.1,
                "net_pnl": i * 100,
                "balance": self.initial_capital + i * 100
            }
            daily_results.append(daily_result)
        mock_get_daily_results.return_value = pd.DataFrame(daily_results)

        # 模拟交易记录
        trades = []
        for i in range(10):
            trade = MagicMock()
            trade.datetime = datetime.strptime(self.start_date, "%Y-%m-%d") + timedelta(days=i*10)
            trade.symbol = self.symbol
            trade.exchange = MagicMock()
            trade.exchange.value = self.exchange
            trade.direction = MagicMock()
            trade.direction.value = "LONG" if i % 2 == 0 else "SHORT"
            trade.offset = MagicMock()
            trade.offset.value = "OPEN" if i % 2 == 0 else "CLOSE"
            trade.price = 100 + i
            trade.volume = 1
            trade.vt_tradeid = f"MOCK-{i}"
            trade.pnl = i * 100
            trades.append(trade)
        mock_get_all_trades.return_value = trades

        # 模拟统计指标
        statistics = {
            "start_date": datetime.strptime(self.start_date, "%Y-%m-%d").date(),
            "end_date": datetime.strptime(self.end_date, "%Y-%m-%d").date(),
            "total_days": 100,
            "profit_days": 60,
            "loss_days": 40,
            "capital": self.initial_capital,
            "end_balance": self.initial_capital + 10000,
            "max_drawdown": -5.0,
            "max_ddpercent": -5.0,
            "total_return": 1.0,
            "annual_return": 3.65,
            "daily_return": 0.01,
            "return_std": 1.0,
            "sharpe_ratio": 2.0,
            "return_drawdown_ratio": 2.0,
            "daily_df": daily_results,
            "trades": trades
        }
        mock_calculate_statistics.return_value = statistics

        # 运行回测
        result = self.backtest_service.run_backtest(
            self.strategy_id,
            self.symbol,
            self.exchange,
            self.interval,
            self.start_date,
            self.end_date,
            self.initial_capital,
            self.rate,
            self.slippage,
            self.parameters
        )

        # 验证结果
        self.assertTrue(result["success"])
        self.assertIn("statistics", result)
        self.assertIn("daily_results", result)
        self.assertIn("trades", result)

        # 打印结果
        # 处理MagicMock对象，使其可以被JSON序列化
        def process_result(obj):
            if isinstance(obj, dict):
                return {k: process_result(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [process_result(item) for item in obj]
            elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'MagicMock':
                return f"MagicMock(id={id(obj)})"
            else:
                return obj

        processed_result = process_result(result)
        print(json.dumps(processed_result, indent=4))

if __name__ == "__main__":
    unittest.main()
