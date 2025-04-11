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

# --- 全局引擎实例 ---
# 创建事件引擎
event_engine = EventEngine()
print("Global Event engine created.")

# 创建SimpleTrade主引擎
main_engine = STMainEngine(event_engine)
print("Global Main engine created.")

# --- 全局 App 和 Gateway 注册 ---
print("Registering gateways and apps globally...")
# 注册IB网关
if IbGateway:
    main_engine.add_gateway(IbGateway)
    print("Global: IB Gateway registered.")

# 注册老虎证券网关
if TigerGateway:
    main_engine.add_gateway(TigerGateway)
    print("Global: Tiger Gateway registered.")

# 加载消息系统应用（先加载，便于其他应用注册消息处理器）
main_engine.add_app(STMessageApp)
print("Global: ST Message app loaded.")

# 加载SimpleTrade应用
main_engine.add_app(STTraderApp)
print("Global: ST Trader app loaded.")

# 加载ST数据管理应用
main_engine.add_app(STDataManagerApp)
print("Global: ST Data Manager app loaded.")

# 加载原始数据管理应用（如果可用）
if DataManagerApp:
    main_engine.add_app(DataManagerApp)
    print("Global: Original Data Manager app loaded.")

# 加载vnpy内置应用（按需选择）
try:
    main_engine.add_app("cta_strategy")  # CTA策略
    print("Global: CTA Strategy app loaded.")
except Exception as e:
    print(f"Global: Failed to load CTA Strategy app: {e}")
print("Global registration complete.")
# --- 结束 全局 App 和 Gateway 注册 ---

def main():
    """SimpleTrade主程序入口 (主要用于非API模式或测试)"""
    print("Starting SimpleTrade main function (non-API mode)...")

    # --- 使用全局引擎实例 ---
    # 引擎和 App 已在全局范围初始化和注册
    # --- 结束 使用全局引擎实例 ---

    print("SimpleTrade main function setup complete! (Engine and apps already initialized)")

    # 保持主程序运行 (如果需要)
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
