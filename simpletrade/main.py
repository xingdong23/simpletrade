"""
SimpleTrade主程序入口

启动SimpleTrade交易平台。
"""

import sys
import os
import logging
from pathlib import Path
import time
import threading
import uvicorn
import asyncio

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    print(f"[INFO] Added project root to sys.path: {project_root}")

# 添加 vendors 目录到 Python 路径
vendors_path = project_root / "vendors"
if vendors_path.exists() and str(vendors_path) not in sys.path:
    sys.path.insert(0, str(vendors_path))
    print(f"[INFO] Added vendors path to sys.path: {vendors_path}")

# 导入配置
from simpletrade.config.settings import API_CONFIG, DATA_SYNC_CONFIG

# 导入核心初始化函数
from simpletrade.core.initialization import initialize_core_components

# 配置日志
log_level_str = os.environ.get("SIMPLETRADE_LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("simpletrade.main")
logger.info(f"Logging configured with level: {log_level_str}")


def run_api_server(host: str, port: int, app_instance):
    """运行 API 服务器

    Args:
        host: 主机地址
        port: 端口号
        app_instance: FastAPI应用实例
    """
    if not app_instance:
        logger.error("Cannot start API server: FastAPI app instance not found.")
        return

    logger.info(f"Starting API server on http://{host}:{port}")
    try:
        uvicorn.run(app_instance, host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"API server failed: {e}", exc_info=True)
    logger.info("API server stopped.")


def start_data_sync(db_instance, periodic=False):
    """启动数据同步服务

    Args:
        db_instance: 数据库实例
        periodic: 是否周期性运行
    """
    try:
        from simpletrade.services.data_sync_service import run_initial_data_sync, run_periodic_data_sync
    except ImportError as e:
        logger.error(f"Failed to import data sync components: {e}")
        return

    if not db_instance:
        logger.error("Cannot start data sync: database instance not available.")
        return

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if periodic:
            logger.info("Starting periodic data synchronization...")
            loop.run_until_complete(run_periodic_data_sync(db_instance=db_instance))
        else:
            logger.info("Running one-time data synchronization...")
            loop.run_until_complete(run_initial_data_sync(db_instance=db_instance))
            logger.info("Data synchronization completed.")
    except Exception as e:
        logger.error(f"Error in data sync thread: {e}", exc_info=True)
    finally:
        logger.info("Closing data sync event loop.")
        loop.close()


def start_api_server(main_engine, event_engine):
    """启动API服务器

    Args:
        main_engine: 主引擎实例
        event_engine: 事件引擎实例
    """
    if not API_CONFIG.get("ENABLED", True):
        logger.info("API server disabled in configuration. Skipping start.")
        return

    try:
        # 导入API相关模块
        from simpletrade.core.server import app as fastapi_app, configure_server

        # 配置API服务器
        if main_engine and event_engine and fastapi_app and configure_server:
            configure_server(main_engine=main_engine, event_engine=event_engine)
            logger.info("API server configured successfully.")

            # 启动API服务器线程
            api_host = API_CONFIG.get("HOST", "0.0.0.0")
            api_port = int(API_CONFIG.get("PORT", 8003))

            api_thread = threading.Thread(
                target=run_api_server,
                args=(api_host, api_port, fastapi_app),
                daemon=True
            )
            api_thread.start()
            logger.info(f"API server thread started at http://{api_host}:{api_port}")
            return api_thread
        else:
            logger.warning("Skipping API server start due to missing components.")
            return None
    except ImportError as e:
        logger.error(f"Failed to import API components: {e}")
        return None
    except Exception as e:
        logger.error(f"Error starting API server: {e}", exc_info=True)
        return None


def start_data_sync_service(db_instance):
    """启动数据同步服务

    Args:
        db_instance: 数据库实例
    """
    if not DATA_SYNC_CONFIG.get("ENABLED", True):
        logger.info("Data sync service disabled in configuration. Skipping start.")
        return None

    if not db_instance:
        logger.error("Cannot start data sync service: database instance not available.")
        return None

    try:
        # 检查是否启用同步周期
        run_periodic = DATA_SYNC_CONFIG.get("PERIODIC_SYNC", False)

        # 是否在启动时同步
        sync_on_startup = DATA_SYNC_CONFIG.get("SYNC_ON_STARTUP", True)

        if sync_on_startup or run_periodic:
            # 创建并启动数据同步线程
            sync_thread = threading.Thread(
                target=start_data_sync,
                args=(db_instance, run_periodic),  # 传递周期性运行标志
                daemon=True
            )
            sync_thread.start()

            if run_periodic:
                logger.info("Periodic data synchronization service thread started.")
            else:
                logger.info("One-time data synchronization service thread started.")

            return sync_thread
        else:
            logger.info("Data synchronization on startup disabled. Skipping initial sync.")
            return None

    except Exception as e:
        logger.error(f"Error starting data sync service: {e}", exc_info=True)
        return None


def keep_running():
    """保持主程序运行，直到收到终止信号"""
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down SimpleTrade...")


def main():
    """SimpleTrade主程序入口点"""
    logger.info("Starting SimpleTrade...")

    try:
        # 1. 初始化核心组件
        main_engine, event_engine, db_instance = initialize_core_components()
        logger.info("Core components initialized successfully.")

        # 2. 启动API服务器（如果配置启用）
        start_api_server(main_engine, event_engine)

        # 3. 启动数据同步服务（如果配置启用）
        start_data_sync_service(db_instance)

        # 4. 主循环保持程序运行
        logger.info("SimpleTrade is running. Press Ctrl+C to shut down.")
        keep_running()

    except Exception as e:
        logger.critical(f"FATAL ERROR during SimpleTrade startup: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
