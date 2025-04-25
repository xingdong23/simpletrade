"""
数据同步服务

负责根据配置，从不同的数据源同步历史数据到VnPy数据库。
"""

import logging
import os
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
import pandas as pd
from pandas.tseries.offsets import BDay

from simpletrade.config.settings import DATA_SYNC_TARGETS, DATA_SYNC_CONFIG, QLIB_DATA_PATH
from simpletrade.models.database import DataImportLog
from simpletrade.apps.st_datamanager.importers import ImporterFactory

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import BaseDatabase
from vnpy.trader.object import BarData

logger = logging.getLogger("simpletrade.services.data_sync_service")

class DataSyncService:
    """数据同步服务类
    
    负责根据配置从不同数据源同步历史数据到VnPy数据库。
    """

    def __init__(self, db_instance: BaseDatabase):
        """初始化数据同步服务
        
        Args:
            db_instance: 数据库实例
        """
        if not isinstance(db_instance, BaseDatabase):
            raise TypeError("DataSyncService requires a valid vnpy.trader.database.BaseDatabase instance.")
             
        self.db: BaseDatabase = db_instance
        logger.info(f"DataSyncService initialized with database instance: {type(self.db)}")
        self.targets = [target for target in DATA_SYNC_TARGETS if target.get("enabled", True)]
        logger.info(f"Found {len(self.targets)} enabled data sync targets")

    def _update_import_log(self, source: str, symbol: str, exchange: Exchange, interval: Interval, 
                           success: bool, message: str, last_begin_date: Optional[datetime] = None, 
                           last_end_date: Optional[datetime] = None):
        """更新数据导入日志
        
        Args:
            source: 数据源名称
            symbol: 品种代码
            exchange: 交易所
            interval: K线周期
            success: 是否导入成功
            message: 导入消息
            last_begin_date: 导入的数据开始日期
            last_end_date: 导入的数据结束日期
        """
        try:
            from sqlalchemy.orm import Session
            from sqlalchemy import create_engine
            from simpletrade.config.settings import DB_CONFIG
            
            # 创建数据库连接
            db_url = f"mysql+pymysql://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
            engine = create_engine(db_url)
            
            with Session(engine) as session:
                # 查找现有记录
                log_entry = session.query(DataImportLog).filter_by(
                    source=source,
                    symbol=symbol,
                    exchange=exchange.value,
                    interval=interval.value
                ).first()
                
                # 更新或创建记录
                current_time = datetime.now()
                if log_entry:
                    log_entry.last_attempt_time = current_time
                    log_entry.status = 'success' if success else 'failed'
                    log_entry.message = message
                    if last_begin_date and success:
                        log_entry.last_begin_date = last_begin_date
                    if last_end_date and success:
                        log_entry.last_end_date = last_end_date
                else:
                    log_entry = DataImportLog(
                        source=source,
                        symbol=symbol,
                        exchange=exchange.value,
                        interval=interval.value,
                        last_attempt_time=current_time,
                        status='success' if success else 'failed',
                        message=message,
                        last_begin_date=last_begin_date if success else None,
                        last_end_date=last_end_date if success else None
                    )
                    session.add(log_entry)
                
                session.commit()
                logger.info(f"Updated import log for {symbol} from {source}. Status: {'success' if success else 'failed'}")
        except Exception as e:
            logger.error(f"Error updating import log: {e}", exc_info=True)

    def _get_last_import_date(self, source: str, symbol: str, exchange: str, interval: str) -> Optional[datetime]:
        """获取上次导入的结束日期
        
        Args:
            source: 数据源名称
            symbol: 品种代码
            exchange: 交易所
            interval: K线周期
            
        Returns:
            上次导入的结束日期，如果没有记录则返回None
        """
        try:
            from sqlalchemy.orm import Session
            from sqlalchemy import create_engine
            from simpletrade.config.settings import DB_CONFIG
            
            # 创建数据库连接
            db_url = f"mysql+pymysql://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
            engine = create_engine(db_url)
            
            with Session(engine) as session:
                # 查找现有记录
                log_entry = session.query(DataImportLog).filter_by(
                    source=source,
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval
                ).first()
                
                if log_entry and log_entry.last_end_date:
                    logger.info(f"Found previous import record for {symbol} ({source}): last end date {log_entry.last_end_date}")
                    return log_entry.last_end_date
                
                logger.info(f"No previous import record found for {symbol} ({source})")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving last import date: {e}", exc_info=True)
            return None
            
    def _get_last_begin_date(self, source: str, symbol: str, exchange: str, interval: str) -> Optional[datetime]:
        """获取上次导入的开始日期
        
        Args:
            source: 数据源名称
            symbol: 品种代码
            exchange: 交易所
            interval: K线周期
            
        Returns:
            上次导入的开始日期，如果没有记录则返回None
        """
        try:
            from sqlalchemy.orm import Session
            from sqlalchemy import create_engine
            from simpletrade.config.settings import DB_CONFIG
            
            # 创建数据库连接
            db_url = f"mysql+pymysql://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"
            engine = create_engine(db_url)
            
            with Session(engine) as session:
                # 查找现有记录
                log_entry = session.query(DataImportLog).filter_by(
                    source=source,
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval
                ).first()
                
                if log_entry and log_entry.last_begin_date:
                    logger.info(f"Found previous import record for {symbol} ({source}): last begin date {log_entry.last_begin_date}")
                    return log_entry.last_begin_date
                
                logger.info(f"No previous import record found for {symbol} ({source})")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving last begin date: {e}", exc_info=True)
            return None

    def _get_db_date_range(self, symbol: str, exchange: Exchange, interval: Interval) -> Tuple[Optional[datetime], Optional[datetime]]:
        """从数据库获取K线数据的日期范围
        
        Args:
            symbol: 品种代码
            exchange: 交易所
            interval: K线周期
            
        Returns:
            (最早日期, 最晚日期) 元组，如果没有数据则返回 (None, None)
        """
        if not self.db:
            logger.warning("Cannot check database for bar date range: database connection not available")
            return None, None
            
        try:
            # 使用数据库查询函数获取日期范围
            bars = self.db.load_bar_data(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start=datetime(1970, 1, 1),  # 从最早日期开始
                end=datetime.now(timezone.utc)  # 到当前日期
            )
            
            if not bars:
                logger.info(f"No existing data in database for {symbol}")
                return None, None
                
            earliest_date = min(bar.datetime for bar in bars)
            latest_date = max(bar.datetime for bar in bars)
            logger.info(f"Data range in database for {symbol}: {earliest_date} to {latest_date}")
            return earliest_date, latest_date
            
        except Exception as e:
            logger.error(f"Error querying database for bar date range: {e}", exc_info=True)
            return None, None

    def _get_db_existing_dates(self, symbol: str, exchange: Exchange, interval: Interval) -> Set[datetime.date]:
        """获取数据库中指定品种已有数据的日期集合
        
        Args:
            symbol: 品种代码
            exchange: 交易所
            interval: K线周期
            
        Returns:
            已有数据的日期集合（只包含日期部分，不含时间）
        """
        if not self.db:
            logger.warning("Cannot check database for existing dates: database connection not available")
            return set()
            
        try:
            # 使用数据库查询函数获取现有数据
            bars = self.db.load_bar_data(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                start=datetime(1970, 1, 1),  # 从最早日期开始
                end=datetime.now(timezone.utc)  # 到当前日期
            )
            
            if not bars:
                logger.info(f"No existing data in database for {symbol}")
                return set()
            
            # 获取所有日期（只保留日期部分，不含时间）
            existing_dates = {bar.datetime.date() for bar in bars}
            logger.info(f"Found {len(existing_dates)} existing dates in database for {symbol}")
            return existing_dates
            
        except Exception as e:
            logger.error(f"Error querying database for existing dates: {e}", exc_info=True)
            return set()

    def _get_trading_dates(self, start_date: datetime, end_date: datetime, exchange: Exchange) -> List[datetime.date]:
        """根据交易所获取指定日期范围内的所有交易日
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            exchange: 交易所
            
        Returns:
            交易日列表（只包含日期部分，不含时间）
        """
        try:
            # 1. 基本方法：使用pandas生成交易日历（不含周末）
            # 使用 business days 作为基础，但不考虑节假日
            date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq=BDay())
            
            # 2. 未来可以考虑更复杂的方法：
            # a) 根据交易所区分不同市场的交易日历（包括节假日）
            # b) 使用专门的交易日历库或API
            # c) 维护自己的交易日历数据库
            
            # 转换为日期列表
            trading_dates = [d.date() for d in date_range]
            
            logger.info(f"Generated {len(trading_dates)} trading dates from {start_date.date()} to {end_date.date()}")
            return trading_dates
            
        except Exception as e:
            logger.error(f"Error generating trading dates: {e}", exc_info=True)
            # 如果生成失败，返回从起始日期到结束日期的全部日期（包括周末和节假日）
            all_dates = [(start_date + timedelta(days=i)).date() for i in range((end_date - start_date).days + 1)]
            logger.warning(f"Falling back to all calendar dates: {len(all_dates)} dates")
            return all_dates

    def _group_dates_into_ranges(self, dates: List[datetime.date], max_gap: int = 5) -> List[Tuple[datetime, datetime]]:
        """将日期列表分组成连续区间
        
        Args:
            dates: 日期列表（已排序）
            max_gap: 允许的最大日期间隔，超过此值会分为不同区间
            
        Returns:
            日期区间列表，每个元素为 (开始日期, 结束日期) 元组
        """
        if not dates:
            return []
            
        # 对日期进行排序
        sorted_dates = sorted(dates)
        
        # 初始化区间列表和当前区间
        ranges = []
        current_range_start = sorted_dates[0]
        current_range_end = sorted_dates[0]
        
        # 遍历日期列表，将连续的日期合并为区间
        for i in range(1, len(sorted_dates)):
            date = sorted_dates[i]
            prev_date = sorted_dates[i-1]
            
            # 计算与前一天的差距（天数）
            gap = (date - prev_date).days
            
            # 如果差距小于等于允许的最大间隔，扩展当前区间
            if gap <= max_gap:
                current_range_end = date
            # 否则，结束当前区间并开始新区间
            else:
                # 将当前区间转换为datetime对象添加到结果中
                ranges.append((
                    datetime.combine(current_range_start, datetime.min.time()),
                    datetime.combine(current_range_end, datetime.min.time())
                ))
                # 开始新区间
                current_range_start = date
                current_range_end = date
        
        # 添加最后一个区间
        ranges.append((
            datetime.combine(current_range_start, datetime.min.time()),
            datetime.combine(current_range_end, datetime.min.time())
        ))
        
        logger.info(f"Grouped {len(dates)} dates into {len(ranges)} continuous ranges")
        for i, (start, end) in enumerate(ranges):
            logger.debug(f"Range {i+1}: {start.date()} to {end.date()}")
            
        return ranges

    async def sync_all_targets(self):
        """同步所有配置的目标数据"""
        if not self.targets:
            logger.warning("No data synchronization targets configured or enabled.")
            return

        if not self.db:
            logger.error("Database instance not available in sync_all_targets.")
            return

        tasks = [self.sync_target(target) for target in self.targets]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 记录每个任务的结果
        for i, result in enumerate(results):
            target = self.targets[i]
            if isinstance(result, Exception):
                logger.error(f"Error syncing target {target}: {result}", exc_info=result)

        logger.info("Finished sync_all_targets run.")

    async def sync_target(self, target: dict):
        """同步单个目标数据
        
        Args:
            target: 目标配置字典
        """
        # 提取源和基本符号信息（用于日志记录）
        source = target.get("source")
        symbol = target.get("symbol")
        
        if not all([source, symbol]):
            logger.warning(f"Skipping invalid target (missing source or symbol): {target}")
            return

        try:
            # 获取交易所和周期（仅用于日志记录）
            exchange_str = target.get("exchange", "")
            interval_str = target.get("interval", "")
            
            try:
                exchange = Exchange(exchange_str)
                interval = Interval(interval_str)
            except ValueError as e:
                logger.error(f"Invalid exchange or interval in target {target}: {e}")
                return
                
            logger.info(f"Starting data import for {symbol} from {source}...")
            
            # 使用工厂创建导入器
            importer = ImporterFactory.create_importer(source)
            if not importer:
                message = f"Unsupported data source: {source}"
                logger.warning(message)
                self._update_import_log(source, symbol, exchange, interval, False, message)
                return
            
            # 让导入器从目标配置中提取并验证所需参数
            try:
                params = importer.extract_and_validate_params(target)
                
                # 从参数中获取基本信息
                symbol = params.pop("symbol")
                exchange_name = params.pop("exchange")
                interval_name = params.pop("interval")
                start_date_str = params.pop("start_date", None)
                end_date_str = params.pop("end_date", None)
                
                # 转换类型
                exchange = Exchange(exchange_name)
                interval = Interval(interval_name)
                
                # 转换日期
                configured_start_dt = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
                end_dt = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else datetime.now()
                
                # 如果没有配置开始日期，尝试从导入日志获取
                if not configured_start_dt:
                    last_end_date = self._get_last_import_date(
                        source=source,
                        symbol=symbol,
                        exchange=exchange_name,
                        interval=interval_name
                    )
                    
                    if last_end_date:
                        # 有导入记录，设置开始日期为最后导入日期的下一天
                        configured_start_dt = last_end_date + timedelta(days=1)
                        logger.info(f"Using start date based on import log: {configured_start_dt}")
                    else:
                        # 默认使用较早的开始日期
                        configured_start_dt = datetime(2010, 1, 1)
                        logger.info(f"No start date configured or found in logs. Using default: {configured_start_dt}")
                
                # 精确到日的智能数据导入
                if interval == Interval.DAILY and self.db:
                    # 1. 获取数据库中已有的日期
                    existing_dates = self._get_db_existing_dates(symbol, exchange, interval)
                    
                    # 2. 获取应该有的交易日期
                    all_trading_dates = self._get_trading_dates(configured_start_dt, end_dt, exchange)
                    
                    # 3. 计算缺失的日期
                    missing_dates = [d for d in all_trading_dates if d not in existing_dates]
                    
                    if not missing_dates:
                        logger.info(f"No missing dates found for {symbol} between {configured_start_dt.date()} and {end_dt.date()}")
                        self._update_import_log(
                            source=source, 
                            symbol=symbol, 
                            exchange=exchange, 
                            interval=interval, 
                            success=True, 
                            message=f"No missing dates to import",
                            last_begin_date=configured_start_dt,
                            last_end_date=end_dt
                        )
                        return
                    
                    logger.info(f"Found {len(missing_dates)} missing dates for {symbol}")
                    
                    # 4. 将缺失日期分组为连续区间
                    missing_ranges = self._group_dates_into_ranges(missing_dates)
                    
                    # 5. 针对每个缺失区间导入数据
                    all_bars = []
                    for start_range, end_range in missing_ranges:
                        logger.info(f"Importing data for missing range: {start_range.date()} to {end_range.date()}")
                        success, message, bars = importer.import_data(
                            symbol=symbol,
                            exchange=exchange,
                            interval=interval,
                            start_date=start_range,
                            end_date=end_range,
                            **params  # 传递其他提取的参数
                        )
                        
                        if success and bars:
                            # 筛选只包含缺失日期的数据
                            filtered_bars = []
                            for bar in bars:
                                if bar.datetime.date() in missing_dates:
                                    filtered_bars.append(bar)
                                    
                            logger.info(f"Retrieved {len(bars)} bars, {len(filtered_bars)} are for missing dates")
                            all_bars.extend(filtered_bars)
                        else:
                            logger.warning(f"Failed to import data for range {start_range.date()} to {end_range.date()}: {message}")
                    
                    # 保存所有导入的数据
                    if all_bars:
                        logger.info(f"Saving {len(all_bars)} bars for missing dates from {source} importer to database...")
                        count = self.db.save_bar_data(all_bars)
                        logger.info(f"Saved {count} bars for {symbol} from {source} importer.")
                        
                        # 找出最新日期（改为记录整个范围）
                        if all_bars:
                            earliest_date = min(bar.datetime for bar in all_bars)
                            latest_date = max(bar.datetime for bar in all_bars)
                            logger.info(f"Imported data range: {earliest_date} to {latest_date}")
                        else:
                            earliest_date = None
                            latest_date = None
                        
                        # 更新消息以反映保存结果
                        message = f"Successfully imported and saved {count} bars for missing dates from {source} data."
                        
                        # 导入成功，记录到导入日志
                        self._update_import_log(source, symbol, exchange, interval, True, message, earliest_date, latest_date)
                    else:
                        logger.warning(f"No data was imported for missing dates of {symbol}.")
                        self._update_import_log(source, symbol, exchange, interval, True, "No data available for missing dates", None, None)
                        
                    return
                
                # 如果不是日线数据或没有数据库连接，使用区间导入方式
                # 获取数据库中已有数据的日期范围
                db_earliest_date, db_latest_date = self._get_db_date_range(symbol, exchange, interval)
                
                if db_earliest_date and db_latest_date:
                    # 数据库中已有数据，判断是否需要补充历史数据和更新新数据
                    
                    # 计算需要导入的日期区间（可能有多个）
                    date_ranges = []
                    
                    # 1. 检查是否需要补充历史数据（配置的开始日期早于数据库中最早的记录）
                    if configured_start_dt < db_earliest_date:
                        # 需要补充历史数据
                        history_end = db_earliest_date - timedelta(days=1)  # 避免重叠
                        logger.info(f"Need to import historical data from {configured_start_dt} to {history_end}")
                        date_ranges.append((configured_start_dt, history_end))
                    
                    # 2. 检查是否需要更新最新数据（数据库最新日期之后有新数据）
                    if db_latest_date < end_dt:
                        # 需要更新最新数据
                        latest_start = db_latest_date + timedelta(days=1)  # 避免重叠
                        logger.info(f"Need to import new data from {latest_start} to {end_dt}")
                        date_ranges.append((latest_start, end_dt))
                    
                    # 如果没有需要导入的区间，跳过导入
                    if not date_ranges:
                        logger.info(f"Skipping import: database already has complete data from {db_earliest_date} to {db_latest_date}")
                        self._update_import_log(
                            source=source, 
                            symbol=symbol, 
                            exchange=exchange, 
                            interval=interval, 
                            success=True, 
                            message=f"Skipped import: database already has complete data",
                            last_begin_date=db_earliest_date,
                            last_end_date=db_latest_date
                        )
                        return
                    
                    # 处理各个需要导入的日期区间
                    all_bars = []
                    for start_range, end_range in date_ranges:
                        # 导入数据
                        logger.info(f"Importing data for range: {start_range} to {end_range}")
                        success, message, bars = importer.import_data(
                            symbol=symbol,
                            exchange=exchange,
                            interval=interval,
                            start_date=start_range,
                            end_date=end_range,
                            **params  # 传递其他提取的参数
                        )
                        
                        if success and bars:
                            all_bars.extend(bars)
                            logger.info(f"Successfully imported {len(bars)} bars for range {start_range} to {end_range}")
                        else:
                            logger.warning(f"Failed to import data for range {start_range} to {end_range}: {message}")
                    
                    # 保存所有导入的数据
                    if all_bars:
                        logger.info(f"Saving {len(all_bars)} bars from {source} importer to database...")
                        count = self.db.save_bar_data(all_bars)
                        logger.info(f"Saved {count} bars for {symbol} from {source} importer.")
                        
                        # 找出日期范围（改为记录整个范围）
                        if all_bars:
                            earliest_date = min(bar.datetime for bar in all_bars)
                            latest_date = max(bar.datetime for bar in all_bars)
                            logger.info(f"Imported data range: {earliest_date} to {latest_date}")
                        else:
                            earliest_date = db_earliest_date
                            latest_date = db_latest_date
                        
                        # 更新消息以反映保存结果
                        message = f"Successfully imported and saved {count} bars from {source} data."
                        
                        # 导入成功，记录到导入日志
                        self._update_import_log(source, symbol, exchange, interval, True, message, earliest_date, latest_date)
                    else:
                        logger.warning(f"No new data was imported for {symbol}.")
                        self._update_import_log(source, symbol, exchange, interval, True, "No new data available", db_earliest_date, db_latest_date)
                        
                    return
                
                # 如果数据库中没有数据，使用配置的日期范围导入所有数据
                logger.info(f"No existing data found. Importing full range from {configured_start_dt} to {end_dt}")
                success, message, bars = importer.import_data(
                    symbol=symbol,
                    exchange=exchange,
                    interval=interval,
                    start_date=configured_start_dt,
                    end_date=end_dt,
                    **params  # 传递其他提取的参数
                )
                
                logger.info(f"Importer result for {symbol}: Success={success}, Msg='{message}', Bars obtained: {len(bars)}")
                
                # 处理数据保存
                if success and bars:
                    if not self.db:
                        message += " (Error: Cannot save bars, database connection not available.)"
                        logger.error(message)
                        self._update_import_log(source, symbol, exchange, interval, False, message, None, None)
                    else:
                        logger.info(f"Saving {len(bars)} bars from {source} importer to database...")
                        count = self.db.save_bar_data(bars)
                        logger.info(f"Saved {count} bars for {symbol} from {source} importer.")
                        
                        # 找出日期范围
                        earliest_date = None
                        latest_date = None
                        if bars:
                            earliest_date = min(bar.datetime for bar in bars)
                            latest_date = max(bar.datetime for bar in bars)
                            logger.info(f"Imported data range: {earliest_date} to {latest_date}")
                        
                        # 更新消息以反映保存结果
                        message = f"Successfully imported and saved {count} bars from {source} data."
                        
                        # 导入成功，记录到导入日志
                        self._update_import_log(source, symbol, exchange, interval, True, message, earliest_date, latest_date)
                elif success and not bars:
                    logger.warning(f"Import reported success but returned no bars for {symbol} (Message: '{message}'). Nothing to save.")
                    # 记录到导入日志（成功但无数据）
                    self._update_import_log(source, symbol, exchange, interval, True, message, None, None)
                elif not success:
                    logger.error(f"Import failed for {symbol} (Message: '{message}'). Nothing saved.")
                    # 记录到导入日志（失败）
                    self._update_import_log(source, symbol, exchange, interval, False, message, None, None)
                
            except ValueError as param_err:
                message = f"Parameter validation failed: {param_err}"
                logger.error(message)
                self._update_import_log(source, symbol, exchange, interval, False, message, None, None)
                return

        except Exception as e:
            error_message = f"Error during sync_target execution for {target}: {e}"
            logger.error(error_message, exc_info=True)
            
            # 尝试从异常中恢复交易所和周期信息（可能未初始化）
            try:
                exchange = Exchange(target.get("exchange", ""))
                interval = Interval(target.get("interval", ""))
            except:
                # 最差情况下使用字符串值
                exchange = target.get("exchange", "UNKNOWN")
                interval = target.get("interval", "UNKNOWN")
                
            # 记录异常到导入日志
            self._update_import_log(source, symbol, exchange, interval, False, error_message, None, None)
            # Re-raise the exception so asyncio.gather logs it properly
            raise e


async def run_initial_data_sync(db_instance: BaseDatabase):
    """初始化数据同步服务并运行同步
    
    Args:
        db_instance: 数据库实例
    """
    logger.info("Starting initial data sync process...")
    try:
        data_sync_service = DataSyncService(db_instance=db_instance)
        
        logger.info("DataSyncService initialized. Calling sync_all_targets...")
        await data_sync_service.sync_all_targets()
        logger.info("Initial data sync process finished.")

    except Exception as e:
        logger.error(f"Error during initial data sync execution: {e}", exc_info=True) 