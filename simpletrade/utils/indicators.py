"""
技术指标工具模块

使用pandas-ta库实现常用技术指标，作为TA-Lib的替代品。
"""

import pandas as pd
import pandas_ta as ta
from typing import Tuple, List, Dict, Any, Union, Optional

def calculate_sma(df: pd.DataFrame, column: str = 'close', periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
    """
    计算简单移动平均线
    
    参数:
        df (pd.DataFrame): 包含价格数据的DataFrame
        column (str): 用于计算的列名，默认为'close'
        periods (List[int]): 周期列表，默认为[5, 10, 20, 60]
        
    返回:
        pd.DataFrame: 添加了SMA列的DataFrame
    """
    df_copy = df.copy()
    for period in periods:
        df_copy[f'ma{period}'] = ta.sma(df_copy[column], length=period)
    return df_copy

def calculate_ema(df: pd.DataFrame, column: str = 'close', periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
    """
    计算指数移动平均线
    
    参数:
        df (pd.DataFrame): 包含价格数据的DataFrame
        column (str): 用于计算的列名，默认为'close'
        periods (List[int]): 周期列表，默认为[5, 10, 20, 60]
        
    返回:
        pd.DataFrame: 添加了EMA列的DataFrame
    """
    df_copy = df.copy()
    for period in periods:
        df_copy[f'ema{period}'] = ta.ema(df_copy[column], length=period)
    return df_copy

def calculate_macd(df: pd.DataFrame, column: str = 'close', 
                  fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    计算MACD指标
    
    参数:
        df (pd.DataFrame): 包含价格数据的DataFrame
        column (str): 用于计算的列名，默认为'close'
        fast (int): 快线周期，默认为12
        slow (int): 慢线周期，默认为26
        signal (int): 信号线周期，默认为9
        
    返回:
        pd.DataFrame: 添加了MACD指标列的DataFrame
    """
    df_copy = df.copy()
    macd = ta.macd(df_copy[column], fast=fast, slow=slow, signal=signal)
    df_copy['macd'] = macd['MACD_12_26_9']
    df_copy['macd_signal'] = macd['MACDs_12_26_9']
    df_copy['macd_hist'] = macd['MACDh_12_26_9']
    return df_copy

def calculate_rsi(df: pd.DataFrame, column: str = 'close', period: int = 14) -> pd.DataFrame:
    """
    计算RSI指标
    
    参数:
        df (pd.DataFrame): 包含价格数据的DataFrame
        column (str): 用于计算的列名，默认为'close'
        period (int): 周期，默认为14
        
    返回:
        pd.DataFrame: 添加了RSI列的DataFrame
    """
    df_copy = df.copy()
    df_copy['rsi'] = ta.rsi(df_copy[column], length=period)
    return df_copy

def calculate_bollinger_bands(df: pd.DataFrame, column: str = 'close', 
                             period: int = 20, std: float = 2.0) -> pd.DataFrame:
    """
    计算布林带
    
    参数:
        df (pd.DataFrame): 包含价格数据的DataFrame
        column (str): 用于计算的列名，默认为'close'
        period (int): 周期，默认为20
        std (float): 标准差倍数，默认为2.0
        
    返回:
        pd.DataFrame: 添加了布林带列的DataFrame
    """
    df_copy = df.copy()
    bbands = ta.bbands(df_copy[column], length=period, std=std)
    df_copy['bb_upper'] = bbands['BBU_20_2.0']
    df_copy['bb_middle'] = bbands['BBM_20_2.0']
    df_copy['bb_lower'] = bbands['BBL_20_2.0']
    return df_copy

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    计算平均真实范围(ATR)
    
    参数:
        df (pd.DataFrame): 包含价格数据的DataFrame，必须包含'high', 'low', 'close'列
        period (int): 周期，默认为14
        
    返回:
        pd.DataFrame: 添加了ATR列的DataFrame
    """
    df_copy = df.copy()
    df_copy['atr'] = ta.atr(df_copy['high'], df_copy['low'], df_copy['close'], length=period)
    return df_copy

def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算所有常用指标
    
    参数:
        df (pd.DataFrame): 包含价格数据的DataFrame，必须包含'open', 'high', 'low', 'close', 'volume'列
        
    返回:
        pd.DataFrame: 添加了所有指标列的DataFrame
    """
    df_copy = df.copy()
    
    # 计算移动平均线
    df_copy = calculate_sma(df_copy)
    df_copy = calculate_ema(df_copy)
    
    # 计算MACD
    df_copy = calculate_macd(df_copy)
    
    # 计算RSI
    df_copy = calculate_rsi(df_copy)
    
    # 计算布林带
    df_copy = calculate_bollinger_bands(df_copy)
    
    # 计算ATR
    df_copy = calculate_atr(df_copy)
    
    # 添加更多指标...
    # 随机指标
    stoch = ta.stoch(df_copy['high'], df_copy['low'], df_copy['close'], k=14, d=3, smooth_k=3)
    df_copy['stoch_k'] = stoch['STOCHk_14_3_3']
    df_copy['stoch_d'] = stoch['STOCHd_14_3_3']
    
    # 相对强弱指数变化率
    df_copy['rsi_change'] = ta.rsi(df_copy['close'], length=14).diff()
    
    # 成交量加权平均价格
    df_copy['vwap'] = ta.vwap(df_copy['high'], df_copy['low'], df_copy['close'], df_copy['volume'])
    
    return df_copy
