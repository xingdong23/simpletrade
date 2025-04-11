"""
SimpleTrade主引擎模块

本模块扩展了vnpy的MainEngine，添加了SimpleTrade特有的功能。
"""

from vnpy.trader.engine import MainEngine
from vnpy.event import EventEngine, Event
from vnpy.trader.app import BaseApp

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

    def add_app(self, app_class: type[BaseApp] | str):
        """添加应用模块"""
        # --- 处理字符串形式的 vnpy 内置 App ---
        if isinstance(app_class, str):
            app_name_str = app_class
            print(f"Adding built-in app (str) {app_name_str} using superclass method...")
            try:
                super().add_app(app_name_str)
            except Exception as e:
                print(f"Failed to add built-in app {app_name_str}: {e}")
            return
        # --- 结束处理字符串 ---
            
        # --- 处理类形式的自定义 App ---
        # 检查是否是我们的自定义 App 类 (假设它们都有特定的基类或标识)
        app_name = app_class.__name__
        if app_name in self.apps:
            print(f"{app_name} app already added.")
            return
        
        try:
            # 尝试使用 main_engine 和 event_engine 初始化
            # 假设我们的 App 都需要这两个参数
            if hasattr(app_class, "__init__") and 'main_engine' in app_class.__init__.__code__.co_varnames and 'event_engine' in app_class.__init__.__code__.co_varnames:
                 print(f"Initializing custom app {app_name} with engines...")
                 app: BaseApp = app_class(main_engine=self, event_engine=self.event_engine)
                 self.apps[app_name] = app
                 self.engines[app_name] = app # 兼容 get_engine
            # else:
                 # 如果不是我们的自定义 App，调用父类的方法处理（适用于 vnpy 内置 App）
                 # print(f"Adding app {app_name} using superclass method...")
                 # super().add_app(app_class) # 这部分逻辑已移到字符串处理部分
                 
        except Exception as e:
            print(f"Failed to add app {app_name}: {e}")
