"""
SimpleTrade数据管理模块

提供数据管理功能，包括数据下载、导入、导出、查询和管理。
直接使用vnpy的数据模型和数据管理功能。
"""

# 使用vnpy的数据模型
# 导入数据模型
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval

# 导入数据管理器
from .manager import DataManager
