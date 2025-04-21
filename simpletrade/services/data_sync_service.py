"""
数据同步服务

负责根据配置，从不同的数据源同步历史数据到VnPy数据库。
"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import traceback
import os

from sqlalchemy.orm import Session

# 导入配置和模型
from simpletrade.config.settings import DATA_SYNC_TARGETS
from simpletrade.config.database import SessionLocal, get_db
from simpletrade.models.database import DataImportLog

# 导入VnPy相关
from vnpy.trader.constant import Exchange, Interval
import vnpy.trader.database as database_module
from vnpy.trader.object import BarData

# 导入数据导入器 (目前只有Qlib)
from simpletrade.apps.st_datamanager.importers.qlib_importer import QlibDataImporter
# TODO: Add imports for other importers (CSV, Yahoo etc.) when implemented

# 导入辅助函数
from .backtest_service import _get_vnpy_exchange, _get_vnpy_interval # Reuse helper functions

logger = logging.getLogger("simpletrade.services.data_sync_service")

class DataSyncService:
    """数据同步服务类"""

    def __init__(self):
        """初始化，加载目标列表"""
        self.targets = DATA_SYNC_TARGETS
        logger.info(f"DataSyncService initialized with {len(self.targets)} target(s).")

    def sync_all_targets(self):
        """同步所有配置的目标"""
        logger.info("Starting sync for all configured targets...")
        if not self.targets:
            logger.warning("No data sync targets configured in settings.py")
            return

        for target_config in self.targets:
            self.sync_target(target_config)
        
        logger.info("Finished sync for all configured targets.")

    def sync_target(self, target_config: Dict[str, Any]):
        """同步单个目标"""
        source = target_config.get("source")
        symbol = target_config.get("symbol")
        exchange_str = target_config.get("exchange")
        interval_str = target_config.get("interval")

        # 基本参数校验
        if not all([source, symbol, exchange_str, interval_str]):
            logger.error(f"Invalid target configuration, missing required fields: {target_config}")
            return
            
        logger.info(f"Starting sync for target: {source}/{symbol}.{exchange_str}[{interval_str}]")
        
        # 获取数据库会话
        db: Optional[Session] = None
        log_entry: Optional[DataImportLog] = None
        start_sync_time = datetime.now()

        try:
            db = SessionLocal()
            
            # --- 1. 查找或创建日志条目 --- 
            log_entry = db.query(DataImportLog).filter(
                DataImportLog.source == source,
                DataImportLog.symbol == symbol,
                DataImportLog.exchange == exchange_str,
                DataImportLog.interval == interval_str
            ).first()
            
            if not log_entry:
                log_entry = DataImportLog(
                    source=source,
                    symbol=symbol,
                    exchange=exchange_str,
                    interval=interval_str,
                    status='idle' # Start with idle
                )
                db.add(log_entry)
                db.commit() # Commit early to get an ID and establish the record
                db.refresh(log_entry)
                logger.info(f"Created new DataImportLog entry for target.")
            else:
                 logger.info(f"Found existing DataImportLog entry. Last imported date: {log_entry.last_import_date}, Status: {log_entry.status}")
            
            # 更新状态为 'syncing' 并记录尝试时间
            log_entry.status = 'syncing'
            log_entry.message = "Starting sync..."
            log_entry.last_attempt_time = start_sync_time 
            db.commit()

            # --- 2. 确定需要同步的开始日期 --- 
            # 从上次导入日期+1天开始，如果从未导入过，则从一个较早的默认日期开始 (可配置)
            # TODO: Make default start date configurable
            default_start_date = datetime(2010, 1, 1) 
            start_date = log_entry.last_import_date + timedelta(days=1) if log_entry.last_import_date else default_start_date
            
            # 结束日期通常是今天或昨天 (避免当天未收盘数据)
            # TODO: Make end date strategy configurable (e.g., up to yesterday)
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            
            if start_date >= end_date:
                 logger.info(f"Data is up-to-date for {symbol}.{exchange_str}[{interval_str}]. Last imported: {log_entry.last_import_date}. Skipping sync.")
                 log_entry.status = 'success' # Mark as success if already up-to-date
                 log_entry.message = "Data already up-to-date."
                 db.commit()
                 return # 无需同步

            logger.info(f"Calculated sync range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

            # --- 3. 准备参数 (枚举转换) ---
            vnpy_exchange = _get_vnpy_exchange(exchange_str)
            vnpy_interval = _get_vnpy_interval(interval_str)
            if not vnpy_exchange or not vnpy_interval:
                 raise ValueError(f"Invalid exchange '{exchange_str}' or interval '{interval_str}' for VnPy.")

            # --- 4. 选择并执行导入器 --- 
            bars_to_save: List[BarData] = []
            import_success = False
            import_message = ""

            if source == "qlib":
                qlib_importer = QlibDataImporter()
                 # 需要 Qlib 的特定目录, 这个逻辑需要完善，暂时用 backtest_service 的逻辑
                qlib_base_dir = "/qlib_data"
                qlib_specific_dir = None
                if vnpy_exchange in [Exchange.SSE, Exchange.SZSE, Exchange.BSE]:
                     qlib_specific_dir = os.path.join(qlib_base_dir, "cn_data")
                elif vnpy_exchange in [Exchange.NASDAQ, Exchange.NYSE, Exchange.AMEX]:
                     qlib_specific_dir = os.path.join(qlib_base_dir, "us_data")
                
                if qlib_specific_dir and os.path.exists(qlib_specific_dir):
                     success, message, loaded_bars = qlib_importer.import_data(
                         qlib_dir=qlib_specific_dir,
                         symbol=symbol,
                         exchange=vnpy_exchange,
                         interval=vnpy_interval,
                         start_date=start_date,
                         end_date=end_date
                     )
                     if success and loaded_bars:
                         bars_to_save = loaded_bars
                         import_success = True
                         import_message = message
                     else:
                         import_message = f"Qlib import failed: {message}"
                else:
                     import_message = f"Qlib specific directory not found or not configured: {qlib_specific_dir}"
            
            # elif source == "csv":
            #     csv_path = target_config.get("csv_path")
            #     if csv_path:
            #         csv_importer = CsvImporter() # Assuming CsvImporter exists
            #         success, message, loaded_bars = csv_importer.import_data(csv_path, symbol, exchange, interval, start_date, end_date)
            #         # ... handle result ...
            #     else:
            #         import_message = "CSV path not configured."
            
            # elif source == "yahoo":
            #     # ... call Yahoo importer ...
            
            else:
                import_message = f"Unsupported data source: {source}"
                logger.error(import_message)

            # --- 5. 保存数据到数据库 --- 
            if import_success and bars_to_save:
                 logger.info(f"Attempting to save {len(bars_to_save)} bars for {symbol}.{exchange_str} to VnPy database...")
                 try:
                     # Get the configured database manager instance from VnPy
                     database_manager = database_module.get_database()
                     logger.info(f"Obtained database manager instance: {type(database_manager)}")
                     
                     # Save the bar data using the obtained manager
                     saved_count = database_manager.save_bar_data(bars_to_save)
                     logger.info(f"Successfully saved {saved_count} bars to VnPy database for {symbol}.{exchange_str}.")

                     # --- Update log entry on successful save ---
                     log_entry.status = 'success'
                     # Use the calculated end_date for the last import date
                     # Ensure end_date is a date object if last_import_date expects one
                     log_entry.last_import_date = end_date.date() if isinstance(end_date, datetime) else end_date
                     log_entry.message = f"Successfully imported {saved_count} bars up to {log_entry.last_import_date.strftime('%Y-%m-%d')}. {import_message or ''}".strip()
                     db.commit()
                     
                 except Exception as db_save_e:
                     logger.error(f"Failed to save bars to VnPy database: {db_save_e}\\n{traceback.format_exc()}")
                     log_entry.status = 'failed'
                     log_entry.message = f"DB save error: {db_save_e}"
                     db.commit()
            elif not import_success:
                 # 如果导入步骤失败
                 log_entry.status = 'failed'
                 log_entry.message = import_message
                 db.commit()
            else: # Import success but no bars found in the date range
                 logger.info(f"No new data found for {symbol}.{exchange_str} in range {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.")
                 log_entry.status = 'success' # Mark as success, even if no new bars
                 log_entry.message = f"No new data in specified range up to {end_date.strftime('%Y-%m-%d')}."
                 # Optionally update last_import_date to end_date? Needs careful thought.
                 db.commit()
                 
        except Exception as e:
            logger.error(f"Error syncing target {target_config}: {e}\\n{traceback.format_exc()}")
            if db and log_entry: # Try to update log even if error occurred mid-process
                 try:
                     log_entry.status = 'failed'
                     log_entry.message = f"Sync error: {e}"
                     db.commit()
                 except Exception as log_update_e:
                      logger.error(f"Failed to update log status on error: {log_update_e}")
                      db.rollback() # Rollback if log update fails
        finally:
            if db:
                db.close()
                logger.debug(f"Database session closed for target sync: {symbol}.{exchange_str}")

# --- Function to be called on startup ---
def run_initial_data_sync():
    """执行初始数据同步任务"""
    logger.info("Executing initial data synchronization...")
    try:
        sync_service = DataSyncService()
        sync_service.sync_all_targets()
        logger.info("Initial data synchronization task finished.")
    except Exception as e:
        logger.error(f"Error during initial data synchronization task: {e}", exc_info=True)

# --- Example Usage (Can be called from main.py or a scheduler) ---
# if __name__ == "__main__":
#     # Configure logging if running standalone
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     
#     run_initial_data_sync() # Call the wrapper function 