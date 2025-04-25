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

# 导入基类
from .base_importer import BaseDataImporter

logger = logging.getLogger(__name__) # Setup logger for the importer module

class QlibDataImporter(BaseDataImporter):
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

    def extract_and_validate_params(self, target_config: Dict[str, Any]) -> Dict[str, Any]:
        """从目标配置中提取并验证Qlib导入器参数
        
        Args:
            target_config: 完整的目标配置字典
            
        Returns:
            处理后的参数字典，可直接用于import_data方法
            
        Raises:
            ValueError: 当必要参数缺失或无效时
        """
        # 首先获取基类提取的基本参数
        params = super().extract_and_validate_params(target_config)
        
        # 提取并验证Qlib特有参数：market
        market = target_config.get("market")
        if not market:
            raise ValueError("Missing required parameter for Qlib: market ('cn' or 'us')")
        
        if market not in ["cn", "us"]:
            raise ValueError(f"Invalid market identifier for Qlib: '{market}'. Expected 'cn' or 'us'.")
        
        params["market"] = market
        
        # 处理qlib_dir参数
        qlib_dir = target_config.get("qlib_dir")
        if not qlib_dir:
            # 从配置中获取默认路径
            from simpletrade.config.settings import QLIB_DATA_PATH
            if not QLIB_DATA_PATH:
                raise ValueError("QLIB_DATA_PATH not configured. Set SIMPLETRADE_QLIB_DATA_PATH environment variable.")
            
            if not os.path.exists(QLIB_DATA_PATH):
                raise ValueError(f"QLIB_DATA_PATH ('{QLIB_DATA_PATH}') does not exist.")
                
            qlib_dir = QLIB_DATA_PATH
            logger.debug(f"Using default Qlib data path from config: {QLIB_DATA_PATH}")
        
        params["qlib_dir"] = qlib_dir
        
        return params

    def _get_market_subdir(self, market: str) -> str:
        """根据市场标识获取子目录名"""
        # 简单映射，可以根据需要扩展
        if market == "cn":
            return "cn_data"
        elif market == "us":
            return "us_data"
        else:
            # 如果市场未知或不支持，可以选择抛出错误或返回空字符串/None
            logger.error(f"Unsupported market identifier: '{market}'. Expected 'cn' or 'us'.")
            # raise ValueError(f"Unsupported market identifier: {market}")
            return "" # 返回空字符串，让后续路径检查失败

    def _read_calendar(self, qlib_dir: str, market: str) -> List[str]:
        """读取交易日历 (根据市场)"""
        market_subdir = self._get_market_subdir(market)
        if not market_subdir:
            return [] # 如果市场无效，无法找到日历
            
        calendar_path = os.path.join(qlib_dir, market_subdir, 'calendars', 'day.txt')
        logger.debug(f"_read_calendar: Attempting to read calendar from: {calendar_path}")
        if not os.path.exists(calendar_path):
            logger.error(f"Calendar file not found at {calendar_path}")
            return []

        try:
            with open(calendar_path, 'r') as f:
                calendar = [line.strip() for line in f if line.strip()]
            logger.debug(f"_read_calendar: Successfully read calendar with {len(calendar)} entries.")
            return calendar
        except Exception as e:
            logger.error(f"Error reading calendar file {calendar_path}: {e}")
            return []

    def _get_symbol_path(self, qlib_dir: str, market: str, symbol: str) -> str:
        """获取品种数据路径 (根据市场)"""
        market_subdir = self._get_market_subdir(market)
        if not market_subdir:
            return "" # 如果市场无效，无法找到路径

        # 基础 features 目录现在包含市场子目录
        features_dir = os.path.join(qlib_dir, market_subdir, 'features')
        logger.debug(f"_get_symbol_path: Base features directory for market '{market}': {features_dir}")

        # 检查symbol是否直接存在 (例如 AAPL)
        symbol_path = os.path.join(features_dir, symbol)
        logger.debug(f"_get_symbol_path: Checking direct path: {symbol_path}")
        if os.path.exists(symbol_path):
            return symbol_path

        # 如果市场是中国市场 (cn) 且 symbol 是数字，尝试添加 sh/sz 前缀
        if market == "cn" and symbol.isdigit():
            logger.debug(f"_get_symbol_path: CN market and numeric symbol '{symbol}', attempting prefix conversion.")
            # 尝试上海交易所格式
            sh_symbol = f'sh{symbol}'
            sh_path = os.path.join(features_dir, sh_symbol)
            logger.debug(f"_get_symbol_path: Checking SH path: {sh_path}")
            if os.path.exists(sh_path):
                return sh_path

            # 尝试深圳交易所格式
            sz_symbol = f'sz{symbol}'
            sz_path = os.path.join(features_dir, sz_symbol)
            logger.debug(f"_get_symbol_path: Checking SZ path: {sz_path}")
            if os.path.exists(sz_path):
                return sz_path

        # 如果各种尝试都失败，返回最初尝试的直接路径（即使它不存在）
        logger.warning(f"_get_symbol_path: Symbol path not found after checks for market '{market}'. Returning initial attempt: {symbol_path}")
        return symbol_path # 返回这个不存在的路径，让后续逻辑处理

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
        logger.debug(f"_read_bin_file: Read {field_name} from {file_path}. Shape: {df.shape}") 
        return df

    def _read_symbol_data(self, qlib_dir: str, market: str, symbol: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """读取品种数据 (根据市场)"""
        symbol_path = self._get_symbol_path(qlib_dir, market, symbol)
        logger.info(f"_read_symbol_data: Attempting to read data for symbol '{symbol}' (market: {market}) from path: {symbol_path}")
        if not symbol_path or not os.path.exists(symbol_path): # 检查路径有效性
            logger.error(f"_read_symbol_data: Symbol path is invalid or does not exist: '{symbol_path}'")
            return pd.DataFrame()

        # 获取所有可用的数据文件
        data_files = []
        try:
            # 假设数据文件直接在 symbol_path 下，不包含 day/min 子目录
            for file in os.listdir(symbol_path):
                 # 根据文件扩展名判断周期 (这里简单处理，只找 .bin)
                 # 注意：这可能需要根据 qlib 的实际存储方式调整
                 # 如果 qlib 把日线和分钟线放不同子目录，这里需要修改
                 if file.endswith('.bin'): # 假设直接是 .bin 文件
                    data_files.append(os.path.join(symbol_path, file))
            logger.debug(f"_read_symbol_data: Found .bin files in {symbol_path}: {data_files}")
        except Exception as list_e:
            logger.error(f"_read_symbol_data: Error listing files in {symbol_path}: {list_e}")
            return pd.DataFrame()

        if not data_files:
            logger.warning(f"_read_symbol_data: No .bin files found in {symbol_path}")
            return pd.DataFrame()

        # 读取各个字段的数据
        field_dfs = {}
        for file_path in data_files:
            field_name = os.path.basename(file_path).split('.')[0]
            # Check if field is relevant (e.g., open, high, low, close, volume, factor)
            if field_name in self.qlib_fields:
                try:
                     df_field = self._read_bin_file(file_path)
                     if not df_field.empty:
                         field_dfs[field_name] = df_field
                except Exception as read_bin_e:
                     logger.error(f"_read_symbol_data: Error reading bin file {file_path}: {read_bin_e}")
            else:
                logger.debug(f"_read_symbol_data: Skipping irrelevant file: {file_path}")

        if not field_dfs:
            logger.warning("_read_symbol_data: No relevant data loaded from any .bin files.")
            return pd.DataFrame()
            
        # 合并所有字段数据
        try:
            all_indices = sorted(set().union(*[df.index for df in field_dfs.values()]))
            result_df = pd.DataFrame(index=all_indices)
            for field_name, df in field_dfs.items():
                result_df[field_name] = df[field_name]
            logger.debug(f"_read_symbol_data: Merged DataFrame shape before datetime conversion: {result_df.shape}")
        except Exception as merge_e:
            logger.error(f"_read_symbol_data: Error merging field DataFrames: {merge_e}")
            return pd.DataFrame()

        # 将索引转换为日期
        calendar = self._read_calendar(qlib_dir, market)
        if not calendar:
            logger.error(f"_read_symbol_data: Cannot convert index to datetime, calendar for market '{market}' not found or empty.")
            return pd.DataFrame()
            
        logger.debug(f"_read_symbol_data: Using calendar for market '{market}' with {len(calendar)} entries.")
        try:
            date_map = {i: pd.Timestamp(date) for i, date in enumerate(calendar)}
            result_df['datetime'] = result_df.index.map(lambda x: date_map.get(x, pd.NaT))
            logger.debug(f"_read_symbol_data: DataFrame shape after index mapping: {result_df.shape}")
            
            initial_rows = len(result_df)
            result_df = result_df.dropna(subset=['datetime'])
            dropped_rows = initial_rows - len(result_df)
            if dropped_rows > 0:
                logger.warning(f"_read_symbol_data: Dropped {dropped_rows} rows due to invalid datetime mapping.")
            logger.debug(f"_read_symbol_data: DataFrame shape after dropna('datetime'): {result_df.shape}")

            # --- Localize datetime --- 
            # 决定时区：US 市场用 US/Eastern, CN 市场用 Asia/Shanghai
            target_tz = 'Asia/Shanghai' if market == 'cn' else 'US/Eastern'
            logger.debug(f"_read_symbol_data: Attempting to localize datetime to {target_tz}")
            if 'datetime' in result_df.columns and not result_df.empty:
                try:
                    result_df['datetime'] = result_df['datetime'].dt.tz_localize(target_tz, ambiguous='infer')
                    logger.debug(f"_read_symbol_data: Localized datetime column to {target_tz}. Example: {result_df['datetime'].iloc[0] if not result_df.empty else 'N/A'}")
                except Exception as tz_localize_e:
                    logger.error(f"_read_symbol_data: Failed to localize datetime column: {tz_localize_e}")
                    # Decide action: continue with naive or return empty
            
            # 过滤日期范围 (使用本地化后的日期)
            localized_start_date = None
            localized_end_date = None
            try:
                if start_date:
                    ts_start = pd.Timestamp(start_date)
                    localized_start_date = ts_start.tz_localize(target_tz) if ts_start.tzinfo is None else ts_start.tz_convert(target_tz)
                    logger.debug(f"_read_symbol_data: Localized start_date for filtering: {localized_start_date}")
                if end_date:
                    ts_end = pd.Timestamp(end_date)
                    localized_end_date = ts_end.tz_localize(target_tz) if ts_end.tzinfo is None else ts_end.tz_convert(target_tz)
                    logger.debug(f"_read_symbol_data: Localized end_date for filtering: {localized_end_date}")
            except Exception as filter_localize_e:
                 logger.error(f"_read_symbol_data: Error localizing start/end date for filtering: {filter_localize_e}")
                 return pd.DataFrame()
             
            initial_rows_before_filter = len(result_df)
            if localized_start_date: result_df = result_df[result_df['datetime'] >= localized_start_date]
            if localized_end_date: result_df = result_df[result_df['datetime'] <= localized_end_date]
            filtered_rows = initial_rows_before_filter - len(result_df)
            if filtered_rows > 0: logger.debug(f"_read_symbol_data: Filtered out {filtered_rows} rows based on date range.")
            logger.info(f"_read_symbol_data: Final DataFrame shape after date filtering: {result_df.shape}")

        except Exception as convert_e:
            logger.error(f"_read_symbol_data: Error during datetime conversion or filtering: {convert_e}", exc_info=True)
            return pd.DataFrame()

        return result_df

    def import_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs
    ) -> Tuple[bool, str, List[BarData]]:
        """导入指定品种、周期的数据
        
        Args:
            symbol: 品种代码
            exchange: 交易所
            interval: K线周期
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 额外参数，包括：
                qlib_dir: Qlib数据根目录
                market: 市场标识 ('cn' 或 'us')
                
        Returns:
            Tuple[bool, str, List[BarData]]: (是否成功, 消息, BarData列表)
        """
        # 从 kwargs 中获取 qlib 特有参数
        qlib_dir = kwargs.get("qlib_dir")
        market = kwargs.get("market")
        
        if not qlib_dir:
            return False, "Missing required parameter: qlib_dir", []
            
        if not market:
            return False, "Missing required parameter: market ('cn' or 'us')", []
            
        # 检查 interval 是否支持 (当前实现主要针对日线 .day.bin)
        if interval != Interval.DAILY:
             msg = f"Unsupported interval for Qlib importer: {interval}. Currently only supports Daily."
             logger.warning(msg)
             return False, msg, []

        # 检查市场标识是否有效
        if market not in ["cn", "us"]:
            msg = f"Invalid market identifier: '{market}'. Expected 'cn' or 'us'."
            logger.error(msg)
            return False, msg, []

        logger.info(f"Starting Qlib import: Market={market}, Symbol={symbol}, Interval={interval}, Exchange={exchange} from {qlib_dir}")

        # 读取数据到 DataFrame
        try:
            data_df = self._read_symbol_data(qlib_dir, market, symbol, start_date, end_date)
        except Exception as e:
            msg = f"Error reading symbol data for {symbol} (market {market}): {e}"
            logger.error(msg, exc_info=True)
            return False, msg, []

        if data_df.empty:
            msg = f"No data found or loaded for {symbol} (market {market}) in the specified period or path."
            logger.warning(msg)
            return True, msg, [] # 认为成功，但没有数据

        # 转换 DataFrame 为 BarData 列表
        bars: List[BarData] = []
        try:
            for _, row in data_df.iterrows():
                # 获取必要字段，使用 .get 提供默认值以防字段缺失
                dt = row.get('datetime')
                open_price = float(row.get('open', 0.0) or 0.0)
                high_price = float(row.get('high', 0.0) or 0.0)
                low_price = float(row.get('low', 0.0) or 0.0)
                close_price = float(row.get('close', 0.0) or 0.0)
                volume = float(row.get('volume', 0.0) or 0.0)
                open_interest = float(row.get('factor', 0.0) or 0.0) # 从 factor 映射

                # 检查数据有效性 (例如 datetime 是否存在)
                if pd.isna(dt):
                    logger.warning(f"Skipping row due to missing datetime: {row.to_dict()}")
                    continue
                if high_price < low_price or any(p < 0 for p in [open_price, high_price, low_price, close_price]) or volume < 0:
                    logger.warning(f"Skipping row due to invalid price/volume data: {row.to_dict()}")
                    continue
                    
                # 转换时区到 UTC (因为 VnPy 内部通常期望 UTC)
                # 之前已经本地化到市场时区，现在转换为 UTC
                try:
                     dt_utc = dt.tz_convert('UTC')
                     # Convert to Python datetime
                     dt_py = dt_utc.to_pydatetime()
                except Exception as utc_convert_e:
                     logger.error(f"Failed to convert datetime {dt} to UTC or Python datetime: {utc_convert_e}")
                     continue # Skip if conversion fails

                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    datetime=dt_py,
                    interval=interval,
                    volume=volume,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    open_interest=open_interest,
                    gateway_name="QIMPORT" # 标记数据来源
                )
                bars.append(bar)

            msg = f"Successfully converted {len(bars)} bars from DataFrame for {symbol} (market {market})."
            logger.info(msg)
            return True, msg, bars

        except Exception as convert_e:
            msg = f"Error converting DataFrame to BarData for {symbol} (market {market}): {convert_e}"
            logger.error(msg, exc_info=True)
            return False, msg, []
