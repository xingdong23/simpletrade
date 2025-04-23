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
import threading  # 导入 threading
import uvicorn    # 导入 uvicorn
import asyncio  # 导入 asyncio

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
from simpletrade.config.settings import DB_CONFIG, API_CONFIG # Import DB_CONFIG and API_CONFIG

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

# --- 导入 FastAPI 应用实例和配置函数 ---
# 假设 FastAPI 实例在 simpletrade/api/server.py 中名为 app
# 假设配置函数名为 configure_server
try:
    from simpletrade.api.server import app as fastapi_app, configure_server # 添加 configure_server
    logger.info("FastAPI app and configure_server imported successfully.")
except ImportError as e:
    logger.error(f"Failed to import FastAPI app/configure_server from simpletrade.api.server: {e}")
    fastapi_app = None
    configure_server = None # 确保 configure_server 也为 None

# --- 导入后台数据同步函数 ---
try:
    from simpletrade.services.data_sync_service import run_initial_data_sync
    logger.info("Background data sync function imported successfully.")
except ImportError as e:
    logger.warning(f"Could not import run_initial_data_sync: {e}. Background sync disabled.")
    run_initial_data_sync = None

def run_api_server(host: str, port: int, app_instance):
    """在一个单独的线程中运行 Uvicorn 服务器"""
    if not app_instance:
        logger.error("Cannot start API server: FastAPI app instance not found.")
        return
    logger.info(f"Starting Uvicorn API server on http://{host}:{port}")
    try:
        # 注意：uvicorn.run() 在这里是阻塞的，直到服务器停止
        uvicorn.run(app_instance, host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"Uvicorn server failed: {e}", exc_info=True)
    logger.info("Uvicorn API server stopped.")

# --- 后台数据同步线程函数 (借鉴自 run_api.py) ---
def start_background_sync():
    if not run_initial_data_sync:
        logger.warning("run_initial_data_sync not available, skipping background sync.")
        return
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        logger.info("Background thread: Running run_initial_data_sync...")
        loop.run_until_complete(run_initial_data_sync())
        logger.info("Background thread: run_initial_data_sync completed.")
    except Exception as e:
        logger.error(f"EXCEPTION in background sync thread: {e}", exc_info=True)
    finally:
        logger.info("Background thread: Closing event loop.")
        loop.close()

def main():
    """SimpleTrade主程序入口 (现在同时启动核心引擎, API服务器和后台同步)"""
    logger.info("Starting SimpleTrade main function (Core + API + Sync mode)...") # 更新日志

    # --- 调用核心初始化函数来获取引擎实例 ---
    logger.info("Initializing core components via initialize_core_components...")
    try:
        # 注意：现在 main_engine 和 event_engine 是局部变量
        main_engine, event_engine = initialize_core_components()
        logger.info("Core components initialized successfully for main function.")

        # +++ 配置 API 服务器，注入引擎 +++
        logger.info("Configuring API server with core engines...")
        if fastapi_app and configure_server:
            try:
                configure_server(main_engine=main_engine, event_engine=event_engine)
                logger.info("API server configured successfully.")
            except Exception as config_e:
                logger.error(f"Error configuring API server: {config_e}", exc_info=True)
                # 可以决定是否因为配置失败而退出，或者只是跳过 API 启动
                # 这里选择记录错误并可能导致后续 API 线程不启动（因为依赖于配置）
        elif not fastapi_app:
            logger.warning("FastAPI app not imported, skipping API configuration.")
        else: # fastapi_app 存在但 configure_server 不存在
            logger.warning("configure_server function not found, skipping API configuration.")
        # +++ 结束 API 服务器配置 +++

    except Exception as e:
        logger.error(f"FATAL ERROR during core initialization or API config in main: {e}", exc_info=True)
        sys.exit(1)
    # --- 结束核心初始化调用 ---

    # --- 启动 API 服务器线程 ---
    # 检查 fastapi_app 是否成功导入并且配置函数存在（即使配置出错也尝试启动）
    if fastapi_app and configure_server: 
        api_host = API_CONFIG.get("HOST", "0.0.0.0")
        api_port = int(API_CONFIG.get("PORT", 8002))
        
        api_thread = threading.Thread(
            target=run_api_server, 
            args=(api_host, api_port, fastapi_app), 
            daemon=True # 设置为守护线程
        )
        api_thread.start()
        logger.info(f"API server thread started. Access API docs at http://{api_host}:{api_port}/docs")
    else:
        logger.warning("Skipping API server start because FastAPI app or configure_server function could not be imported.")
    # --- 结束 API 服务器启动 ---

    # --- 启动后台数据同步线程 ---
    if run_initial_data_sync:
        logger.info("Creating and starting background data sync thread...")
        try:
            sync_thread = threading.Thread(target=start_background_sync, daemon=True)
            sync_thread.start()
            logger.info("Background data sync thread started.")
        except Exception as thread_e:
            logger.error(f"FAILED to start background data sync thread: {thread_e}", exc_info=True)
    else:
        logger.info("Skipping background data sync because function was not imported.")
    # --- 结束后台数据同步启动 ---

    logger.info("SimpleTrade Core Engine is running. API server and Sync task are running in separate threads (if started).") # 更新日志
    logger.info("Press Ctrl+C to shut down.")

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
    # return main_engine, event_engine # 通常主脚本不需要返回

if __name__ == "__main__":
    # 调用 main 函数，它现在负责初始化和启动 API
    main()
