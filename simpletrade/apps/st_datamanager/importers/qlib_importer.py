"""
Qlib数据格式导入器

用于将qlib格式的数据导入到SimpleTrade系统中。
"""

import os
import sys
import struct
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import logging

# 添加vendors目录到Python路径
root_path = str(Path(__file__).parent.parent.parent.parent.parent)
vendors_path = os.path.join(root_path, 'vendors')
sys.path.append(vendors_path)

# 导入vnpy相关模块
from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval

logger = logging.getLogger(__name__) # Setup logger for the importer module

class QlibDataImporter:
    """Qlib数据格式导入器"""

    def __init__(self):
        """初始化"""
        # 定义qlib数据字段映射
        self.qlib_fields = {
            'open': 'open_price',
            'high': 'high_price',
            'low': 'low_price',
            'close': 'close_price',
            'volume': 'volume',
            'factor': 'open_interest',  # 使用factor作为open_interest
            # 'change': 'change'  # 移除：价格变化百分比，VnPy BarData无此字段
        }

        # 支持的周期映射
        self.interval_map = {
            Interval.DAILY: 'day',
            Interval.MINUTE: 'min'
        }

    def _read_calendar(self, qlib_dir: str) -> List[str]:
        """读取交易日历"""
        calendar_path = os.path.join(qlib_dir, 'calendars', 'day.txt')
        if not os.path.exists(calendar_path):
            return []

        with open(calendar_path, 'r') as f:
            calendar = [line.strip() for line in f if line.strip()]

        return calendar

    def _get_symbol_path(self, qlib_dir: str, symbol: str) -> str:
        """获取品种数据路径"""
        features_dir = os.path.join(qlib_dir, 'features')
        logger.warning(f"_get_symbol_path: Base features directory: {features_dir}")

        # 检查symbol是否直接存在
        symbol_path = os.path.join(features_dir, symbol)
        logger.warning(f"_get_symbol_path: Checking direct path: {symbol_path}")
        exists = os.path.exists(symbol_path)
        logger.warning(f"_get_symbol_path: Direct path exists: {exists}")
        if exists:
            return symbol_path

        # 如果不存在，尝试转换格式（例如将600000转换为sh600000）
        if symbol.isdigit(): # This part only relevant for numeric symbols (A-shares)
            logger.warning(f"_get_symbol_path: Symbol '{symbol}' is numeric, attempting prefix conversion.")
            # 尝试上海交易所格式
            sh_symbol = f'sh{symbol}'
            sh_path = os.path.join(features_dir, sh_symbol)
            logger.warning(f"_get_symbol_path: Checking SH path: {sh_path}")
            sh_exists = os.path.exists(sh_path)
            logger.warning(f"_get_symbol_path: SH path exists: {sh_exists}")
            if sh_exists:
                return sh_path

            # 尝试深圳交易所格式
            sz_symbol = f'sz{symbol}'
            sz_path = os.path.join(features_dir, sz_symbol)
            logger.warning(f"_get_symbol_path: Checking SZ path: {sz_path}")
            sz_exists = os.path.exists(sz_path)
            logger.warning(f"_get_symbol_path: SZ path exists: {sz_exists}")
            if sz_exists:
                return sz_path

        # 如果都不存在或不是数字代码, 返回原始尝试的路径 (即使它可能不存在)
        logger.warning(f"_get_symbol_path: No conversion applied or successful, returning original path attempt: {symbol_path}")
        return symbol_path

    def _read_bin_file(self, file_path: str) -> pd.DataFrame:
        """读取qlib二进制文件

        qlib的数据格式是一种特殊的二进制格式，每个文件对应一个字段（如open, close, high, low, volume等）
        文件格式为：开始索引（4字节浮点数）+ 一系列数据（4字节浮点数）
        """
        if not os.path.exists(file_path):
            return pd.DataFrame()

        # 获取字段名称
        field_name = os.path.basename(file_path).split('.')[0]

        # 读取二进制文件
        with open(file_path, 'rb') as f:
            # 读取文件头（第一个浮点数是开始索引）
            start_index = struct.unpack('f', f.read(4))[0]

            # 读取所有数据
            data = np.fromfile(f, dtype='<f')

            # 创建日期索引
            indices = np.arange(int(start_index), int(start_index) + len(data))

        # 创建DataFrame
        df = pd.DataFrame({field_name: data}, index=indices)
        # Add logging for shape
        logger.warning(f"_read_bin_file: Read {field_name} from {file_path}. Shape: {df.shape}") 
        return df

    def _read_symbol_data(self, qlib_dir: str, symbol: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """读取品种数据"""
        symbol_path = self._get_symbol_path(qlib_dir, symbol)
        logger.warning(f"_read_symbol_data: Attempting to read data for symbol '{symbol}' from path: {symbol_path}")
        exists = os.path.exists(symbol_path)
        logger.warning(f"_read_symbol_data: Path exists: {exists}")
        if not exists:
            logger.warning(f"_read_symbol_data: Symbol path does not exist: {symbol_path}")
            return pd.DataFrame()

        # 获取所有可用的数据文件
        data_files = []
        try:
            for root, _, files in os.walk(symbol_path):
                for file in files:
                    if file.endswith('.day.bin'):
                        data_files.append(os.path.join(root, file))
            logger.warning(f"_read_symbol_data: Found .day.bin files: {data_files}")
        except Exception as walk_e:
            logger.error(f"_read_symbol_data: Error during os.walk for {symbol_path}: {walk_e}")
            return pd.DataFrame()

        if not data_files:
            logger.warning(f"_read_symbol_data: No .day.bin files found in {symbol_path}")
            return pd.DataFrame()

        # 读取各个字段的数据
        field_dfs = {}
        for file_path in data_files:
            field_name = os.path.basename(file_path).split('.')[0]
            try:
                 df_field = self._read_bin_file(file_path)
                 if not df_field.empty:
                     field_dfs[field_name] = df_field
            except Exception as read_bin_e:
                 logger.error(f"_read_symbol_data: Error reading bin file {file_path}: {read_bin_e}")

        if not field_dfs:
            logger.warning("_read_symbol_data: No data loaded from any .bin files.")
            return pd.DataFrame()

        # 合并所有字段数据
        try:
            all_indices = sorted(set().union(*[df.index for df in field_dfs.values()]))
            result_df = pd.DataFrame(index=all_indices)
            for field_name, df in field_dfs.items():
                result_df[field_name] = df[field_name]
            logger.warning(f"_read_symbol_data: Merged DataFrame shape before datetime conversion: {result_df.shape}")
        except Exception as merge_e:
            logger.error(f"_read_symbol_data: Error merging field DataFrames: {merge_e}")
            return pd.DataFrame()

        # 将索引转换为日期
        calendar_path = os.path.join(qlib_dir, 'calendars', 'day.txt') # Define calendar path here
        logger.warning(f"_read_symbol_data: Checking for calendar file at: {calendar_path}")
        calendar = self._read_calendar(qlib_dir)
        if calendar:
            logger.warning(f"_read_symbol_data: Calendar file found. Length: {len(calendar)}")
            try:
                date_map = {i: pd.Timestamp(date) for i, date in enumerate(calendar)}
                result_df['datetime'] = result_df.index.map(lambda x: date_map.get(x, pd.NaT))
                logger.warning(f"_read_symbol_data: DataFrame shape after index mapping: {result_df.shape}")
                
                initial_rows = len(result_df)
                result_df = result_df.dropna(subset=['datetime']) # Drop rows where index couldn't be mapped
                dropped_rows = initial_rows - len(result_df)
                logger.warning(f"_read_symbol_data: DataFrame shape after dropna('datetime'): {result_df.shape}. Dropped {dropped_rows} rows.")

                # --- Localize datetime to US/Eastern --- 
                if 'datetime' in result_df.columns and not result_df.empty:
                    try:
                        # Assuming US stock data is in US/Eastern timezone
                        target_tz = 'US/Eastern' 
                        result_df['datetime'] = result_df['datetime'].dt.tz_localize(target_tz, ambiguous='infer')
                        logger.warning(f"_read_symbol_data: Localized datetime column to {target_tz}. Example: {result_df['datetime'].iloc[0] if not result_df.empty else 'N/A'}")
                    except Exception as tz_localize_e:
                        logger.error(f"_read_symbol_data: Failed to localize datetime column: {tz_localize_e}")
                        # Decide if we should return empty df or continue with naive
                        # For now, let's log the error and continue, VnPy might handle some cases
                        # return pd.DataFrame() 
                # --- End Localization ---
                
                # 过滤日期范围
                localized_start_date = None
                localized_end_date = None
                target_tz = 'US/Eastern' # Define target_tz again or ensure it's in scope
                
                try:
                    if start_date:
                        # Convert to Timestamp and localize if naive
                        ts_start = pd.Timestamp(start_date)
                        if ts_start.tzinfo is None or ts_start.tzinfo.utcoffset(ts_start) is None:
                            localized_start_date = ts_start.tz_localize(target_tz)
                        else:
                            localized_start_date = ts_start.tz_convert(target_tz) # Convert if already aware
                        logger.warning(f"_read_symbol_data: Localized start_date for filtering: {localized_start_date}")

                    if end_date:
                        ts_end = pd.Timestamp(end_date)
                        if ts_end.tzinfo is None or ts_end.tzinfo.utcoffset(ts_end) is None:
                            localized_end_date = ts_end.tz_localize(target_tz)
                        else:
                            localized_end_date = ts_end.tz_convert(target_tz) # Convert if already aware
                        logger.warning(f"_read_symbol_data: Localized end_date for filtering: {localized_end_date}")

                except Exception as filter_localize_e:
                     logger.error(f"_read_symbol_data: Error localizing start/end date for filtering: {filter_localize_e}")
                     # Decide how to handle: maybe return empty df?
                     return pd.DataFrame()
                 
                initial_rows_before_filter = len(result_df)
                if localized_start_date:
                    result_df = result_df[result_df['datetime'] >= localized_start_date]
                if localized_end_date:
                    result_df = result_df[result_df['datetime'] <= localized_end_date]
                filtered_rows = initial_rows_before_filter - len(result_df)
                logger.warning(f"_read_symbol_data: DataFrame shape after date filtering ({localized_start_date} to {localized_end_date}): {result_df.shape}. Filtered out {filtered_rows} rows.")
            except Exception as convert_e:
                logger.error(f"_read_symbol_data: Error during datetime conversion or filtering: {convert_e}")
                return pd.DataFrame()
        else:
            logger.error(f"_read_symbol_data: Calendar file not found at {calendar_path}. Cannot convert index to datetime.")
            return pd.DataFrame() # Return empty if no calendar

        # Final check before returning
        if result_df.empty:
            logger.warning("_read_symbol_data: Returning empty DataFrame after all processing.")
        else:
            logger.warning(f"_read_symbol_data: Returning DataFrame with shape: {result_df.shape}")
            
        return result_df

    def import_data(
        self,
        qlib_dir: str,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[bool, str, List[BarData]]:
        """
        从qlib格式数据导入K线数据

        参数:
            qlib_dir (str): qlib数据目录路径
            symbol (str): 交易品种代码
            exchange (Exchange): 交易所
            interval (Interval): K线周期
            start_date (datetime, optional): 开始日期，默认为None，表示从最早的数据开始
            end_date (datetime, optional): 结束日期，默认为None，表示到最新的数据结束

        返回:
            Tuple[bool, str, List[BarData]]: (成功标志, 消息, K线数据列表)
        """
        # 检查目录是否存在
        if not os.path.exists(qlib_dir):
            return False, f"Qlib数据目录不存在: {qlib_dir}", []

        # 检查周期是否支持
        if interval not in self.interval_map:
            return False, f"不支持的K线周期: {interval}", []

        try:
            # 读取交易日历
            calendar = self._read_calendar(qlib_dir)
            if not calendar:
                return False, "无法读取交易日历", []

            # Store original symbol for BarData creation
            original_symbol = symbol
            # Determine the symbol format used for searching in Qlib filesystem
            search_symbol = symbol

            if exchange in [Exchange.NASDAQ, Exchange.NYSE, Exchange.AMEX]:
                search_symbol = symbol.lower()
                logger.warning(f"Using lowercase symbol '{search_symbol}' for searching US stock data.")
            elif exchange in [Exchange.SSE, Exchange.SZSE, Exchange.BSE]:
                # Apply sh/sz prefix if symbol is numeric (consistent with _get_symbol_path logic?)
                # Note: _get_symbol_path also attempts this, maybe centralize?
                # For now, let's keep the logic here for clarity before calling read_symbol_data
                if symbol.isdigit():
                    if exchange == Exchange.SSE:
                         search_symbol = f"sh{symbol}"
                    elif exchange == Exchange.SZSE:
                         search_symbol = f"sz{symbol}"
                    # Add logic for BSE or other prefixes if needed
                    logger.warning(f"Using prefixed symbol '{search_symbol}' for searching China A-share data.")
            # Add elif for other exchange-specific symbol formats if needed

            # 读取品种数据 using the processed search_symbol
            df = self._read_symbol_data(qlib_dir, search_symbol, start_date, end_date)
            if df.empty:
                # Use search_symbol in the error message to show what was looked for
                return False, f"未找到品种数据: {search_symbol} (searched)", []

            # 转换为BarData列表
            bars = []
            for _, row in df.iterrows():
                # 创建BarData对象 - Use original_symbol here!
                bar = BarData(
                    symbol=original_symbol,
                    exchange=exchange,
                    datetime=row['datetime'].to_pydatetime(),
                    interval=interval,
                    gateway_name="QLIB"
                )

                # 设置价格和成交量数据
                for qlib_field, vnpy_field in self.qlib_fields.items():
                    if qlib_field in row:
                        setattr(bar, vnpy_field, float(row[qlib_field]))
                    elif qlib_field.lower() in row:  # 尝试小写字段名
                        setattr(bar, vnpy_field, float(row[qlib_field.lower()]))

                # 确保必要字段都有值
                required_fields = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
                if all(hasattr(bar, field) and getattr(bar, field) is not None for field in required_fields):
                    bars.append(bar)

            # 检查是否成功导入数据
            if not bars:
                 # Consider if df was not empty but no valid bars were created
                 return False, f"未能将Qlib数据转换为有效BarData: {original_symbol}", []

            logger.info(f"Successfully imported {len(bars)} bars for {original_symbol} from Qlib.")
            return True, f"成功导入 {len(bars)} 条数据", bars

        except FileNotFoundError as e:
            logger.error(f"Error importing Qlib data for {original_symbol}: {e}")
            return False, f"导入时文件未找到: {e}", []
        except Exception as e:
            logger.error(f"Unexpected error importing Qlib data for {original_symbol}: {e}\\n{traceback.format_exc()}")
            return False, f"导入时发生意外错误: {e}", []
