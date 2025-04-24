"""
数据同步服务

负责根据配置，从不同的数据源同步历史数据到VnPy数据库。
"""

import logging
from datetime import datetime, timedelta, date, timezone
from typing import List, Dict, Any, Optional
import os
import asyncio

# 导入配置和模型
from simpletrade.config.settings import DATA_SYNC_TARGETS, PROJECT_ROOT, QLIB_DATA_PATH

# 导入VnPy相关
from vnpy.trader.constant import Exchange, Interval
# +++ 恢复使用 VnPy 标准数据库接口 +++
from vnpy.trader.database import get_database, BaseDatabase # 导入 get_database 和 BaseDatabase
from vnpy.trader.object import BarData

# --- 导入 Qlib 数据导入器 --- 
from simpletrade.apps.st_datamanager.importers.qlib_importer import QlibDataImporter

# 导入辅助函数
from .backtest_service import _get_vnpy_exchange, _get_vnpy_interval

# --- 移除直接导入 vnpy_mysql 的逻辑 ---
# try:
#     from vnpy_mysql import MysqlDatabase
#     ...
# except ...
#     MysqlDatabase = None

logger = logging.getLogger("simpletrade.services.data_sync_service")

# --- 移除硬编码的 QLIB_DATA_DIR --- 
# QLIB_DATA_DIR = ... 

class DataSyncService:
    """数据同步服务类"""

    def __init__(self, db_instance: BaseDatabase):
        """Initializes the DataSyncService with a provided database instance."""
        if not isinstance(db_instance, BaseDatabase):
             logger.error(f"Invalid database instance provided to DataSyncService: {type(db_instance)}")
             # Decide how to handle this - raise error? set self.db to None?
             # For now, let's raise an error to make the problem obvious
             raise TypeError("DataSyncService requires a valid vnpy.trader.database.BaseDatabase instance.")
             
        self.db: BaseDatabase = db_instance # 直接使用传入的实例
        logger.info(f"DataSyncService initialized with provided database instance: {type(self.db)}")
        # --- 移除内部 get_database 调用 --- 
        # try:
        #     logger.debug("Attempting to get database instance via get_database()...")
        #     self.db = get_database()
        #     logger.info(f"DataSyncService initialized with database instance: {type(self.db)}")
        # except Exception as e:
        #     logger.error(f"Failed to get database instance using get_database(): {e}", exc_info=True)
        #     self.db = None # Ensure db is None on error

        self.targets = DATA_SYNC_TARGETS
        self.qlib_importer = QlibDataImporter()

    # --- 保持 sync_all_targets 和 sync_target 使用 get_database 时的版本 --- 
    async def sync_all_targets(self):
        """Synchronizes data for all targets specified in the configuration."""
        if not self.targets:
            logger.warning("No data synchronization targets configured.")
            return

        if not self.db:
            logger.error("Database instance not available in sync_all_targets.")
            return

        tasks = [self.sync_target(target) for target in self.targets]
        results = await asyncio.gather(*tasks, return_exceptions=True) # 捕获每个任务的异常

        # 记录每个任务的结果
        for i, result in enumerate(results):
            target = self.targets[i]
            if isinstance(result, Exception):
                logger.error(f"Error syncing target {target}: {result}", exc_info=result)

        logger.info("Finished sync_all_targets run.")


    async def sync_target(self, target: dict):
        """Synchronizes data for a single target."""
        source = target.get("source")
        symbol = target.get("symbol")
        exchange_str = target.get("exchange")
        interval_str = target.get("interval")
        start_date_str = target.get("start_date", "2020-01-01")
        end_date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        market = target.get("market")

        logger.info(f"Processing sync target: {target}")
        if source.lower() == "qlib" and not market:
             logger.error(f"Skipping Qlib target due to missing 'market' field: {target}")
             return
        if not all([source, symbol, exchange_str, interval_str]): 
             logger.warning(f"Skipping invalid target (missing basic fields): {target}"); 
             return

        try:
            exchange = Exchange(exchange_str)
            interval = Interval(interval_str)
        except ValueError as e: logger.error(f"Invalid exchange or interval in target {target}: {e}"); return

        success = False # Initialize success flag
        message = ""      # Initialize message string
        bars = []       # Initialize bars list
        try:
            logger.info(f"Starting data import for {symbol} from {source}...")
            if source.lower() == "qlib":
                # --- 使用配置的 QLIB_DATA_PATH --- 
                logger.info(f"Using QlibDataImporter for {symbol} (market: {market})...")
                
                # 检查 QLIB_DATA_PATH 是否已配置且存在
                if not QLIB_DATA_PATH or not os.path.exists(QLIB_DATA_PATH):
                    message = f"QLIB_DATA_PATH ('{QLIB_DATA_PATH}') not configured or does not exist. Skipping Qlib import for {symbol}. Set SIMPLETRADE_QLIB_DATA_PATH environment variable."
                    logger.error(message)
                    success = False
                else:
                    # 路径有效，继续导入
                    start_dt = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
                    end_dt = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
                    
                    # 调用导入器的 import_data 方法, 传入 market
                    _success, _message, _bars = self.qlib_importer.import_data(
                        qlib_dir=QLIB_DATA_PATH,
                        market=market,
                        symbol=symbol,
                        exchange=exchange, 
                        interval=interval, 
                        start_date=start_dt,
                        end_date=end_dt
                    )
                    success = _success
                    message = _message
                    bars = _bars # Assign bars list
                    logger.info(f"QlibDataImporter result for {symbol}: Success={success}, Msg='{message}', Bars obtained: {len(bars)}")
                    
                    # 保存数据的逻辑移到 if/else 块外面，统一处理
                    # if success and bars:
                    #    ... (save logic removed from here) ...
            
            elif source.lower() == "csv": # Example: Placeholder for CSV import
                 message = f"CSV import for {symbol} not implemented yet."
                 logger.warning(message)
                 success = False

            else:
                message = f"Unsupported data source: {source}"
                logger.warning(message)
                success = False

            # --- 统一处理数据保存 --- 
            if success and bars:
                if not self.db:
                     message += " (Error: Cannot save bars, database connection not available.)"
                     logger.error(message)
                     success = False # Mark as failed if DB not available
                else:
                    logger.info(f"Saving {len(bars)} bars from {source} importer to database...")
                    count = self.db.save_bar_data(bars)
                    logger.info(f"Saved {count} bars for {symbol} from {source} importer.")
                    # 更新消息以反映保存结果
                    message = f"Successfully imported and saved {count} bars from {source} data."
            elif success and not bars:
                 logger.warning(f"Import reported success but returned no bars for {symbol} (Message: '{message}'). Nothing to save.")
                 # Keep success as True, message contains reason
            elif not success:
                 logger.error(f"Import failed for {symbol} (Message: '{message}'). Nothing saved.")
                 # Keep success as False

        except Exception as e:
            logger.error(f"Error during sync_target execution for {target}: {e}", exc_info=True)
            # Re-raise the exception so asyncio.gather logs it properly
            raise e 

# --- 移除 _import_data_from_qlib --- 

# +++ 修改 run_initial_data_sync 接收 db_instance +++ 
async def run_initial_data_sync(db_instance: BaseDatabase):
    """Initializes the DataSyncService with the provided db_instance and runs synchronization."""
    logger.info("Starting initial data sync process...")
    try:
        # +++ 使用传入的 db_instance 初始化服务 +++
        data_sync_service = DataSyncService(db_instance=db_instance)
        
        # 不再需要在内部检查 self.db, 因为初始化时已传入
        logger.info("DataSyncService initialized. Calling sync_all_targets...")
        await data_sync_service.sync_all_targets()
        logger.info("Initial data sync process finished.")

    except Exception as e:
        logger.error(f"Error during initial data sync execution: {e}", exc_info=True)