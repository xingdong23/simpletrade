"""
SimpleTrade应用基类模块

本模块定义了SimpleTrade应用的基类，用于扩展vnpy的应用架构。
"""

from pathlib import Path
from vnpy.trader.app import BaseApp
from vnpy.trader.engine import BaseEngine

class STBaseApp(BaseApp):
    """
    SimpleTrade基础应用类
    
    所有SimpleTrade应用都应继承此类。
    """

    app_type = "st"  # SimpleTrade应用类型
    app_name = ""    # 应用名称
    app_module = ""  # 应用模块
    app_path = ""    # 应用路径
    display_name = ""  # 显示名称
    engine_class = None  # 引擎类
    widget_class = None  # 界面类
    
    def __init__(self, main_engine, event_engine):
        """
        初始化
        
        参数:
            main_engine (MainEngine): 主引擎
            event_engine (EventEngine): 事件引擎
        """
        super().__init__(main_engine, event_engine)

class STBaseEngine(BaseEngine):
    """
    SimpleTrade基础引擎类
    
    所有SimpleTrade引擎都应继承此类。
    """
    
    def __init__(self, main_engine, event_engine, app_name):
        """
        初始化
        
        参数:
            main_engine (MainEngine): 主引擎
            event_engine (EventEngine): 事件引擎
            app_name (str): 应用名称
        """
        super().__init__(main_engine, event_engine, app_name)
        
        # 添加到主引擎的ST引擎列表
        if hasattr(main_engine, "add_st_engine"):
            main_engine.add_st_engine(app_name, self)
