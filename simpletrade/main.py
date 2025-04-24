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

# --- Import Shared Configs (Still needed for API thread) ---
# Although SETTINGS are configured elsewhere, API thread needs API_CONFIG directly
from simpletrade.config.settings import API_CONFIG

# --- 导入核心初始化函数 ---
from simpletrade.core.initialization import initialize_core_components

# --- Optional App/Gateway Imports ---
# We still need these imports here to check for module existence
# and potentially pass them later if needed, or just log warnings.
logger = logging.getLogger(__name__) # Define logger early for imports
try:
    from vnpy_datamanager import DataManagerApp
    logger.info("Optional app 'vnpy_datamanager' imported successfully.")
except ImportError:
    logger.warning("Optional app 'vnpy_datamanager' not found. Install if needed.")
    DataManagerApp = None
try:
    from vnpy_ib import IbGateway
    logger.info("Optional gateway 'vnpy_ib' imported successfully.")
except ImportError:
    logger.warning("Optional gateway 'vnpy_ib' not found. Install if needed.")
    IbGateway = None
try:
    from vnpy_tiger import TigerGateway
    logger.info("Optional gateway 'vnpy_tiger' imported successfully.")
except ImportError as e:
    # Reduced severity, just a warning if not found
    logger.warning(f"Optional gateway 'vnpy_tiger' not found. Error: {e}")
    TigerGateway = None
# --- End Optional Imports ---


# --- Configure Logging (Keep this early) ---
# Read log level from config BEFORE setting up handler
log_level_str = os.environ.get("SIMPLETRADE_LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

logging.basicConfig(
    level=log_level, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()] # Output to console
)
# Re-get logger after basicConfig
logger = logging.getLogger("simpletrade.main")
logger.info(f"Logging configured with level: {log_level_str}")
# --- End Logging Configuration ---

# --- Remove VnPy Settings Logging Block --- 
# This logging is now redundant or better placed within initialization
# logger.info("Applied MySQL database settings...") 
# ...
# --- End Removed Block ---

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
        uvicorn.run(app_instance, host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"Uvicorn server failed: {e}", exc_info=True)
    logger.info("Uvicorn API server stopped.")

def start_background_sync(db_instance):
    if not run_initial_data_sync:
        logger.warning("run_initial_data_sync not available, skipping background sync.")
        return
        
    if not db_instance:
        logger.error("No database instance provided to background sync thread. Skipping sync.")
        return
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        logger.info("Background thread: Running run_initial_data_sync...")
        loop.run_until_complete(run_initial_data_sync(db_instance=db_instance))
        logger.info("Background thread: run_initial_data_sync completed.")
    except Exception as e:
        logger.error(f"EXCEPTION in background sync thread: {e}", exc_info=True)
    finally:
        logger.info("Background thread: Closing event loop.")
        loop.close()

def main():
    """SimpleTrade主程序入口 (现在同时启动核心引擎, API服务器和后台同步)"""
    logger.info("Starting SimpleTrade main function (Core + API + Sync mode)...")

    # --- 调用核心初始化函数来获取引擎实例 (Now handles SETTINGS config) ---
    logger.info("Initializing core components via initialize_core_components...")
    main_engine = None # Initialize to None
    event_engine = None
    db_instance = None # Initialize to None
    try:
        # +++ 接收 db_instance +++
        main_engine, event_engine, db_instance = initialize_core_components()
        logger.info("Core components initialized successfully for main function.")

        # +++ 配置 API 服务器，注入引擎 +++
        logger.info("Configuring API server with core engines...")
        if fastapi_app and configure_server:
            try:
                # 确保 main_engine 和 event_engine 有效
                if main_engine and event_engine:
                     configure_server(main_engine=main_engine, event_engine=event_engine)
                     logger.info("API server configured successfully.")
                else:
                     logger.error("Cannot configure API server: Core engines not properly initialized.")
            except Exception as config_e:
                logger.error(f"Error configuring API server: {config_e}", exc_info=True)
        elif not fastapi_app:
            logger.warning("FastAPI app not imported, skipping API configuration.")
        else: # fastapi_app 存在但 configure_server 不存在
            logger.warning("configure_server function not found, skipping API configuration.")
        # +++ 结束 API 服务器配置 +++

    except Exception as e:
        logger.critical(f"FATAL ERROR during core initialization or API config in main: {e}", exc_info=True)
        sys.exit(1)
    # --- 结束核心初始化调用 ---

    # --- 启动 API 服务器线程 ---
    if fastapi_app and configure_server and main_engine and event_engine: # Add checks for engines
        api_host = API_CONFIG.get("HOST", "0.0.0.0") 
        api_port = int(API_CONFIG.get("PORT", 8003))
        
        api_thread = threading.Thread(
            target=run_api_server, 
            args=(api_host, api_port, fastapi_app), 
            daemon=True
        )
        api_thread.start()
        logger.info(f"API server thread started. Access API docs at http://{api_host}:{api_port}/docs")
    else:
        logger.warning("Skipping API server start due to import/configuration issues or failed core initialization.")
    # --- 结束 API 服务器启动 ---

    # --- 启动后台数据同步线程 ---
    # +++ 检查 db_instance 是否有效 +++
    if run_initial_data_sync and db_instance:
        logger.info("Creating and starting background data sync thread...")
        try:
            # +++ 将 db_instance 传递给线程目标函数 +++
            sync_thread = threading.Thread(
                target=start_background_sync, 
                args=(db_instance,), # Pass db_instance as argument
                daemon=True
            )
            sync_thread.start()
            logger.info("Background data sync thread started.")
        except Exception as thread_e:
            logger.error(f"FAILED to start background data sync thread: {thread_e}", exc_info=True)
    elif not run_initial_data_sync:
        logger.info("Skipping background data sync because function was not imported.")
    else: # run_initial_data_sync exists, but db_instance is None
        logger.error("Skipping background data sync because database instance was not obtained during initialization.")
    # --- 结束后台数据同步启动 ---

    logger.info("SimpleTrade Core Engine is running. API server and Sync task are running in separate threads (if started).")
    logger.info("Press Ctrl+C to shut down.")

    # 保持主程序运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down SimpleTrade...")
        if main_engine:
            main_engine.close()
        logger.info("SimpleTrade shutdown completed.")

if __name__ == "__main__":
    main()
