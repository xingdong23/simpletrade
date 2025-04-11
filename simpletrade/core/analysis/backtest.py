"""
SimpleTrade回测模块

提供策略回测功能。
直接使用vnpy的数据模型。
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Callable

# 导入vnpy的数据模型
from vnpy.trader.object import BarData
from .indicators import bars_to_dataframe, calculate_indicators


class BacktestResult:
    """回测结果"""

    def __init__(self, df: pd.DataFrame, initial_capital: float = 100000.0):
        """初始化

        参数:
            df: 回测数据DataFrame
            initial_capital: 初始资金
        """
        self.df = df
        self.initial_capital = initial_capital

        # 计算回测结果
        self.calculate_results()

    def calculate_results(self):
        """计算回测结果"""
        df = self.df

        # 计算每笔交易的收益
        df["trade_profit"] = 0.0
        df.loc[df["position_change"] == -1, "trade_profit"] = df["close"] - df["entry_price"]
        df.loc[df["position_change"] == 1, "trade_profit"] = df["entry_price"] - df["close"]

        # 计算累计收益
        df["cumulative_profit"] = df["trade_profit"].cumsum()

        # 计算资金曲线
        df["capital"] = self.initial_capital + df["cumulative_profit"]

        # 计算回撤
        df["drawdown"] = df["capital"].cummax() - df["capital"]
        df["drawdown_pct"] = df["drawdown"] / df["capital"].cummax()

        # 计算统计指标
        self.total_trades = (df["position_change"] != 0).sum()
        self.winning_trades = (df["trade_profit"] > 0).sum()
        self.losing_trades = (df["trade_profit"] < 0).sum()

        if self.total_trades > 0:
            self.win_rate = self.winning_trades / self.total_trades
        else:
            self.win_rate = 0.0

        self.total_profit = df["trade_profit"].sum()
        self.max_drawdown = df["drawdown"].max()
        self.max_drawdown_pct = df["drawdown_pct"].max()

        if self.initial_capital > 0:
            self.return_pct = self.total_profit / self.initial_capital * 100
        else:
            self.return_pct = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        返回:
            Dict[str, Any]: 回测结果字典
        """
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "total_profit": self.total_profit,
            "return_pct": self.return_pct,
            "max_drawdown": self.max_drawdown,
            "max_drawdown_pct": self.max_drawdown_pct,
            "initial_capital": self.initial_capital,
            "final_capital": self.initial_capital + self.total_profit
        }


def backtest_strategy(
    bars: List[BarData],
    strategy_name: str,
    strategy_params: Dict[str, Any],
    indicators: List[Dict[str, Any]] = None,
    initial_capital: float = 100000.0
) -> BacktestResult:
    """回测策略

    参数:
        bars: K线数据列表
        strategy_name: 策略名称
        strategy_params: 策略参数
        indicators: 技术指标配置列表
        initial_capital: 初始资金

    返回:
        BacktestResult: 回测结果
    """
    if not bars:
        return None

    # 转换为DataFrame
    df = bars_to_dataframe(bars)

    # 计算技术指标
    if indicators:
        df = calculate_indicators(bars, indicators)

    # 初始化策略
    if strategy_name == "MovingAverageCrossover":
        df = moving_average_crossover_strategy(df, strategy_params)
    elif strategy_name == "RSIStrategy":
        df = rsi_strategy(df, strategy_params)
    elif strategy_name == "BollingerBandsStrategy":
        df = bollinger_bands_strategy(df, strategy_params)
    else:
        raise ValueError(f"不支持的策略: {strategy_name}")

    # 计算回测结果
    result = BacktestResult(df, initial_capital)

    return result


def moving_average_crossover_strategy(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    """移动平均线交叉策略

    参数:
        df: K线数据DataFrame
        params: 策略参数

    返回:
        pd.DataFrame: 包含策略信号的DataFrame
    """
    fast_period = params.get("fast_period", 5)
    slow_period = params.get("slow_period", 20)

    # 计算移动平均线
    df[f"SMA_{fast_period}"] = df["close"].rolling(fast_period).mean()
    df[f"SMA_{slow_period}"] = df["close"].rolling(slow_period).mean()

    # 计算信号
    df["signal"] = 0
    df.loc[df[f"SMA_{fast_period}"] > df[f"SMA_{slow_period}"], "signal"] = 1
    df.loc[df[f"SMA_{fast_period}"] < df[f"SMA_{slow_period}"], "signal"] = -1

    # 计算仓位变化
    df["position"] = df["signal"]
    df["position_change"] = df["position"].diff()

    # 计算入场价格
    df["entry_price"] = np.nan
    df.loc[df["position_change"] != 0, "entry_price"] = df["close"]

    return df


def rsi_strategy(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    """RSI策略

    参数:
        df: K线数据DataFrame
        params: 策略参数

    返回:
        pd.DataFrame: 包含策略信号的DataFrame
    """
    period = params.get("period", 14)
    overbought = params.get("overbought", 70)
    oversold = params.get("oversold", 30)

    # 计算RSI
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    df[f"RSI_{period}"] = 100 - (100 / (1 + rs))

    # 计算信号
    df["signal"] = 0
    df.loc[df[f"RSI_{period}"] < oversold, "signal"] = 1
    df.loc[df[f"RSI_{period}"] > overbought, "signal"] = -1

    # 计算仓位变化
    df["position"] = df["signal"]
    df["position_change"] = df["position"].diff()

    # 计算入场价格
    df["entry_price"] = np.nan
    df.loc[df["position_change"] != 0, "entry_price"] = df["close"]

    return df


def bollinger_bands_strategy(df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
    """布林带策略

    参数:
        df: K线数据DataFrame
        params: 策略参数

    返回:
        pd.DataFrame: 包含策略信号的DataFrame
    """
    period = params.get("period", 20)
    std_dev = params.get("std_dev", 2)

    # 计算布林带
    df[f"BOLL_Middle"] = df["close"].rolling(period).mean()
    df[f"BOLL_Std"] = df["close"].rolling(period).std()
    df[f"BOLL_Upper"] = df[f"BOLL_Middle"] + std_dev * df[f"BOLL_Std"]
    df[f"BOLL_Lower"] = df[f"BOLL_Middle"] - std_dev * df[f"BOLL_Std"]

    # 计算信号
    df["signal"] = 0
    df.loc[df["close"] < df[f"BOLL_Lower"], "signal"] = 1
    df.loc[df["close"] > df[f"BOLL_Upper"], "signal"] = -1

    # 计算仓位变化
    df["position"] = df["signal"]
    df["position_change"] = df["position"].diff()

    # 计算入场价格
    df["entry_price"] = np.nan
    df.loc[df["position_change"] != 0, "entry_price"] = df["close"]

    return df
