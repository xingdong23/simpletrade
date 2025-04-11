"""
SimpleTrade主引擎模块

本模块扩展了vnpy的MainEngine，添加了SimpleTrade特有的功能。
"""

from vnpy.trader.engine import MainEngine
from vnpy.event import EventEngine, Event

class STMainEngine(MainEngine):
    """
    SimpleTrade主引擎

    负责管理所有功能模块，包括交易接口、应用模块和SimpleTrade特有的引擎。
    """

    def __init__(self, event_engine=None):
        """
        初始化

        参数:
            event_engine (EventEngine, optional): 事件引擎，默认为None
        """
        if event_engine is None:
            event_engine = EventEngine()
        super().__init__(event_engine)

        # 添加SimpleTrade特有的功能
        self.st_engines = {}

        # 注册事件处理函数
        self.register_event()

    def register_event(self):
        """注册事件处理函数"""
        self.event_engine.register("eLog", self.process_log_event)

    def process_log_event(self, event):
        """
        处理日志事件

        参数:
            event (Event): 日志事件
        """
        log = event.data
        # 可以添加自定义日志处理逻辑，如保存到数据库等

    def add_st_engine(self, engine_name, engine):
        """
        添加SimpleTrade引擎

        参数:
            engine_name (str): 引擎名称
            engine (object): 引擎实例
        """
        if engine_name in self.st_engines:
            return

        self.st_engines[engine_name] = engine

    def get_st_engine(self, engine_name):
        """
        获取SimpleTrade引擎

        参数:
            engine_name (str): 引擎名称

        返回:
            object: 引擎实例，如果不存在则返回None
        """
        return self.st_engines.get(engine_name, None)

    def connect(self, setting, gateway_name):
        """
        连接交易接口

        参数:
            setting (dict): 接口设置
            gateway_name (str): 接口名称

        返回:
            bool: 连接是否成功
        """
        # 添加前置处理，如连接日志记录
        print(f"Connecting to {gateway_name}...")

        # 调用原始连接方法
        result = super().connect(setting, gateway_name)

        # 添加后置处理，如连接状态检查
        if result:
            print(f"Connected to {gateway_name} successfully.")
        else:
            print(f"Failed to connect to {gateway_name}.")

        return result
