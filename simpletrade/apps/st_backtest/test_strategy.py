"""
测试策略
"""

from datetime import datetime
from typing import Dict, List, Any

class TestStrategy:
    """测试策略"""

    def __init__(self, engine, name, vt_symbol, setting=None):
        """构造函数"""
        self.engine = engine
        self.name = name
        self.vt_symbol = vt_symbol
        self.setting = setting or {}
        self.pos = 0
        self.trades = []
        self.daily_results = []

    def on_init(self):
        """初始化策略"""
        print(f"策略初始化: {self.name}")

    def on_start(self):
        """启动策略"""
        print(f"策略启动: {self.name}")

    def on_stop(self):
        """停止策略"""
        print(f"策略停止: {self.name}")

    def on_tick(self, tick):
        """Tick数据回调"""
        pass

    def on_bar(self, bar):
        """K线数据回调"""
        # 简单的策略：每10个K线买入一次，每20个K线卖出一次
        if len(self.engine.history_bars) % 10 == 0:
            self.buy(bar.close_price, 1)
        elif len(self.engine.history_bars) % 20 == 0:
            self.sell(bar.close_price, 1)

    def buy(self, price, volume):
        """买入"""
        self.pos += volume
        trade = {
            "datetime": datetime.now(),
            "symbol": self.vt_symbol,
            "exchange": "MOCK",
            "direction": "LONG",
            "offset": "OPEN",
            "price": price,
            "volume": volume,
            "vt_tradeid": f"MOCK-{len(self.trades)}",
            "pnl": 0.0
        }
        self.trades.append(trade)
        print(f"买入: {price} x {volume}")

    def sell(self, price, volume):
        """卖出"""
        self.pos -= volume
        trade = {
            "datetime": datetime.now(),
            "symbol": self.vt_symbol,
            "exchange": "MOCK",
            "direction": "SHORT",
            "offset": "CLOSE",
            "price": price,
            "volume": volume,
            "vt_tradeid": f"MOCK-{len(self.trades)}",
            "pnl": 0.0
        }
        self.trades.append(trade)
        print(f"卖出: {price} x {volume}")

    def update_daily_close(self, price):
        """更新每日收盘价"""
        daily_result = {
            "date": datetime.now().date(),
            "close_price": price,
            "pos": self.pos,
            "net_pnl": 0.0,
            "balance": self.engine.capital
        }
        self.daily_results.append(daily_result)
        print(f"每日收盘: {price}, 持仓: {self.pos}")
