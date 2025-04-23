"""
SimpleTrade主程序入口

启动SimpleTrade交易平台。
"""

import sys
import os
import logging
from pathlib import Path
import time
import json # Keep json import if needed elsewhere, but Tiger connect logic moved

# --- Add vendors directory to sys.path ---
# This allows importing modules like vnpy_tiger located in the vendors directory.
project_root = Path(__file__).parent.parent.absolute()
vendors_path = project_root / "vendors"
if vendors_path.exists() and str(vendors_path) not in sys.path:
    sys.path.insert(0, str(vendors_path))
    print(f"[INFO] Added vendors path to sys.path: {vendors_path}")
# --- End sys.path modification ---

# --- Configure VnPy Database Settings EARLY ---
# Import necessary modules for configuration
from vnpy.trader.setting import SETTINGS
from simpletrade.config.settings import DB_CONFIG # Import DB_CONFIG from your settings

# Set VnPy database settings to match project's MySQL config
SETTINGS["database.driver"] = "mysql"  # Explicitly set driver to mysql
SETTINGS["database.host"] = DB_CONFIG["DB_HOST"]
SETTINGS["database.port"] = int(DB_CONFIG["DB_PORT"]) # Ensure port is integer
SETTINGS["database.database"] = DB_CONFIG["DB_NAME"]
SETTINGS["database.user"] = DB_CONFIG["DB_USER"]
SETTINGS["database.password"] = DB_CONFIG["DB_PASSWORD"]

# Optional: Log the settings being applied (use logger after basicConfig)
# We need to ensure logging is configured before using logger here.
# Moving logging config up or delaying this log message.
# print("[INFO] Applied MySQL settings to VnPy global SETTINGS.") # Temporary print
# --- End VnPy Database Configuration ---

# --- 导入核心初始化函数 ---
from simpletrade.core.initialization import initialize_core_components

# --- 不再需要导入 EventEngine, STMainEngine, Apps, Gateways (它们在 initialization 中处理) ---
# from vnpy.event import EventEngine
# from simpletrade.core.engine import STMainEngine
# from simpletrade.apps.st_trader import STTraderApp
# from simpletrade.apps.st_datamanager import STDataManagerApp
# from simpletrade.apps.st_message import STMessageApp
# try: from vnpy_datamanager import DataManagerApp except ImportError: DataManagerApp = None
# try: from vnpy_ib import IbGateway except ImportError: IbGateway = None
# try: from vnpy_tiger import TigerGateway except ImportError: TigerGateway = None


# 配置日志 (Moved up slightly to allow logging VnPy settings)
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("simpletrade.main")

# Log the applied VnPy settings now that logger is configured
logger.info("Applied MySQL database settings to VnPy global SETTINGS:")
logger.info(f"  Driver: {SETTINGS.get('database.driver')}")
logger.info(f"  Host: {SETTINGS.get('database.host')}")
logger.info(f"  Port: {SETTINGS.get('database.port')}")
logger.info(f"  Database: {SETTINGS.get('database.database')}")
logger.info(f"  User: {SETTINGS.get('database.user')}")
# Avoid logging password directly
logger.info(f"  Password: {'********' if SETTINGS.get('database.password') else ''}")

# Remove debug sys.path print
# # Display Python search paths (Remove this one, moved to earlier debug print)
# # logger.debug("Python search paths (in main.py):")
# # for i, path in enumerate(sys.path):
# #     logger.debug(f"  {i}: {path}")

try:
    from vnpy_datamanager import DataManagerApp
    logger.info("vnpy_datamanager imported successfully.")
except ImportError:
    logger.warning("Warning: vnpy_datamanager not found. Please install it first.")
    DataManagerApp = None

try:
    from vnpy_ib import IbGateway
    logger.info("vnpy_ib imported successfully.")
except ImportError:
    logger.warning("Warning: vnpy_ib not found. Please install it first.")
    IbGateway = None

try:
    logger.info("Attempting to import vnpy_tiger...")
    from vnpy_tiger import TigerGateway
    logger.info("vnpy_tiger imported successfully.")
except ImportError as e:
    logger.error(f"Warning: vnpy_tiger not found. Error: {e}")
    logger.warning("Please install it first.")
    TigerGateway = None

# --- 移除全局引擎实例创建 ---
# event_engine = EventEngine()
# main_engine = STMainEngine(event_engine)

# --- 移除全局 App 和 Gateway 注册 ---
# logger.info("Registering gateways and apps globally...")
# if IbGateway: main_engine.add_gateway(IbGateway)
# if TigerGateway: main_engine.add_gateway(TigerGateway)
# # ... (Tiger 连接逻辑已移入 initialization)
# main_engine.add_app(STMessageApp)
# main_engine.add_app(STTraderApp)
# main_engine.add_app(STDataManagerApp)
# if DataManagerApp: main_engine.add_app(DataManagerApp)
# try: main_engine.add_app("cta_strategy") except Exception as e: logger.error(...)
# logger.info("Global registration complete.")


def main():
    """SimpleTrade主程序入口 (主要用于非API模式或测试)"""
    logger.info("Starting SimpleTrade main function (non-API mode)...")

    # --- 调用核心初始化函数来获取引擎实例 ---
    logger.info("Initializing core components via initialize_core_components...")
    try:
        # 注意：现在 main_engine 和 event_engine 是局部变量
        main_engine, event_engine = initialize_core_components()
        logger.info("Core components initialized successfully for main function.")
    except Exception as e:
        logger.error(f"FATAL ERROR during core initialization in main: {e}", exc_info=True)
        sys.exit(1)
    # --- 结束核心初始化调用 ---

    logger.info("SimpleTrade main function setup complete!")

    # 保持主程序运行 (使用局部 main_engine)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down SimpleTrade...")
        if main_engine: # 确保 main_engine 成功初始化
            main_engine.close()
        logger.info("SimpleTrade shutdown completed.")

    # 返回局部变量 (如果需要的话)
    return main_engine, event_engine

if __name__ == "__main__":
    # 调用 main 函数，它现在负责初始化
    main()
