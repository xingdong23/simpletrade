"""
数据同步服务

负责根据配置，从不同的数据源同步历史数据到VnPy数据库。
"""

import logging # Keep import for now, but won't use logger object directly below
from datetime import datetime, timedelta, date, timezone
from typing import List, Dict, Any, Optional
import traceback
import os
import asyncio

from sqlalchemy.orm import Session

# 导入配置和模型
from simpletrade.config.settings import DATA_SYNC_TARGETS
from simpletrade.config.database import SessionLocal, get_db
from simpletrade.models.database import DataImportLog

# 导入VnPy相关
from vnpy.trader.constant import Exchange, Interval
import vnpy.trader.database as database_module
from vnpy.trader.object import BarData
# from vnpy.trader.setting import SETTINGS as VNPY_SETTINGS # Keep this import
# from vnpy.trader.database.mysql import MysqlDatabase # Remove direct import

# 导入数据导入器 (目前只有Qlib)
from simpletrade.apps.st_datamanager.importers.qlib_importer import QlibDataImporter
# TODO: Add imports for other importers (CSV, Yahoo etc.) when implemented

# 导入辅助函数
from .backtest_service import _get_vnpy_exchange, _get_vnpy_interval # Reuse helper functions

# Attempt to import the specific MySQL database class
# NOTE: The exact path might vary based on VnPy version
try:
    from vnpy.database.mysql import MysqlDatabaseManager
    # print("[Data Sync Service] Successfully imported MysqlDatabaseManager") # REMOVE DEBUG
except ImportError:
    # print("[Data Sync Service] ERROR: Failed to import ... Trying vnpy_mysql driver...") # REMOVE DEBUG
    try:
        # Older versions might use vnpy_mysql
        from vnpy_mysql import MysqlDatabaseManager
        # print("[Data Sync Service] Successfully imported MysqlDatabaseManager from vnpy_mysql") # REMOVE DEBUG
    except ImportError:
        # print("[Data Sync Service] ERROR: Failed to import ... Cannot proceed...") # REMOVE DEBUG
        MysqlDatabaseManager = None # Set to None to handle error below

logger = logging.getLogger("simpletrade.services.data_sync_service") # Restore logger usage

class DataSyncService:
    """数据同步服务类"""

    def __init__(self, db):
        """
        Initializes the DataSyncService.
        """
        # print("[DataSyncService] Initializing...") # REMOVE DEBUG
        if db is None:
             # print("[DataSyncService] Error: Received None for database instance.") # REMOVE DEBUG
             raise ValueError("Database instance is None.")
        self.db = db
        self.targets = DATA_SYNC_TARGETS
        # print(f"[DataSyncService] Initialization complete. DB Type: {type(self.db)}, Targets: {self.targets}") # REMOVE DEBUG

    async def sync_all_targets(self):
        """
        Synchronizes data for all targets specified in the configuration.
        """
        # print("[DataSyncService] Starting sync_all_targets...") # REMOVE DEBUG
        if not self.targets:
            # print("[DataSyncService] No data synchronization targets configured.") # REMOVE DEBUG
            return

        if not self.db:
            # print("[DataSyncService] Error: Database manager not available in sync_all_targets.") # REMOVE DEBUG
            return

        tasks = [self.sync_target(target) for target in self.targets]
        await asyncio.gather(*tasks)
        # print("[DataSyncService] Finished sync_all_targets.") # REMOVE DEBUG

    async def sync_target(self, target: dict):
        """
        Synchronizes data for a single target.
        """
        source = target.get("source")
        symbol = target.get("symbol")
        exchange_str = target.get("exchange")
        interval_str = target.get("interval")
        start_date_str = target.get("start_date", "2020-01-01") # Default start date
        end_date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d') # Default to today

        # print(f"[DataSyncService] Processing target: {target}") # REMOVE DEBUG

        if not all([source, symbol, exchange_str, interval_str]):
            # print(f"[DataSyncService] Skipping invalid target: {target}") # REMOVE DEBUG
            return

        try:
            exchange = Exchange(exchange_str)
            interval = Interval(interval_str)
        except ValueError as e:
            # print(f"[DataSyncService] Invalid exchange or interval in target {target}: {e}") # REMOVE DEBUG
            # Consider logging this error properly later
            return

        # Log checking is still commented out
        # print(f"[DataSyncService] Skipping log check for {symbol} (temporarily disabled).") # REMOVE DEBUG

        success = False
        message = ""
        try:
            # print(f"[DataSyncService] Starting data import for {symbol} from {source}...") # REMOVE DEBUG
            if source.lower() == "qlib":
                success, message = await self._import_data_from_qlib(symbol, exchange_str, interval_str, start_date_str, end_date_str)
            # Add other sources here (e.g., "tushare", "baostock")
            # elif source.lower() == "tushare":
            #     success, message = await self._import_data_from_tushare(...)
            else:
                message = f"Unsupported data source: {source}"
                # print(f"[DataSyncService] {message}") # REMOVE DEBUG

            # print(f"[DataSyncService] Import result for {symbol} from {source}: Success={success}, Msg='{message}'") # REMOVE DEBUG
            # Log updating is still commented out
            # print(f"[DataSyncService] Skipping log update for {symbol} (temporarily disabled).") # REMOVE DEBUG

        except Exception as e:
            error_msg = f"Error syncing target {target}: {e}"
            # print(f"[DataSyncService] {error_msg}") # REMOVE DEBUG
            # Consider logging this error properly later
            print(traceback.format_exc()) # Keep traceback for errors
            # Log updating on error is still commented out
            # print(f"[DataSyncService] Skipping log update on error for {symbol} (temporarily disabled).") # REMOVE DEBUG

    def _check_import_log(self, source: str, symbol: str, exchange_str: str, interval_str: str) -> bool:
        """
        Checks the DataImportLog table to see if data has been successfully imported
        or failed within the cooldown period (e.g., 1 day).
        Uses print for logging. Returns True if import should be skipped, False otherwise.
        """
        print(f"[DataSyncService] Checking import log for {source}, {symbol}, {exchange_str}, {interval_str}")
        cooldown_period = timedelta(days=1)
        cutoff_time = datetime.now(timezone.utc) - cooldown_period

        session = None
        try:
            # Assuming db object has a way to get a session or perform queries
            # This part might need adjustment based on the actual db object type
            # For SQLAlchemy:
            if hasattr(self.db, 'SessionLocal'): # Common pattern
                 session = self.db.SessionLocal()
                 log_entry = session.query(DataImportLog).filter(
                     DataImportLog.source == source,
                     DataImportLog.symbol == symbol,
                     DataImportLog.exchange == exchange_str,
                     DataImportLog.interval == interval_str,
                     DataImportLog.last_attempted >= cutoff_time # Check if attempted recently
                 ).order_by(DataImportLog.last_attempted.desc()).first()
            elif hasattr(self.db, 'load_bar_data'): # Adapt if it's closer to vnpy's direct DB interface
                 # Vnpy's database manager doesn't directly expose general querying like this.
                 # We might need to rethink how DataImportLog is accessed if using vnpy's db manager directly.
                 # For now, assume an SQLAlchemy-like session is available via the passed 'db' object
                 # or handle this logic differently based on 'db' type.
                 print("[DataSyncService] _check_import_log: Direct query via vnpy db manager not standard. Assuming SQLAlchemy session via self.db.SessionLocal for now.")
                 # Placeholder: If not SQLAlchemy, this check might always return False or need rework.
                 return False # Assume we should attempt import if unsure how to check log

            if log_entry:
                if log_entry.success:
                    print(f"[DataSyncService] Found successful import log entry from {log_entry.last_attempted}. Skipping.")
                    return True # Successfully imported recently
                else:
                    print(f"[DataSyncService] Found failed import log entry from {log_entry.last_attempted}. Skipping due to cooldown.")
                    return True # Failed recently, skip due to cooldown
            else:
                 print(f"[DataSyncService] No recent import log entry found. Proceeding with import.")
                 return False # No recent attempt, proceed
        except Exception as e:
             print(f"[DataSyncService] Error checking import log: {e}")
             # import traceback # Already imported
             print(traceback.format_exc())
             return False # Proceed with import if checking failed
        finally:
            if session:
                session.close()

    def _update_import_log(self, source: str, symbol: str, exchange_str: str, interval_str: str, success: bool, message: str = ""):
        """
        Updates or creates an entry in the DataImportLog table.
        Uses print for logging.
        """
        print(f"[DataSyncService] Updating import log for {source}, {symbol}, {exchange_str}, {interval_str}. Success: {success}")
        session = None
        try:
             # Assuming db object has a way to get a session
            if hasattr(self.db, 'SessionLocal'):
                session = self.db.SessionLocal()
                log_entry = session.query(DataImportLog).filter(
                    DataImportLog.source == source,
                    DataImportLog.symbol == symbol,
                    DataImportLog.exchange == exchange_str,
                    DataImportLog.interval == interval_str
                ).first()

                if log_entry:
                    log_entry.success = success
                    log_entry.message = message
                    log_entry.last_attempted = datetime.now(timezone.utc)
                else:
                    log_entry = DataImportLog(
                        source=source,
                        symbol=symbol,
                        exchange=exchange_str,
                        interval=interval_str,
                        success=success,
                        message=message,
                        last_attempted=datetime.now(timezone.utc)
                    )
                    session.add(log_entry)
                session.commit()
                print("[DataSyncService] Import log updated successfully.")
            else:
                 print("[DataSyncService] _update_import_log: Cannot update log, self.db does not have SessionLocal.")

        except Exception as e:
            print(f"[DataSyncService] Error updating import log: {e}")
            # import traceback # Already imported
            print(traceback.format_exc())
            if session:
                session.rollback()
        finally:
            if session:
                session.close()

    async def _import_data_from_qlib(self, symbol: str, exchange_str: str, interval_str: str, start_date: str, end_date: str) -> tuple[bool, str]:
        """
        Imports data from Qlib for the given parameters and saves it using the database manager.
        """
        # print(f"[DataSyncService] Importing Qlib data for: {symbol}, {exchange_str}, {interval_str}, {start_date} to {end_date}") # REMOVE DEBUG
        try:
            # Ensure qlib is initialized (consider doing this once at service start)
            # from qlib.config import REG_CN
            # from qlib.data import D
            # provider_uri = app_settings.QLIB_PROVIDER_URI # This would fail as app_settings is removed
            # Check if QLIB_PROVIDER_URI is needed and where it should come from
            # It's NOT in the current settings.py. Needs to be added or handled differently.
            # For now, commenting out the qlib init part that depends on it.
            # provider_uri = None # Placeholder
            # if not provider_uri:
            #     print("[DataSyncService] QLIB_PROVIDER_URI not configured (placeholder). Skipping Qlib init.")
            #     # return False, "QLIB_PROVIDER_URI not configured"
            # else:
            #    qlib.init(provider_uri=provider_uri, region=REG_CN)
            #    print("[DataSyncService] Qlib initialized for import.") # Potentially slow to init repeatedly

            # This requires Qlib to be installed and configured correctly in the environment
            # Dynamically import qlib related modules only when needed
            try:
                import qlib
                from qlib.data import D
                from qlib.config import REG_CN
            except ImportError:
                 # print("[DataSyncService] Qlib not installed or found.") # REMOVE DEBUG
                 return False, "Qlib library not installed."

            # Map interval format if necessary (e.g., '1d' for Qlib, 'd' or '1d' for VnPy)
            # VnPy Interval enum -> Qlib frequency string
            interval_map = {
                Interval.MINUTE: "1m", # Qlib might need specific minute frequencies
                Interval.HOUR: "60m", # Adjust as needed
                Interval.DAILY: "1d",
                # Add mappings for weekly, monthly if needed and supported by Qlib/VnPy
            }
            qlib_freq = interval_map.get(Interval(interval_str))
            if not qlib_freq:
                return False, f"Unsupported interval for Qlib import: {interval_str}"

            # Format symbol for Qlib (e.g., SH600000)
            # Assuming exchange_str is like "SSE", "SZSE" and symbol is "600000"
            qlib_symbol = f"{exchange_str.upper()}{symbol}" # Adjust formatting based on Qlib needs

            # print(f"[DataSyncService] Fetching data from Qlib: Symbol={qlib_symbol}, Freq={qlib_freq}, Start={start_date}, End={end_date}") # REMOVE DEBUG
            # Fetch data using Qlib
            # Note: Qlib's fields might differ ('open', 'high', 'low', 'close', 'volume', 'factor')
            # You might need ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOL'] depending on your Qlib data source
            fields = ['$open', '$high', '$low', '$close', '$volume'] # Use Qlib's dynamic field names
            data_df = D.features([qlib_symbol], fields, start_time=start_date, end_time=end_date, freq=qlib_freq)

            if data_df.empty:
                # print(f"[DataSyncService] No data found in Qlib for {qlib_symbol} in the specified period.") # REMOVE DEBUG
                return False, "No data found in Qlib"

            # Rename columns to match VnPy's BarData requirements
            # Qlib fields: $open, $high, $low, $close, $volume
            # VnPy fields: open_price, high_price, low_price, close_price, volume
            rename_map = {
                '$open': 'open_price',
                '$high': 'high_price',
                '$low': 'low_price',
                '$close': 'close_price',
                '$volume': 'volume'
            }
            data_df = data_df.rename(columns=rename_map)

            # Reset index to get datetime and symbol
            data_df = data_df.reset_index()
            # Qlib index levels might be ['datetime', 'instrument']

            # Convert to VnPy BarData objects
            from vnpy.trader.object import BarData
            from vnpy.trader.constant import Exchange, Interval # Re-import for clarity

            bars = []
            for _, row in data_df.iterrows():
                # Ensure datetime is timezone-aware (UTC is standard for VnPy)
                dt = row['datetime'].tz_localize(None).tz_localize(timezone.utc) # Assuming Qlib datetime is naive

                bar = BarData(
                    symbol=symbol,
                    exchange=Exchange(exchange_str),
                    datetime=dt,
                    interval=Interval(interval_str),
                    volume=row['volume'],
                    open_price=row['open_price'],
                    high_price=row['high_price'],
                    low_price=row['low_price'],
                    close_price=row['close_price'],
                    gateway_name="DB", # Use "DB" or a specific identifier
                    # open_interest=row.get('open_interest', 0) # Add if available in Qlib data
                )
                bars.append(bar)

            if not bars:
                # print("[DataSyncService] No bars created from Qlib data.") # REMOVE DEBUG
                return False, "Failed to convert Qlib data to BarData"

            # Save bars to database using the vnpy database manager
            # print(f"[DataSyncService] Saving {len(bars)} bars to database...") # REMOVE DEBUG
            count = self.db.save_bar_data(bars)
            # print(f"[DataSyncService] Saved {count} bars for {symbol} from Qlib.") # REMOVE DEBUG
            return True, f"Successfully imported {count} bars."

        except Exception as e:
            error_msg = f"Failed to import Qlib data for {symbol}: {e}"
            # print(f"[DataSyncService] {error_msg}") # REMOVE DEBUG
            print(traceback.format_exc()) # Keep traceback for errors
            return False, error_msg

# Define the function to run data synchronization
async def run_initial_data_sync():
    """
    Initializes the DataSyncService and runs synchronization for all configured targets.
    Directly instantiates the MysqlDatabaseManager, bypassing get_database().
    """
    # print("[Data Sync Thread] Entered run_initial_data_sync.") # REMOVE DEBUG
    db = None
    try:
        from vnpy.trader.setting import SETTINGS
        # print(f"[Data Sync Thread] Imported SETTINGS inside function scope.") # REMOVE DEBUG
        # print(f"[Data Sync Thread] SETTINGS check before direct instantiation: ...") # REMOVE DEBUG

        from vnpy.trader.database import get_database # Keep this import for now, although bypassed below
        # print(f"[Data Sync Thread] Imported get_database inside function scope.") # REMOVE DEBUG

        # print("[Data Sync Thread] Directly instantiating MysqlDatabaseManager...") # REMOVE DEBUG
        if MysqlDatabaseManager:
            db = MysqlDatabaseManager()
            # print(f"[Data Sync Thread] Database instance directly instantiated: {type(db)}") # REMOVE DEBUG
        else:
            # print("[Data Sync Thread] ERROR: MysqlDatabaseManager class not available...") # REMOVE DEBUG
            return

        if db is None:
            # print("[Data Sync Thread] Failed to directly instantiate database instance...") # REMOVE DEBUG
            return

        # print("[Data Sync Thread] Creating DataSyncService instance...") # REMOVE DEBUG
        data_sync_service = DataSyncService(db)
        # print("[Data Sync Thread] DataSyncService instance created.") # REMOVE DEBUG

        # print("[Data Sync Thread] Calling sync_all_targets...") # REMOVE DEBUG
        await data_sync_service.sync_all_targets()
        # print("[Data Sync Thread] sync_all_targets finished.") # REMOVE DEBUG

    except Exception as e:
        # print(f"[Data Sync Thread] Error during initial data sync: {e}") # REMOVE DEBUG
        # Keep traceback for errors
        print(traceback.format_exc())

    # print("[Data Sync Thread] Exiting run_initial_data_sync.") # REMOVE DEBUG

# --- Example Usage (Can be called from main.py or a scheduler) ---
# if __name__ == "__main__":
#     # Configure logging if running standalone
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     
#     run_initial_data_sync() # Call the wrapper function 