"""
SimpleTrade应用基础模块

本模块定义了SimpleTrade应用的基础类。
"""

import importlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from types import ModuleType

from vnpy.trader.app import BaseApp
from vnpy.trader.engine import BaseEngine

# 导入vnpy相关模块
# from vnpy.vnpy.trader.app import BaseApp
# from vnpy.vnpy.trader.engine import BaseEngine

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

    def __init__(self):
        """
        初始化 - 移除 main_engine 和 event_engine 参数
        """
        super().__init__() # 调用父类初始化
        self.main_engine = None
        self.event_engine = None
        self.engine = None

    def init_engine(self, main_engine, event_engine):
        """
        初始化引擎 - 由 MainEngine.add_app 调用
        """
        self.main_engine = main_engine
        self.event_engine = event_engine

        # 创建应用引擎实例 (如果 engine_class 已定义)
        if self.engine_class:
            self.engine = self.engine_class(main_engine, event_engine, self.app_name)

class STBaseEngine(BaseEngine):
    """
    SimpleTrade基础引擎类

    所有SimpleTrade引擎都应继承此类。
    """

    def __init__(self, main_engine, event_engine, app_name: Optional[str] = None):
        """
        初始化 - 使 app_name 可选以兼容 VnPy add_engine 的调用

        参数:
            main_engine (MainEngine): 主引擎
            event_engine (EventEngine): 事件引擎
            app_name (str, optional): 应用名称. Defaults to None.
        """
        resolved_app_name = app_name
        if resolved_app_name is None:
            # 如果 app_name 未被 add_engine 提供, 使用引擎类名作为后备
            # 这可能不是 App 类中定义的 app_name, 但 BaseEngine 可能需要一个字符串名称
            resolved_app_name = self.__class__.__name__

        # 使用解析出的名称调用父类 __init__
        # 注意: 这依赖于 vnpy.trader.engine.BaseEngine 的 __init__ 接受 engine_name
        super().__init__(main_engine, event_engine, resolved_app_name)

        # 将解析出的名称存储为 engine_name 供内部使用
        self.engine_name = resolved_app_name

        # 添加到主引擎的ST引擎列表
        if hasattr(main_engine, "add_st_engine"):
            # 使用存储的 engine_name
            main_engine.add_st_engine(self.engine_name, self)
