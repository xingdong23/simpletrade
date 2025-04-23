#!/usr/bin/env python
import os
# Set environment variables for VnPy database settings BEFORE importing vnpy
# Use the VNPY_SETTING_{SECTION}__{KEY} format
os.environ['VNPY_SETTING_DATABASE__DRIVER'] = 'mysql' # VnPy typically uses 'driver' internally
os.environ['VNPY_SETTING_DATABASE__HOST'] = 'mysql'
os.environ['VNPY_SETTING_DATABASE__PORT'] = '3306'
os.environ['VNPY_SETTING_DATABASE__USER'] = 'simpletrade' # Use appropriate user
os.environ['VNPY_SETTING_DATABASE__PASSWORD'] = 'password'  # Use appropriate password
os.environ['VNPY_SETTING_DATABASE__DATABASE'] = 'simpletrade'

# Print a confirmation that variables are set (for debugging)
# print("Database environment variables set for VnPy (using VNPY_SETTING__...).")
# print(f"VNPY_SETTING_DATABASE__DRIVER={os.environ.get('VNPY_SETTING_DATABASE__DRIVER')}")
# print(f"VNPY_SETTING_DATABASE__HOST={os.environ.get('VNPY_SETTING_DATABASE__HOST')}")

import uvicorn
import logging
import sys
from pathlib import Path
import argparse
from fastapi import FastAPI # 导入 FastAPI
import threading # Import threading
import asyncio # Import asyncio
from simpletrade.services.data_sync_service import run_initial_data_sync # Import async sync function

# print("====== [run_api.py] Script Started ======") # REMOVE DEBUG

# +++ Add Global Logging Configuration +++
logging.basicConfig(
    level=logging.DEBUG,  # Set level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)] # Ensure output goes to console (stdout specifically)
)
# print("====== [run_api.py] Global logging configured. ======") # REMOVE DEBUG
# +++ End Global Logging Configuration +++

# +++ Configure VnPy Database Settings +++
try:
    # from simpletrade.config.settings import DB_CONFIG # Not needed if using env vars primarily
    from vnpy.trader.setting import SETTINGS
    import vnpy.trader.database as database_module # Keep import for get_database() usage later

    # --- Force Override VnPy Settings IMMEDIATELY after importing SETTINGS --- 
    # print("====== [run_api.py] Manually overriding VnPy SETTINGS for database (early)... ======") # REMOVE DEBUG
    SETTINGS["database.driver"] = "mysql"
    SETTINGS["database.host"] = "mysql"
    SETTINGS["database.port"] = 3306
    SETTINGS["database.user"] = "simpletrade"  # Use appropriate user
    SETTINGS["database.password"] = "password"   # Use appropriate password
    SETTINGS["database.database"] = "simpletrade"
    # print(f"====== [run_api.py] SETTINGS manually overridden (early): driver={SETTINGS.get('database.driver')}, host={SETTINGS.get('database.host')}, port={SETTINGS.get('database.port')}, db={SETTINGS.get('database.database')} ======") # REMOVE DEBUG
    # --- End Force Override --- 

    # --- Attempt to re-initialize database module AFTER override --- 
    # print("====== [run_api.py] Attempting to call database_module.init() to apply overridden settings... ======") # REMOVE DEBUG
    try:
        database_module.init() # Try calling init without args, assuming it reads global SETTINGS
        # print("====== [run_api.py] database_module.init() called successfully. ======") # REMOVE DEBUG
    except Exception as init_exc:
        # print(f"====== [run_api.py] WARNING: database_module.init() failed: {init_exc} ======") # REMOVE DEBUG
        # Keep traceback for actual errors
        # import traceback
        # print(traceback.format_exc())
        pass # Ignore init error for now, as it seems not to exist
    # --- End Re-initialize Attempt --- 

    # Keep standard logging
    logging.info(f"VnPy database SETTINGS check after override and init attempt: driver={SETTINGS.get('database.driver', 'N/A')}, host={SETTINGS.get('database.host', 'N/A')}, port={SETTINGS.get('database.port', 0)}, database={SETTINGS.get('database.database', 'N/A')}, user={SETTINGS.get('database.user', 'N/A')}")
    # print(f"====== [run_api.py] VnPy database SETTINGS check after override and init attempt: ...") # REMOVE DEBUG

except ImportError as e:
    logging.error(f"Failed to import SETTINGS or database_module: {e}.")
    # print(f"====== [run_api.py] ERROR: Failed to import ...") # REMOVE DEBUG
except Exception as e:
    logging.error(f"Error configuring VnPy database settings: {e}", exc_info=True)
    # print(f"====== [run_api.py] ERROR configuring VnPy database settings: {e} ======") # REMOVE DEBUG
# +++ End VnPy Database Configuration +++

# Add project root to sys.path to allow imports like simpletrade.core
project_root = Path(__file__).parent.parent # 因为脚本现在在 docker_scripts 下，所以需要 parent.parent
sys.path.insert(0, str(project_root))
# print(f"====== [run_api.py] Project root added to sys.path: {project_root} ======") # REMOVE DEBUG

# --- 创建 FastAPI 应用实例 (不再使用 lifespan) ---
# print("====== [run_api.py] Creating FastAPI instance... ======") # REMOVE DEBUG
app = FastAPI(title="SimpleTrade API", version="0.1.0") # Removed lifespan
# print("====== [run_api.py] FastAPI instance CREATED. ======") # REMOVE DEBUG check if this prints

# --- 尝试导入和初始化引擎 & 配置服务器 --- 
try:
    # print("====== [run_api.py] Importing vnpy.event.EventEngine... ======") # REMOVE DEBUG
    from vnpy.event import EventEngine
    # print("====== [run_api.py] Importing simpletrade.core.engine.STMainEngine... ======") # REMOVE DEBUG
    from simpletrade.core.engine import STMainEngine
    # 从 simpletrade.api.server 导入修改后的 configure_server 函数
    # print("====== [run_api.py] Importing simpletrade.api.server.configure_server... ======") # REMOVE DEBUG
    from simpletrade.api.server import configure_server # Keep importing configure_server
    # print("====== [run_api.py] Imports successful ======") # REMOVE DEBUG

    # --- 初始化主引擎 (无 UI 依赖的关键部分) ---
    main_engine = None
    event_engine = None
    # print("====== [run_api.py] Initializing EventEngine... ======") # REMOVE DEBUG
    event_engine = EventEngine()
    # print("====== [run_api.py] EventEngine initialized. ======") # REMOVE DEBUG
    # print("====== [run_api.py] Initializing STMainEngine (headless)... ======") # REMOVE DEBUG
    main_engine = STMainEngine(event_engine)
    # print("====== [run_api.py] Headless STMainEngine initialized successfully. ======") # REMOVE DEBUG

    # --- 配置 FastAPI 应用 (恢复调用) --- 
    # print("====== [run_api.py] Configuring FastAPI server instance... ======") # REMOVE DEBUG
    configure_server(app=app, main_engine=main_engine, event_engine=event_engine) 
    # print("====== [run_api.py] FastAPI server instance configured. ======") # REMOVE DEBUG

except Exception as e:
    # 如果在导入、引擎初始化或服务器配置阶段出错，打印错误并退出
    print(f"====== [run_api.py] FATAL ERROR during setup: {e} ======")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)

# --- Define a wrapper function to run the async task in the thread --- 
def start_background_sync():
    """Creates a new event loop and runs the async data sync function."""
    # print("====== [run_api.py] Background thread started. Creating new event loop... ======") # REMOVE DEBUG
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # print("====== [run_api.py] New event loop created and set. Running run_initial_data_sync... ======") # REMOVE DEBUG
    try:
        # Run the coroutine within the new loop
        loop.run_until_complete(run_initial_data_sync())
        # print("====== [run_api.py] run_initial_data_sync completed. ======") # REMOVE DEBUG
    except Exception as e:
        # Keep exception printing for the thread
        print(f"====== [run_api.py] EXCEPTION in background sync thread: {e} ======")
        import traceback
        print(traceback.format_exc())
    finally:
        # print("====== [run_api.py] Closing background thread event loop. ======") # REMOVE DEBUG
        loop.close()
        # print("====== [run_api.py] Background thread event loop closed. ======") # REMOVE DEBUG

# --- 启动后台数据同步线程 (使用新的同步包装函数) --- 
# print("====== [run_api.py] Creating and starting background data sync thread (using wrapper)... ======") # REMOVE DEBUG
try:
    # Change the target to the new synchronous wrapper function
    sync_thread = threading.Thread(target=start_background_sync, daemon=True)
    sync_thread.start()
    # print("====== [run_api.py] Background data sync thread started (using wrapper). ======") # REMOVE DEBUG
except Exception as thread_e:
    # Keep thread start error logging
    print(f"====== [run_api.py] FAILED to start background data sync thread: {thread_e} ======")

# --- 启动 Uvicorn --- 
if __name__ == "__main__": # 添加 main guard
    # print("====== [run_api.py] Starting Uvicorn server... ======") # REMOVE DEBUG
    
    # 构建 uvicorn 参数字典 (强制 reload=False, for stability first)
    uvicorn_params = {
        "host": "0.0.0.0",
        "port": 8003,
        "log_level": "info",
        "reload": False # Set reload to False initially for stability check
    }
         
    uvicorn.run(
        "docker_scripts.run_api:app", # <--- 确保导入字符串正确!
        **uvicorn_params # 使用解包传递参数
    )
    # Code below uvicorn.run() will likely not execute until server stops
    # print("====== [run_api.py] Uvicorn finished (should not happen if running normally) ======") # REMOVE DEBUG 