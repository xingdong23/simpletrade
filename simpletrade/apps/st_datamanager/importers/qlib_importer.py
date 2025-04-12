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

# 添加vendors目录到Python路径
root_path = str(Path(__file__).parent.parent.parent.parent.parent)
vendors_path = os.path.join(root_path, 'vendors')
sys.path.append(vendors_path)

# 导入vnpy相关模块
from vnpy.vnpy.trader.object import BarData
from vnpy.vnpy.trader.constant import Exchange, Interval

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
            'change': 'change'  # 价格变化百分比
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
        # 在qlib中，股票代码通常存储在features目录下
        features_dir = os.path.join(qlib_dir, 'features')

        # 检查symbol是否直接存在
        symbol_path = os.path.join(features_dir, symbol)
        if os.path.exists(symbol_path):
            return symbol_path

        # 如果不存在，尝试转换格式（例如将600000转换为sh600000）
        if symbol.isdigit():
            # 尝试上海交易所格式
            sh_symbol = f'sh{symbol}'
            sh_path = os.path.join(features_dir, sh_symbol)
            if os.path.exists(sh_path):
                return sh_path

            # 尝试深圳交易所格式
            sz_symbol = f'sz{symbol}'
            sz_path = os.path.join(features_dir, sz_symbol)
            if os.path.exists(sz_path):
                return sz_path

        # 如果都不存在，返回原始路径
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
        return df

    def _read_symbol_data(self, qlib_dir: str, symbol: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """读取品种数据"""
        symbol_path = self._get_symbol_path(qlib_dir, symbol)
        if not os.path.exists(symbol_path):
            return pd.DataFrame()

        # 获取所有可用的数据文件
        data_files = []
        for root, _, files in os.walk(symbol_path):
            for file in files:
                if file.endswith('.day.bin'):  # 只读取日线数据
                    data_files.append(os.path.join(root, file))

        if not data_files:
            return pd.DataFrame()

        # 读取各个字段的数据
        field_dfs = {}
        for file_path in data_files:
            field_name = os.path.basename(file_path).split('.')[0]
            df = self._read_bin_file(file_path)
            if not df.empty:
                field_dfs[field_name] = df

        if not field_dfs:
            return pd.DataFrame()

        # 合并所有字段数据
        # 获取所有数据帧的索引并取并集
        all_indices = sorted(set().union(*[df.index for df in field_dfs.values()]))

        # 创建结果数据帧
        result_df = pd.DataFrame(index=all_indices)

        # 将每个字段的数据添加到结果数据帧
        for field_name, df in field_dfs.items():
            result_df[field_name] = df[field_name]

        # 将索引转换为日期
        # 获取交易日历
        calendar = self._read_calendar(qlib_dir)
        if calendar:
            # 创建日期映射字典，将数字索引映射到日期
            date_map = {i: pd.Timestamp(date) for i, date in enumerate(calendar)}

            # 将索引转换为日期
            result_df['datetime'] = result_df.index.map(lambda x: date_map.get(x, pd.NaT))

            # 删除无效日期
            result_df = result_df.dropna(subset=['datetime'])

            # 过滤日期范围
            if start_date:
                result_df = result_df[result_df['datetime'] >= start_date]
            if end_date:
                result_df = result_df[result_df['datetime'] <= end_date]

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

            # 处理股票代码格式
            # 如果是纯数字代码，根据交易所添加前缀
            original_symbol = symbol
            if symbol.isdigit():
                if exchange.value == "SSE":
                    symbol = f"sh{symbol}"
                elif exchange.value == "SZSE":
                    symbol = f"sz{symbol}"

            # 读取品种数据
            df = self._read_symbol_data(qlib_dir, symbol, start_date, end_date)
            if df.empty:
                return False, f"未找到品种数据: {symbol}", []

            # 转换为BarData列表
            bars = []
            for _, row in df.iterrows():
                # 创建BarData对象
                bar = BarData(
                    symbol=original_symbol,  # 使用原始代码
                    exchange=exchange,
                    datetime=row['datetime'],
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
                return False, f"未能导入任何数据: {symbol}", []

            # 按日期排序
            bars.sort(key=lambda x: x.datetime)

            return True, f"成功导入 {len(bars)} 条K线数据", bars

        except Exception as e:
            import traceback
            error_msg = f"导入Qlib数据时发生错误: {str(e)}\n{traceback.format_exc()}"
            return False, error_msg, []
