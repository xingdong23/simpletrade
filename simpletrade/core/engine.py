"""
SimpleTrade主引擎模块

本模块扩展了vnpy的MainEngine，添加了SimpleTrade特有的功能。
"""

from vnpy.trader.engine import MainEngine, BaseEngine
from vnpy.event import EventEngine, Event
from vnpy.trader.app import BaseApp
from vnpy_ctastrategy import CtaStrategyApp
import inspect  # 需要导入 inspect 模块

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

        # 添加CTA策略应用
        self.add_app(CtaStrategyApp)

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

    def add_app(self, app_class: type[BaseApp]) -> BaseEngine:
        """
        覆盖 VnPy 的 add_app 方法，并智能处理引擎初始化参数。
        Add app, handling different engine __init__ signatures.
        """
        app: BaseApp = app_class()
        self.apps[app.app_name] = app

        if hasattr(app, "init_engine"):
            app.init_engine(self, self.event_engine)

        if not hasattr(app, "engine_class") or not app.engine_class:
            self.write_log(f"App {app.app_name} does not have an associated engine_class.", source="STMainEngine")
            return None

        engine_class = app.engine_class
        engine_name = app.app_name

        # === 智能参数处理 ===
        try:
            # Inspect the engine's __init__ method signature
            sig = inspect.signature(engine_class.__init__)
            params = sig.parameters
            num_params = len(params) # 获取参数总数 (包括 self)

            # 根据 __init__ 的参数数量调用构造函数
            if num_params == 4:  # 期望 __init__(self, main_engine, event_engine, engine_name)
                engine: BaseEngine = engine_class(self, self.event_engine, engine_name)
            elif num_params == 3:  # 期望 __init__(self, main_engine, event_engine)，例如 CtaEngine
                engine: BaseEngine = engine_class(self, self.event_engine)
                # 由于 BaseEngine.__init__ 需要 engine_name，而这里没有传递
                # 尝试在实例化后手动设置 engine_name (如果引擎实例允许)
                if hasattr(engine, 'engine_name') and not engine.engine_name:
                     try:
                         engine.engine_name = engine_name
                     except AttributeError:
                         self.write_log(f"Warning: Could not set engine_name on {engine_class.__name__} instance after initialization.", source="STMainEngine")

            else: # 处理非预期的参数数量
                raise TypeError(f"Engine class {engine_class.__name__}.__init__ has an unexpected signature with {num_params} parameters.")

        except Exception as e:
            self.write_log(f"Failed to inspect or initialize engine {engine_name} for app {app.app_name}. Error: {e}", source="STMainEngine")
            raise e

        # 确保 engine_name 被设置 (如果可能)
        if not hasattr(engine, 'engine_name') or not engine.engine_name:
            self.write_log(f"Warning: Engine {engine.__class__.__name__} instance created but 'engine_name' attribute might be missing or incorrect.", source="STMainEngine")
            try:
                if not getattr(engine, 'engine_name', None):
                    engine.engine_name = engine_name
            except AttributeError:
                pass

        self.engines[engine_name] = engine # 使用 app_name 作为 key 存储

        if hasattr(app, "init_app"):
            app.init_app()

        return engine

    def get_cta_engine(self):
        """
        获取CTA策略引擎

        返回:
            CtaEngine: CTA策略引擎实例
        """
        return self.get_engine("CtaStrategy")
