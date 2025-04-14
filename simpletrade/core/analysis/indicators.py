"""
SimpleTrade技术指标模块

提供技术指标计算功能。
直接使用vnpy的数据模型。
使用纯Python实现，不依赖talib库。
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Union
import logging

# 导入vnpy数据模型
from vnpy.trader.object import BarData

# 配置日志
logger = logging.getLogger("simpletrade.core.analysis.indicators")


def calculate_indicators(bars: List[BarData], indicators: List[Dict[str, Any]]) -> pd.DataFrame:
    """计算技术指标

    参数:
        bars: K线数据列表
        indicators: 技术指标配置列表，每个配置包含指标名称和参数

    返回:
        pd.DataFrame: 包含K线数据和技术指标的DataFrame
    """
    if not bars:
        return pd.DataFrame()

    # 转换为DataFrame
    df = bars_to_dataframe(bars)

    # 计算技术指标
    for indicator in indicators:
        name = indicator.get("name", "")
        params = indicator.get("params", {})

        if name == "SMA":
            period = params.get("period", 20)
            df[f"SMA_{period}"] = calculate_sma(df, period)
        elif name == "EMA":
            period = params.get("period", 20)
            df[f"EMA_{period}"] = calculate_ema(df, period)
        elif name == "MACD":
            fast_period = params.get("fast_period", 12)
            slow_period = params.get("slow_period", 26)
            signal_period = params.get("signal_period", 9)
            macd, signal, hist = calculate_macd(df, fast_period, slow_period, signal_period)
            df[f"MACD"] = macd
            df[f"MACD_Signal"] = signal
            df[f"MACD_Hist"] = hist
        elif name == "RSI":
            period = params.get("period", 14)
            df[f"RSI_{period}"] = calculate_rsi(df, period)
        elif name == "BOLL":
            period = params.get("period", 20)
            std_dev = params.get("std_dev", 2)
            upper, middle, lower = calculate_bollinger_bands(df, period, std_dev)
            df[f"BOLL_Upper"] = upper
            df[f"BOLL_Middle"] = middle
            df[f"BOLL_Lower"] = lower

    return df

def bars_to_dataframe(bars: List[BarData]) -> pd.DataFrame:
    """将K线数据列表转换为DataFrame

    参数:
        bars: K线数据列表

    返回:
        pd.DataFrame: K线数据DataFrame
    """
    data = []
    for bar in bars:
        data.append({
            "datetime": bar.datetime,
            "open": bar.open_price,
            "high": bar.high_price,
            "low": bar.low_price,
            "close": bar.close_price,
            "volume": bar.volume,
            "open_interest": bar.open_interest
        })

    df = pd.DataFrame(data)
    df.set_index("datetime", inplace=True)
    return df

def calculate_sma(df: pd.DataFrame, period: int) -> pd.Series:
    """计算简单移动平均线

    参数:
        df: K线数据DataFrame
        period: 周期

    返回:
        pd.Series: 简单移动平均线
    """
    return df["close"].rolling(period).mean()

def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
    """计算指数移动平均线

    参数:
        df: K线数据DataFrame
        period: 周期

    返回:
        pd.Series: 指数移动平均线
    """
    return df["close"].ewm(span=period, adjust=False).mean()

def calculate_macd(df: pd.DataFrame, fast_period: int, slow_period: int, signal_period: int) -> tuple:
    """计算MACD

    参数:
        df: K线数据DataFrame
        fast_period: 快线周期
        slow_period: 慢线周期
        signal_period: 信号线周期

    返回:
        tuple: (MACD线, 信号线, 柱状图)
    """
    ema_fast = df["close"].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow_period, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=signal_period, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def calculate_rsi(df: pd.DataFrame, period: int) -> pd.Series:
    """计算RSI

    参数:
        df: K线数据DataFrame
        period: 周期

    返回:
        pd.Series: RSI
    """
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_bollinger_bands(df: pd.DataFrame, period: int, std_dev: float) -> tuple:
    """计算布林带

    参数:
        df: K线数据DataFrame
        period: 周期
        std_dev: 标准差倍数

    返回:
        tuple: (上轨, 中轨, 下轨)
    """
    middle = df["close"].rolling(period).mean()
    std = df["close"].rolling(period).std()
    upper = middle + std_dev * std
    lower = middle - std_dev * std

    return upper, middle, lower
