"""
策略注册模块

导入所有可用的策略类，并提供策略查找功能。
"""

# 导入 vnpy 内置策略
from vnpy.app.cta_strategy.strategies.atr_rsi_strategy import AtrRsiStrategy
from vnpy.app.cta_strategy.strategies.boll_channel_strategy import BollChannelStrategy
from vnpy.app.cta_strategy.strategies.double_ma_strategy import DoubleMaStrategy
from vnpy.app.cta_strategy.strategies.turtle_signal_strategy import TurtleSignalStrategy

# 导入自定义策略
# 如果有自定义策略，可以在这里导入
# from .moving_average_strategy import MovingAverageStrategy

# 策略字典，用于查找策略类
STRATEGY_CLASS_MAP = {
    "AtrRsiStrategy": AtrRsiStrategy,
    "BollChannelStrategy": BollChannelStrategy,
    "DoubleMaStrategy": DoubleMaStrategy,
    "TurtleSignalStrategy": TurtleSignalStrategy,
    # 添加自定义策略
    # "MovingAverageStrategy": MovingAverageStrategy,
}

def get_strategy_class(class_name):
    """
    根据策略类名获取策略类
    
    Args:
        class_name (str): 策略类名
        
    Returns:
        class: 策略类，如果找不到则返回None
    """
    return STRATEGY_CLASS_MAP.get(class_name)

def get_strategy_class_names():
    """
    获取所有可用的策略类名
    
    Returns:
        list: 策略类名列表
    """
    return list(STRATEGY_CLASS_MAP.keys())

def get_strategy_class_details():
    """
    获取所有策略类的详细信息
    
    Returns:
        list: 策略类详细信息列表，每个元素包含类名、参数等信息
    """
    details = []
    for class_name, strategy_class in STRATEGY_CLASS_MAP.items():
        # 获取策略参数
        parameters = getattr(strategy_class, "parameters", [])
        # 获取策略变量
        variables = getattr(strategy_class, "variables", [])
        
        # 获取参数默认值
        param_values = {}
        for param in parameters:
            param_values[param] = getattr(strategy_class, param, None)
        
        details.append({
            "class_name": class_name,
            "parameters": parameters,
            "variables": variables,
            "default_values": param_values
        })
    
    return details
