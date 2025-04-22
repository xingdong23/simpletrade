#!/usr/bin/env python
import os
# Set environment variables for VnPy database settings BEFORE importing vnpy
os.environ['VNPY_DATABASE_DRIVER'] = 'mysql'
os.environ['VNPY_DATABASE_HOST'] = 'mysql'
os.environ['VNPY_DATABASE_PORT'] = '3306'
os.environ['VNPY_DATABASE_USER'] = 'simpletrade'
os.environ['VNPY_DATABASE_PASSWORD'] = 'password'
os.environ['VNPY_DATABASE_DATABASE'] = 'simpletrade'

# Print a confirmation that variables are set (for debugging)
print("Database environment variables set for VnPy.")
print(f"VNPY_DATABASE_DRIVER={os.environ.get('VNPY_DATABASE_DRIVER')}")
print(f"VNPY_DATABASE_HOST={os.environ.get('VNPY_DATABASE_HOST')}")

import uvicorn
import logging
import sys
from pathlib import Path
import argparse
from fastapi import FastAPI # 导入 FastAPI
import threading # Import threading
from simpletrade.services.data_sync_service import run_initial_data_sync # Import sync function

print("====== [run_api.py] Script Started ======") # DEBUG

# +++ Add Global Logging Configuration +++
logging.basicConfig(
    level=logging.DEBUG,  # Set level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)] # Ensure output goes to console (stdout specifically)
)
print("====== [run_api.py] Global logging configured. ======")
# +++ End Global Logging Configuration +++

# +++ Configure VnPy Database Settings +++
try:
    from simpletrade.config.settings import DB_CONFIG
    from vnpy.trader.setting import SETTINGS
    import vnpy.trader.database as database_module # Keep import for get_database() usage later

    # --- Use the correct key 'database.name' --- 
    SETTINGS["database.name"] = "mysql"  # Set database.name instead of database.driver
    # --- Keep other necessary settings for mysql driver ---
    SETTINGS["database.host"] = DB_CONFIG["DB_HOST"]
    SETTINGS["database.port"] = int(DB_CONFIG["DB_PORT"]) # VnPy 需要 int 类型
    SETTINGS["database.database"] = DB_CONFIG["DB_NAME"]
    SETTINGS["database.user"] = DB_CONFIG["DB_USER"]
    SETTINGS["database.password"] = DB_CONFIG["DB_PASSWORD"]

    # Updated logging to reflect the change
    logging.info(f"VnPy database SETTINGS updated: name=mysql, host={SETTINGS['database.host']}, port={SETTINGS['database.port']}, database={SETTINGS['database.database']}, user={SETTINGS['database.user']}")
    print(f"====== [run_api.py] VnPy database SETTINGS updated: name=mysql, host={SETTINGS['database.host']}, port={SETTINGS['database.port']}, database={SETTINGS['database.database']}, user={SETTINGS['database.user']} ======")

    # --- Ensure the incorrect init() call is removed --- 
    # logging.info("Attempting to explicitly initialize VnPy database manager...")
    # print("====== [run_api.py] Attempting to explicitly initialize VnPy database manager... ======")
    # database_module.init(settings=SETTINGS) # REMOVED/COMMENTED
    # logging.info("Explicit VnPy database manager initialization call finished.")
    # print("====== [run_api.py] Explicit VnPy database manager initialization call finished. ======")

except ImportError as e:
    logging.error(f"Failed to import DB_CONFIG, SETTINGS or database_module: {e}. VnPy database might default to SQLite.")
    print(f"====== [run_api.py] ERROR: Failed to import DB_CONFIG, SETTINGS or database_module: {e}. VnPy database might default to SQLite. ======")
except Exception as e:
    logging.error(f"Error configuring VnPy database settings: {e}", exc_info=True)
    print(f"====== [run_api.py] ERROR configuring VnPy database settings: {e} ======")
# +++ End VnPy Database Configuration +++

# Add project root to sys.path to allow imports like simpletrade.core
project_root = Path(__file__).parent.parent # 因为脚本现在在 docker_scripts 下，所以需要 parent.parent
sys.path.insert(0, str(project_root))
print(f"====== [run_api.py] Project root added to sys.path: {project_root} ======") # DEBUG

# --- Define Lifespan directly in this script (REMOVED) ---

# --- 创建 FastAPI 应用实例 (不再使用 lifespan) ---
print("====== [run_api.py] Creating FastAPI instance with lifespan... ======") # DEBUG
app = FastAPI(title="SimpleTrade API", version="0.1.0") # Removed lifespan
print("====== [run_api.py] FastAPI instance CREATED. ======") # DEBUG check if this prints
print("====== [run_api.py] Top-level FastAPI app instance created ======") # DEBUG

# Configure logging (可以保留或移除) - Keep this commented out as we added global config above
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
# print("====== [run_api.py] Logging configured ======")

# --- 尝试导入和初始化引擎 --- 
try:
    print("====== [run_api.py] Importing vnpy.event.EventEngine... ======") # DEBUG
    from vnpy.event import EventEngine
    print("====== [run_api.py] Importing simpletrade.core.engine.STMainEngine... ======") # DEBUG
    from simpletrade.core.engine import STMainEngine
    # 从 simpletrade.api.server 导入修改后的 configure_server 函数
    print("====== [run_api.py] Importing simpletrade.api.server.configure_server... ======") # DEBUG
    from simpletrade.api.server import configure_server # Keep importing configure_server
    print("====== [run_api.py] Imports successful ======") # DEBUG

    # --- 初始化主引擎 (无 UI 依赖的关键部分) ---
    main_engine = None
    event_engine = None
    print("====== [run_api.py] Initializing EventEngine... ======") # DEBUG
    event_engine = EventEngine()
    print("====== [run_api.py] EventEngine initialized. ======") # DEBUG
    print("====== [run_api.py] Initializing STMainEngine (headless)... ======") # DEBUG
    main_engine = STMainEngine(event_engine)
    print("====== [run_api.py] Headless STMainEngine initialized successfully. ======") # DEBUG

    # --- 配置 FastAPI 应用 (恢复调用) --- 
    print("====== [run_api.py] Configuring FastAPI server instance... ======") # DEBUG
    configure_server(app=app, main_engine=main_engine, event_engine=event_engine) 
    print("====== [run_api.py] FastAPI server instance configured. ======") # DEBUG

except Exception as e:
    # 如果在导入、引擎初始化或服务器配置阶段出错，打印错误并退出
    print(f"====== [run_api.py] FATAL ERROR during setup: {e} ======")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)

# --- 移除命令行参数解析 (保持移除) ---
# parser = argparse.ArgumentParser(description="Run SimpleTrade API Server")
# parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
# parser.add_argument("--reload-dir", type=str, default=None, help="Directory to watch for changes") 
# args = parser.parse_args()
# print(f"====== [run_api.py] Reload mode: {args.reload} ======") # DEBUG - REMOVED
# print(f"====== [run_api.py] Reload directory: {args.reload_dir} ======") # DEBUG - REMOVED

# --- 启动后台数据同步线程 (在配置服务器后, 启动 Uvicorn 前) ---
print("====== [run_api.py] Creating and starting background data sync thread... ======") # DEBUG
try:
    sync_thread = threading.Thread(target=run_initial_data_sync, daemon=True)
    sync_thread.start()
    print("====== [run_api.py] Background data sync thread started. ======") # DEBUG
except Exception as thread_e:
    print(f"====== [run_api.py] FAILED to start background data sync thread: {thread_e} ======")

# --- 启动 Uvicorn (现在应该在 try 块外部) ---
# 只有 setup 成功才会执行到这里
if __name__ == "__main__": # 添加 main guard
    print("====== [run_api.py] Starting Uvicorn server... ======") # DEBUG
    
    # 构建 uvicorn 参数字典 (强制 reload=False)
    uvicorn_params = {
        "host": "0.0.0.0",
        "port": 8003,
        "log_level": "info",
        "reload": True # Restore reload to True for development
    }
    
    # --- 移除 reload_dirs 配置 (不再需要) ---
    # if args.reload_dir:
    #     uvicorn_params["reload_dirs"] = [args.reload_dir]
         
    uvicorn.run(
        "docker_scripts.run_api:app", # <--- 确保导入字符串正确!
        **uvicorn_params # 使用解包传递参数
    )
    # Code below uvicorn.run() will likely not execute until server stops
    print("====== [run_api.py] Uvicorn finished (should not happen if running normally) ======") # DEBUG

# --- (旧的启动逻辑已移除或整合到上面) ---
# if main_engine:
#     try:
#         ...
#     except Exception as e:
#         ...
# else:
#     ... 