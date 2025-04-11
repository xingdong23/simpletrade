"""
SimpleTrade主程序入口

启动SimpleTrade交易平台。
"""

from vnpy.event import EventEngine
from simpletrade.core.engine import STMainEngine

# 导入SimpleTrade应用
from simpletrade.apps.st_trader import STTraderApp
from simpletrade.apps.st_datamanager import STDataManagerApp
from simpletrade.apps.st_message import STMessageApp

# 导入外部模块
try:
    from vnpy_datamanager import DataManagerApp
    print("vnpy_datamanager imported successfully.")
except ImportError:
    print("Warning: vnpy_datamanager not found. Please install it first.")
    DataManagerApp = None

try:
    from vnpy_ib import IbGateway
    print("vnpy_ib imported successfully.")
except ImportError:
    print("Warning: vnpy_ib not found. Please install it first.")
    IbGateway = None

try:
    from vnpy_tiger import TigerGateway
    print("vnpy_tiger imported successfully.")
except ImportError:
    print("Warning: vnpy_tiger not found. Please install it first.")
    TigerGateway = None

def main():
    """SimpleTrade主程序入口"""
    print("Starting SimpleTrade...")

    # 创建事件引擎
    event_engine = EventEngine()
    print("Event engine created.")

    # 创建SimpleTrade主引擎
    main_engine = STMainEngine(event_engine)
    print("Main engine created.")

    # 注册IB网关
    if IbGateway:
        main_engine.add_gateway(IbGateway)
        print("IB Gateway registered.")

    # 注册老虎证券网关
    if TigerGateway:
        main_engine.add_gateway(TigerGateway)
        print("Tiger Gateway registered.")

    # 加载消息系统应用（先加载，便于其他应用注册消息处理器）
    main_engine.add_app(STMessageApp)
    print("ST Message app loaded.")

    # 加载SimpleTrade应用
    main_engine.add_app(STTraderApp)
    print("ST Trader app loaded.")

    # 加载ST数据管理应用
    main_engine.add_app(STDataManagerApp)
    print("ST Data Manager app loaded.")

    # 加载原始数据管理应用（如果可用）
    if DataManagerApp:
        main_engine.add_app(DataManagerApp)
        print("Original Data Manager app loaded.")

    # 加载vnpy内置应用（按需选择）
    try:
        main_engine.add_app("cta_strategy")  # CTA策略
        print("CTA Strategy app loaded.")
    except Exception as e:
        print(f"Failed to load CTA Strategy app: {e}")

    # 启动API服务
    try:
        from simpletrade.api.server import create_server
        api_server = create_server(main_engine, event_engine)
        print("API server created.")

        # 开启一个新线程启动API服务
        import threading
        api_thread = threading.Thread(target=api_server.start, daemon=True)
        api_thread.start()
        print("API server started on http://0.0.0.0:8000")
    except Exception as e:
        print(f"Failed to start API server: {e}")

    print("SimpleTrade started successfully!")

    # 保持主程序运行
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down SimpleTrade...")
        main_engine.close()
        print("SimpleTrade shutdown completed.")

if __name__ == "__main__":
    main()
