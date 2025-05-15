"""
CTA策略回测模块
"""

from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum

from vnpy.trader.object import BarData

class BacktestingMode(Enum):
    """回测模式"""
    BAR = 1
    TICK = 2

class BacktestingEngine:
    """回测引擎"""

    def __init__(self):
        """构造函数"""
        self.strategy_class = None
        self.strategy = None
        self.start = None
        self.end = None
        self.rate = 0
        self.slippage = 0
        self.size = 1
        self.pricetick = 0
        self.capital = 1_000_000

    def set_parameters(
        self,
        vt_symbol: str,
        interval: str,
        start: datetime,
        rate: float,
        slippage: float,
        size: float,
        pricetick: float,
        capital: int = 0,
        end: datetime = None,
    ):
        """设置参数"""
        self.vt_symbol = vt_symbol
        self.interval = interval
        self.start = start
        self.rate = rate
        self.slippage = slippage
        self.size = size
        self.pricetick = pricetick
        self.capital = capital
        self.end = end

    def add_strategy(self, strategy_class, setting=None):
        """添加策略"""
        self.strategy_class = strategy_class
        self.strategy = strategy_class(
            self, strategy_class.__name__, self.vt_symbol, setting
        )

    def load_data(self):
        """加载数据"""
        pass

    def run_backtesting(self):
        """运行回测"""
        pass

    def calculate_result(self):
        """计算结果"""
        pass

    def calculate_statistics(self):
        """计算统计指标"""
        pass

    def show_chart(self):
        """显示图表"""
        pass

    def update_daily_close(self, price: float):
        """更新每日收盘价"""
        pass

    def run_optimization(self, optimization_setting, output=True):
        """运行参数优化"""
        pass

    def run_bf_optimization(self, optimization_setting, output=True):
        """运行暴力优化"""
        pass

    def run_ga_optimization(self, optimization_setting, population_size=100, ngen_size=30, output=True):
        """运行遗传算法优化"""
        pass

class OptimizationSetting:
    """参数优化设置"""

    def __init__(self):
        """构造函数"""
        self.params = {}
        self.target_name = ""

    def add_parameter(
        self, name: str, start: float, end: float = None, step: float = None
    ):
        """添加参数"""
        if not end and not step:
            self.params[name] = [start]
            return self

        if start >= end:
            return self

        if step <= 0:
            return self

        value = start
        value_list = []

        while value <= end:
            value_list.append(value)
            value += step

        self.params[name] = value_list
        return self

    def set_target(self, target_name: str):
        """设置优化目标"""
        self.target_name = target_name
        return self

    def generate_settings(self):
        """生成参数设置"""
        settings = []

        if not self.params:
            return settings

        for name, values in self.params.items():
            for value in values:
                setting = {name: value}
                settings.append(setting)

        return settings
