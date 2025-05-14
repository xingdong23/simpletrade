"""
TA-Lib适配器

使用pandas-ta实现TA-Lib的API，作为TA-Lib的替代品。
这个模块可以通过sys.modules['talib'] = TalibAdapter来替换系统中的talib模块。
"""

import numpy as np
import pandas as pd
import pandas_ta as ta
from typing import Tuple, Union, Optional

class TalibAdapter:
    """
    TA-Lib适配器类
    
    实现了TA-Lib的常用函数，使用pandas-ta作为后端。
    """
    
    # 移动平均线
    @staticmethod
    def SMA(close, timeperiod=30):
        """简单移动平均线"""
        df = pd.DataFrame({"close": close})
        result = ta.sma(df["close"], length=timeperiod).values
        return np.nan_to_num(result, nan=0.0)
    
    @staticmethod
    def EMA(close, timeperiod=30):
        """指数移动平均线"""
        df = pd.DataFrame({"close": close})
        result = ta.ema(df["close"], length=timeperiod).values
        return np.nan_to_num(result, nan=0.0)
    
    @staticmethod
    def WMA(close, timeperiod=30):
        """加权移动平均线"""
        df = pd.DataFrame({"close": close})
        result = ta.wma(df["close"], length=timeperiod).values
        return np.nan_to_num(result, nan=0.0)
    
    # MACD
    @staticmethod
    def MACD(close, fastperiod=12, slowperiod=26, signalperiod=9):
        """MACD指标"""
        df = pd.DataFrame({"close": close})
        macd_result = ta.macd(df["close"], fast=fastperiod, slow=slowperiod, signal=signalperiod)
        
        macd_line = macd_result[f"MACD_{fastperiod}_{slowperiod}_{signalperiod}"].values
        signal_line = macd_result[f"MACDs_{fastperiod}_{slowperiod}_{signalperiod}"].values
        hist = macd_result[f"MACDh_{fastperiod}_{slowperiod}_{signalperiod}"].values
        
        macd_line = np.nan_to_num(macd_line, nan=0.0)
        signal_line = np.nan_to_num(signal_line, nan=0.0)
        hist = np.nan_to_num(hist, nan=0.0)
        
        return macd_line, signal_line, hist
    
    # RSI
    @staticmethod
    def RSI(close, timeperiod=14):
        """相对强弱指数"""
        df = pd.DataFrame({"close": close})
        result = ta.rsi(df["close"], length=timeperiod).values
        return np.nan_to_num(result, nan=0.0)
    
    # 布林带
    @staticmethod
    def BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0):
        """布林带"""
        df = pd.DataFrame({"close": close})
        boll_result = ta.bbands(df["close"], length=timeperiod, std=nbdevup)
        
        upper = boll_result[f"BBU_{timeperiod}_{nbdevup}"].values
        middle = boll_result[f"BBM_{timeperiod}_{nbdevup}"].values
        lower = boll_result[f"BBL_{timeperiod}_{nbdevup}"].values
        
        upper = np.nan_to_num(upper, nan=0.0)
        middle = np.nan_to_num(middle, nan=0.0)
        lower = np.nan_to_num(lower, nan=0.0)
        
        return upper, middle, lower
    
    # ATR
    @staticmethod
    def ATR(high, low, close, timeperiod=14):
        """平均真实范围"""
        df = pd.DataFrame({
            "high": high,
            "low": low,
            "close": close
        })
        
        result = ta.atr(df["high"], df["low"], df["close"], length=timeperiod).values
        return np.nan_to_num(result, nan=0.0)
    
    # KDJ
    @staticmethod
    def STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0):
        """随机指标"""
        df = pd.DataFrame({
            "high": high,
            "low": low,
            "close": close
        })
        
        stoch_result = ta.stoch(df["high"], df["low"], df["close"], k=fastk_period, d=slowd_period, smooth_k=slowk_period)
        
        slowk = stoch_result[f"STOCHk_{fastk_period}_{slowk_period}_{slowd_period}"].values
        slowd = stoch_result[f"STOCHd_{fastk_period}_{slowk_period}_{slowd_period}"].values
        
        slowk = np.nan_to_num(slowk, nan=0.0)
        slowd = np.nan_to_num(slowd, nan=0.0)
        
        return slowk, slowd
    
    # CCI
    @staticmethod
    def CCI(high, low, close, timeperiod=14):
        """商品通道指数"""
        df = pd.DataFrame({
            "high": high,
            "low": low,
            "close": close
        })
        
        result = ta.cci(df["high"], df["low"], df["close"], length=timeperiod).values
        return np.nan_to_num(result, nan=0.0)
    
    # ADX
    @staticmethod
    def ADX(high, low, close, timeperiod=14):
        """平均方向指数"""
        df = pd.DataFrame({
            "high": high,
            "low": low,
            "close": close
        })
        
        result = ta.adx(df["high"], df["low"], df["close"], length=timeperiod).values
        return np.nan_to_num(result, nan=0.0)
    
    # 更多指标...

# 导出所有函数到模块级别
SMA = TalibAdapter.SMA
EMA = TalibAdapter.EMA
WMA = TalibAdapter.WMA
MACD = TalibAdapter.MACD
RSI = TalibAdapter.RSI
BBANDS = TalibAdapter.BBANDS
ATR = TalibAdapter.ATR
STOCH = TalibAdapter.STOCH
CCI = TalibAdapter.CCI
ADX = TalibAdapter.ADX

# 使用方法:
# import sys
# sys.modules['talib'] = TalibAdapter
