"""
将Qlib数据直接导入到数据库

直接读取qlib格式的数据并导入到系统数据库中。
"""

import os
import sys
import struct
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到Python路径
root_path = str(Path(__file__).parent.parent)
sys.path.append(root_path)

# 添加vendors目录到Python路径
vendors_path = os.path.join(root_path, 'vendors')
sys.path.append(vendors_path)

# 导入vnpy相关模块
from vnpy.vnpy.trader.object import BarData
from vnpy.vnpy.trader.constant import Exchange, Interval
from vnpy.vnpy.trader.database import get_database

# 获取数据库对象
database_manager = get_database()

def read_calendar(qlib_dir):
    """读取交易日历"""
    calendar_path = os.path.join(qlib_dir, 'calendars', 'day.txt')
    if not os.path.exists(calendar_path):
        return []

    with open(calendar_path, 'r') as f:
        calendar = [line.strip() for line in f if line.strip()]

    return calendar

def read_qlib_bin_file(file_path):
    """读取qlib二进制文件"""
    if not os.path.exists(file_path):
        return None

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

def read_symbol_data(qlib_dir, symbol, start_date=None, end_date=None):
    """读取品种数据"""
    # 在qlib中，股票代码通常存储在features目录下
    features_dir = os.path.join(qlib_dir, 'features')
    symbol_path = os.path.join(features_dir, symbol)

    if not os.path.exists(symbol_path):
        print(f"品种路径不存在: {symbol_path}")
        return pd.DataFrame()

    # 获取所有可用的数据文件
    data_files = []
    for root, _, files in os.walk(symbol_path):
        for file in files:
            if file.endswith('.day.bin'):  # 只读取日线数据
                data_files.append(os.path.join(root, file))

    if not data_files:
        print(f"未找到数据文件: {symbol_path}")
        return pd.DataFrame()

    # 读取各个字段的数据
    field_dfs = {}
    for file_path in data_files:
        field_name = os.path.basename(file_path).split('.')[0]
        df = read_qlib_bin_file(file_path)
        if df is not None and not df.empty:
            field_dfs[field_name] = df

    if not field_dfs:
        print(f"未读取到有效数据: {symbol_path}")
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
    calendar = read_calendar(qlib_dir)
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

def convert_to_bar_data(df, symbol, exchange, interval):
    """将DataFrame转换为BarData列表"""
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
        field_mapping = {
            'open': 'open_price',
            'high': 'high_price',
            'low': 'low_price',
            'close': 'close_price',
            'volume': 'volume',
            'factor': 'open_interest'  # 使用factor作为open_interest
        }

        for qlib_field, vnpy_field in field_mapping.items():
            if qlib_field in row:
                setattr(bar, vnpy_field, float(row[qlib_field]))

        # 确保必要字段都有值
        required_fields = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
        if all(hasattr(bar, field) and getattr(bar, field) is not None for field in required_fields):
            bars.append(bar)

    return bars

def import_qlib_to_database():
    """将Qlib数据导入到数据库"""
    print("开始将Qlib数据导入到数据库...")

    # 设置qlib数据目录
    qlib_dir = "/Users/chengzheng/.qlib/qlib_data/cn_data"

    # 测试读取日历
    calendar = read_calendar(qlib_dir)
    print(f"读取到 {len(calendar)} 个交易日")
    if calendar:
        print(f"第一个交易日: {calendar[0]}")
        print(f"最后一个交易日: {calendar[-1]}")

    # 导入数据
    test_cases = [
        {"symbol": "600000", "qlib_symbol": "sh600000", "exchange": Exchange.SSE, "interval": Interval.DAILY},
        {"symbol": "000001", "qlib_symbol": "sz000001", "exchange": Exchange.SZSE, "interval": Interval.DAILY}
    ]

    for case in test_cases:
        symbol = case["symbol"]
        qlib_symbol = case["qlib_symbol"]
        exchange = case["exchange"]
        interval = case["interval"]

        print(f"\n导入 {symbol}.{exchange.value} {interval.value} 数据...")

        # 设置日期范围（最近一年）
        end_date = datetime(2020, 9, 25)  # 使用qlib数据的最后一个交易日
        start_date = datetime(2019, 9, 25)  # 最近一年的数据

        # 读取数据
        df = read_symbol_data(qlib_dir, qlib_symbol, start_date, end_date)

        if df.empty:
            print(f"未读取到数据: {qlib_symbol}")
            continue

        print(f"读取到 {len(df)} 条数据")

        # 转换为BarData列表
        bars = convert_to_bar_data(df, symbol, exchange, interval)

        if not bars:
            print(f"转换数据失败: {qlib_symbol}")
            continue

        print(f"转换得到 {len(bars)} 条BarData")

        # 将数据保存到数据库
        database_manager.save_bar_data(bars)
        print(f"成功将 {len(bars)} 条数据保存到数据库")

        # 打印前5条数据
        for i, bar in enumerate(bars[:5]):
            if i >= 5:
                break
            print(f"{i+1}. {bar.datetime.strftime('%Y-%m-%d')}: 开{bar.open_price:.4f} 高{bar.high_price:.4f} 低{bar.low_price:.4f} 收{bar.close_price:.4f} 量{bar.volume:.0f}")

if __name__ == "__main__":
    import_qlib_to_database()
