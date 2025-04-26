#!/usr/bin/env python
import os
# Set environment variables for VnPy database settings BEFORE importing vnpy
# Use the VNPY_SETTING_{SECTION}__{KEY} format
# (数据库环境变量设置保持不变)
os.environ['VNPY_SETTING_DATABASE__DRIVER'] = 'mysql'
os.environ['VNPY_SETTING_DATABASE__HOST'] = 'mysql'
os.environ['VNPY_SETTING_DATABASE__PORT'] = '3306'
os.environ['VNPY_SETTING_DATABASE__USER'] = 'simpletrade'
os.environ['VNPY_SETTING_DATABASE__PASSWORD'] = 'password'
os.environ['VNPY_SETTING_DATABASE__DATABASE'] = 'simpletrade'

import uvicorn
import logging
import sys # sys 仍然需要用于日志配置
# from pathlib import Path # 不再需要 Path
import argparse
import threading
import asyncio

# 导入将在 simpletrade 包中定义的应用和配置函数
from simpletrade.services.data_sync_service import run_initial_data_sync
from simpletrade.core.server import configure_server # 导入服务器配置函数
# +++ 导入新的核心初始化函数 +++
from simpletrade.core.initialization import initialize_core_components

# (全局日志配置保持不变)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# (VnPy 数据库设置保持不变，包括手动覆盖 SETTINGS)
try:
    from vnpy.trader.setting import SETTINGS
    import vnpy.trader.database as database_module
    SETTINGS["database.driver"] = "mysql"
    SETTINGS["database.host"] = "mysql"
    SETTINGS["database.port"] = 3306
    SETTINGS["database.user"] = "simpletrade"
    SETTINGS["database.password"] = "password"
    SETTINGS["database.database"] = "simpletrade"
    # 尝试 init (保持不变)
    try:
        database_module.init()
    except Exception as init_exc:
        pass # Ignore init error
    logging.info(f"VnPy database SETTINGS check in run_api: driver={SETTINGS.get('database.driver', 'N/A')}, host={SETTINGS.get('database.host', 'N/A')}") # ...
except Exception as e:
    logging.error(f"Error configuring VnPy database settings in run_api: {e}", exc_info=True)


# --- 不再需要修改 sys.path ---
# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root))

# --- FastAPI 应用实例现在将在 simpletrade.api.server 中创建 ---
# app = FastAPI(title="SimpleTrade API", version="0.1.0") # 移动到 server.py

# --- 初始化引擎 & 配置服务器 (使用新的初始化函数) ---
main_engine = None
event_engine = None
try:
    # +++ 调用核心初始化函数 +++
    logging.info("Initializing core components via initialize_core_components...")
    main_engine, event_engine = initialize_core_components()
    logging.info("Core components initialized successfully.")

    # --- 配置 FastAPI 应用 (传入初始化好的引擎) ---
    logging.info("Configuring FastAPI server via configure_server...")
    configure_server(main_engine=main_engine, event_engine=event_engine)
    logging.info("FastAPI server instance configured.")

except Exception as e:
    logging.error(f"FATAL ERROR during setup in run_api: {e}", exc_info=True)
    sys.exit(1)

# --- 后台数据同步线程 (保持不变) ---
def start_background_sync():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        logging.info("Background thread: Running run_initial_data_sync...")
        loop.run_until_complete(run_initial_data_sync())
        logging.info("Background thread: run_initial_data_sync completed.")
    except Exception as e:
        logging.error(f"EXCEPTION in background sync thread: {e}", exc_info=True)
    finally:
        logging.info("Background thread: Closing event loop.")
        loop.close()

logging.info("Creating and starting background data sync thread...")
try:
    sync_thread = threading.Thread(target=start_background_sync, daemon=True)
    sync_thread.start()
    logging.info("Background data sync thread started.")
except Exception as thread_e:
    logging.error(f"FAILED to start background data sync thread: {thread_e}", exc_info=True)

# --- 启动 Uvicorn (保持不变) ---
if __name__ == "__main__":
    logging.info("Starting Uvicorn server...")
    # 从配置或环境变量获取 host 和 port 可能更好，但暂时保持硬编码
    host = "0.0.0.0"
    port = 8003
    log_level = "info"
    reload = False # 通常在生产或 Docker 中禁用 reload

    logging.info(f"Running Uvicorn on {host}:{port}")

    # 更新指向core.server中的app实例
    uvicorn.run(
        "simpletrade.core.server:app", # 指向 core/server.py 中的 app
        host=host,
        port=port,
        log_level=log_level,
        reload=reload
    ) 