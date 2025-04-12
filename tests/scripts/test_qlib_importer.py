"""
测试Qlib数据导入器

用于测试从qlib格式数据导入到SimpleTrade系统的功能。
"""

import os
import sys
import struct
import pandas as pd
from datetime import datetime
from pathlib import Path
from enum import Enum

# 添加项目根目录到Python路径
root_path = str(Path(__file__).parent.parent.parent)
sys.path.append(root_path)

# 定义简单的枚举类替代vnpy的Exchange和Interval
class Exchange(Enum):
    SSE = "SSE"  # 上海证券交易所
    SZSE = "SZSE"  # 深圳证券交易所

class Interval(Enum):
    MINUTE = "1m"  # 1分钟
    HOUR = "1h"  # 1小时
    DAILY = "d"  # 日线
    WEEKLY = "w"  # 周线
from vnpy.trader.object import BarData

# 定义简化版的QlibDataImporter类
class QlibDataImporter:
    """简化版Qlib数据格式导入器"""

    def __init__(self):
        """初始化"""
        # 定义qlib数据字段映射
        self.qlib_fields = {
            'open': 'open_price',
            'high': 'high_price',
            'low': 'low_price',
            'close': 'close_price',
            'volume': 'volume',
            'factor': 'open_interest'  # 使用factor作为open_interest
        }

        # 支持的周期映射
        self.interval_map = {
            Interval.DAILY: 'day',
            Interval.MINUTE: 'min'
        }

    def _read_calendar(self, qlib_dir: str) -> list:
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
        """读取qlib二进制文件"""
        if not os.path.exists(file_path):
            return pd.DataFrame()

        # 获取字段名称
        field_name = os.path.basename(file_path).split('.')[0]

        # 读取二进制文件
        with open(file_path, 'rb') as f:
            # 读取文件头
            header_size = struct.unpack('i', f.read(4))[0]
            header = f.read(header_size).decode('utf-8')

            # 解析文件头
            # 在qlib中，文件头通常是空的，我们使用文件名作为字段名

            # 读取数据
            data = []
            while True:
                # 每条记录的格式：时间戳(int) + 数据(float)
                record = f.read(8)  # 4字节时间戳 + 4字节浮点数
                if not record or len(record) != 8:
                    break

                timestamp, value = struct.unpack('if', record)

                # 转换时间戳为日期
                date = datetime.fromtimestamp(timestamp)
                data.append([date, value])

        # 创建DataFrame
        df = pd.DataFrame(data, columns=['datetime', field_name])
        return df

    def _read_symbol_data(self, qlib_dir: str, symbol: str, start_date=None, end_date=None) -> pd.DataFrame:
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
            df = self._read_bin_file(file_path)
            if not df.empty:
                field_name = os.path.basename(file_path).split('.')[0]
                field_dfs[field_name] = df

        if not field_dfs:
            return pd.DataFrame()

        # 使用datetime作为基准合并所有字段
        # 首先获取一个基准DataFrame
        base_field = list(field_dfs.keys())[0]
        result_df = field_dfs[base_field][['datetime']].copy()

        # 合并所有字段
        for field_name, field_df in field_dfs.items():
            result_df = pd.merge(result_df, field_df, on='datetime', how='left')

        # 按日期排序
        result_df.sort_values('datetime', inplace=True)

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
        start_date=None,
        end_date=None,
    ):
        """
        从qlib格式数据导入K线数据
        """
        # 检查目录是否存在
        if not os.path.exists(qlib_dir):
            return False, f"Qlib数据目录不存在: {qlib_dir}", []

        # 检查周期是否支持
        if interval not in self.interval_map:
            return False, f"不支持的K线周期: {interval.value}", []

        try:
            # 读取交易日历
            calendar = self._read_calendar(qlib_dir)
            if not calendar:
                return False, "无法读取交易日历", []

            # 读取品种数据
            df = self._read_symbol_data(qlib_dir, symbol, start_date, end_date)
            if df.empty:
                return False, f"未找到品种数据: {symbol}", []

            # 转换为BarData列表
            bars = []
            for _, row in df.iterrows():
                # 创建BarData对象
                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    datetime=row['datetime'],
                    interval=interval,
                    gateway_name="QLIB"
                )

                # 设置价格和成交量数据
                for qlib_field, vnpy_field in self.qlib_fields.items():
                    if qlib_field in row:
                        setattr(bar, vnpy_field, row[qlib_field])

                bars.append(bar)

            # 检查是否成功导入数据
            if not bars:
                return False, f"未能导入任何数据: {symbol}", []

            return True, f"成功导入 {len(bars)} 条K线数据", bars

        except Exception as e:
            import traceback
            error_msg = f"导入Qlib数据时发生错误: {str(e)}\n{traceback.format_exc()}"
            return False, error_msg, []

def test_qlib_importer():
    """测试Qlib数据导入器"""
    print("开始测试Qlib数据导入器...")

    # 设置qlib数据目录
    qlib_dir = "/Users/chengzheng/.qlib/qlib_data/cn_data"

    # 创建导入器
    importer = QlibDataImporter()

    # 测试读取日历
    calendar = importer._read_calendar(qlib_dir)
    print(f"读取到 {len(calendar)} 个交易日")
    if calendar:
        print(f"第一个交易日: {calendar[0]}")
        print(f"最后一个交易日: {calendar[-1]}")

    # 测试获取品种路径
    test_symbols = ["600000", "000001", "sh600000", "sz000001"]
    for symbol in test_symbols:
        symbol_path = importer._get_symbol_path(qlib_dir, symbol)
        exists = os.path.exists(symbol_path)
        print(f"品种 {symbol} 路径: {symbol_path}, 存在: {exists}")

    # 测试导入数据
    test_cases = [
        {"symbol": "600000", "exchange": Exchange.SSE, "interval": Interval.DAILY},
        {"symbol": "000001", "exchange": Exchange.SZSE, "interval": Interval.DAILY},
        {"symbol": "sh600000", "exchange": Exchange.SSE, "interval": Interval.DAILY},
        {"symbol": "sz000001", "exchange": Exchange.SZSE, "interval": Interval.DAILY}
    ]

    for case in test_cases:
        symbol = case["symbol"]
        exchange = case["exchange"]
        interval = case["interval"]

        print(f"\n测试导入 {symbol}.{exchange.value} {interval.value} 数据...")

        # 设置日期范围（最近一年）
        end_date = datetime.now()
        start_date = datetime(end_date.year - 1, end_date.month, end_date.day)

        # 导入数据
        success, msg, bars = importer.import_data(
            qlib_dir=qlib_dir,
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start_date=start_date,
            end_date=end_date
        )

        print(f"导入结果: {success}")
        print(f"消息: {msg}")
        print(f"导入数据数量: {len(bars)}")

        # 打印前5条数据
        for i, bar in enumerate(bars[:5]):
            if i >= 5:
                break
            print(f"{i+1}. {bar.datetime.strftime('%Y-%m-%d')}: 开{bar.open_price:.2f} 高{bar.high_price:.2f} 低{bar.low_price:.2f} 收{bar.close_price:.2f} 量{bar.volume:.2f}")

if __name__ == "__main__":
    test_qlib_importer()
