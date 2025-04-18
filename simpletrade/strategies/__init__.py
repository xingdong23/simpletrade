"""
策略注册模块

导入所有可用的策略类，并提供策略查找功能。
支持动态发现和注册策略。
"""

import os
import importlib
import inspect
import logging
from typing import Dict, List, Type, Any, Optional

# 导入 vnpy 内置策略
from vnpy_ctastrategy.strategies.atr_rsi_strategy import AtrRsiStrategy
from vnpy_ctastrategy.strategies.boll_channel_strategy import BollChannelStrategy
from vnpy_ctastrategy.strategies.double_ma_strategy import DoubleMaStrategy
from vnpy_ctastrategy.strategies.turtle_signal_strategy import TurtleSignalStrategy
from vnpy_ctastrategy.template import CtaTemplate

# 导入自定义策略
# 如果有自定义策略，可以在这里导入
# from .moving_average_strategy import MovingAverageStrategy

logger = logging.getLogger("simpletrade.strategies")

# 策略字典，用于查找策略类
STRATEGY_CLASS_MAP = {
    "AtrRsiStrategy": AtrRsiStrategy,
    "BollChannelStrategy": BollChannelStrategy,
    "DoubleMaStrategy": DoubleMaStrategy,
    "TurtleSignalStrategy": TurtleSignalStrategy,
    # 添加自定义策略
    # "MovingAverageStrategy": MovingAverageStrategy,
}

# 策略分类
STRATEGY_CATEGORIES = {
    "AtrRsiStrategy": "技术指标",
    "BollChannelStrategy": "通道突破",
    "DoubleMaStrategy": "均线",
    "TurtleSignalStrategy": "趋势跟踪",
}

# 策略描述
STRATEGY_DESCRIPTIONS = {
    "AtrRsiStrategy": "结合ATR和RSI指标的策略，ATR用于止损，RSI用于入场信号",
    "BollChannelStrategy": "布林通道策略，通道上轨突破做多，下轨突破做空",
    "DoubleMaStrategy": "双均线策略，快线上穿慢线做多，下穿做空",
    "TurtleSignalStrategy": "海龟交易法则，基于唐奇安通道的趋势跟踪策略",
}

def discover_strategies():
    """
    自动发现并注册策略类

    扫描当前目录下的所有Python文件，查找继承自CtaTemplate的类，并注册为策略

    Returns:
        Dict[str, Type]: 发现的策略类字典
    """
    discovered = {}

    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 遍历当前目录下的所有Python文件
    for filename in os.listdir(current_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # 去掉.py后缀

            try:
                # 导入模块
                module = importlib.import_module(f"simpletrade.strategies.{module_name}")

                # 查找模块中的所有类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # 检查是否是策略类（继承自CtaTemplate且不是CtaTemplate本身）
                    if (issubclass(obj, CtaTemplate) and
                        obj != CtaTemplate and
                        obj.__module__ == module.__name__):

                        discovered[name] = obj
                        logger.info(f"发现策略类: {name}")
            except Exception as e:
                logger.error(f"加载策略模块 {module_name} 失败: {e}")

    return discovered

def register_strategy(class_name: str, strategy_class: Type,
                     category: str = "未分类", description: str = ""):
    """
    注册策略类

    Args:
        class_name (str): 策略类名
        strategy_class (Type): 策略类
        category (str, optional): 策略分类. 默认为"未分类"
        description (str, optional): 策略描述. 默认为空字符串
    """
    STRATEGY_CLASS_MAP[class_name] = strategy_class
    STRATEGY_CATEGORIES[class_name] = category
    STRATEGY_DESCRIPTIONS[class_name] = description
    logger.info(f"注册策略类: {class_name}, 分类: {category}")

def get_strategy_class(class_name: str) -> Optional[Type]:
    """
    根据策略类名获取策略类

    Args:
        class_name (str): 策略类名

    Returns:
        Type: 策略类，如果找不到则返回None
    """
    return STRATEGY_CLASS_MAP.get(class_name)

def get_strategy_class_names() -> List[str]:
    """
    获取所有可用的策略类名

    Returns:
        List[str]: 策略类名列表
    """
    return list(STRATEGY_CLASS_MAP.keys())

def get_strategy_category(class_name: str) -> str:
    """
    获取策略分类

    Args:
        class_name (str): 策略类名

    Returns:
        str: 策略分类，如果找不到则返回"未分类"
    """
    return STRATEGY_CATEGORIES.get(class_name, "未分类")

def get_strategy_description(class_name: str) -> str:
    """
    获取策略描述

    Args:
        class_name (str): 策略类名

    Returns:
        str: 策略描述，如果找不到则返回空字符串
    """
    return STRATEGY_DESCRIPTIONS.get(class_name, "")

def get_strategy_class_details() -> List[Dict[str, Any]]:
    """
    获取所有策略类的详细信息

    Returns:
        List[Dict[str, Any]]: 策略类详细信息列表，每个元素包含类名、参数等信息
    """
    details = []
    for class_name, strategy_class in STRATEGY_CLASS_MAP.items():
        # 获取策略参数
        parameters = getattr(strategy_class, "parameters", [])
        # 获取策略变量
        variables = getattr(strategy_class, "variables", [])

        # 获取参数默认值
        param_values = {}
        param_types = {}
        param_descriptions = {}

        for param in parameters:
            # 获取默认值
            param_values[param] = getattr(strategy_class, param, None)

            # 尝试获取参数类型和描述（如果有的话）
            param_types[param] = "number"  # 默认类型
            param_descriptions[param] = f"{param}参数"  # 默认描述

        details.append({
            "class_name": class_name,
            "category": get_strategy_category(class_name),
            "description": get_strategy_description(class_name),
            "parameters": parameters,
            "variables": variables,
            "default_values": param_values,
            "param_types": param_types,
            "param_descriptions": param_descriptions
        })

    return details

# 自动发现并注册策略
discovered_strategies = discover_strategies()
for name, cls in discovered_strategies.items():
    if name not in STRATEGY_CLASS_MAP:
        register_strategy(name, cls)
