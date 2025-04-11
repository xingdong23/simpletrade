"""
SimpleTrade主程序入口

启动SimpleTrade交易平台。
"""

from vnpy.event import EventEngine
from simpletrade.core.engine import STMainEngine

# 导入SimpleTrade应用
from simpletrade.apps.st_trader import STTraderApp

def main():
    """SimpleTrade主程序入口"""
    print("Starting SimpleTrade...")
    
    # 创建事件引擎
    event_engine = EventEngine()
    print("Event engine created.")

    # 创建SimpleTrade主引擎
    main_engine = STMainEngine(event_engine)
    print("Main engine created.")

    # 加载SimpleTrade应用
    main_engine.add_app(STTraderApp)
    print("ST Trader app loaded.")

    # 加载vnpy内置应用（按需选择）
    try:
        main_engine.add_app("cta_strategy")  # CTA策略
        print("CTA Strategy app loaded.")
    except Exception as e:
        print(f"Failed to load CTA Strategy app: {e}")

    # 启动API服务
    # TODO: 实现API服务启动逻辑
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
