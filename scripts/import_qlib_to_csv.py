"""
将Qlib数据导出为CSV

使用QlibDataImporter将qlib格式的数据导出为CSV文件，然后可以通过CSV导入功能导入到系统中。
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
from vnpy.trader.constant import Exchange, Interval

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
    print(f"\n开始读取品种数据: {symbol}")

    # 在qlib中，股票代码通常存储在features目录下
    features_dir = os.path.join(qlib_dir, 'features')
    symbol_path = os.path.join(features_dir, symbol)
    print(f"品种路径: {symbol_path}")

    if not os.path.exists(symbol_path):
        print(f"品种路径不存在: {symbol_path}")
        return pd.DataFrame()

    # 获取所有可用的数据文件
    data_files = []
    for root, _, files in os.walk(symbol_path):
        for file in files:
            if file.endswith('.day.bin'):  # 只读取日线数据
                data_files.append(os.path.join(root, file))

    print(f"找到 {len(data_files)} 个数据文件")
    for file in data_files[:5]:  # 只显示前5个
        print(f"  - {os.path.basename(file)}")

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

def export_to_csv(df, output_file):
    """导出数据到CSV文件"""
    # 打印原始列名
    print(f"原始列名: {df.columns.tolist()}")

    # 重命名列名，使其符合vnpy的命名规范
    rename_map = {
        'open': 'open_price',
        'high': 'high_price',
        'low': 'low_price',
        'close': 'close_price',
        'volume': 'volume',
        'factor': 'open_interest'
    }

    # 重命名列
    df_renamed = df.copy()
    for old_name, new_name in rename_map.items():
        if old_name in df_renamed.columns:
            df_renamed[new_name] = df_renamed[old_name]
            df_renamed = df_renamed.drop(old_name, axis=1)

    # 打印重命名后的列名
    print(f"重命名后的列名: {df_renamed.columns.tolist()}")

    # 确保所有必要的列都存在
    required_columns = ['datetime', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'open_interest']
    for col in required_columns:
        if col not in df_renamed.columns:
            if col == 'open_interest':
                df_renamed[col] = 0  # 设置默认值
            elif col == 'volume' and 'factor' in df_renamed.columns:
                # 如果没有volume列但有factor列，使用factor作为volume
                df_renamed[col] = df_renamed['factor'] * 10000
                print(f"使用factor作为{col}")
            else:
                print(f"缺少必要的列: {col}")
                return False

    # 导出到CSV文件
    df_renamed.to_csv(output_file, index=False)
    print(f"数据已导出到: {output_file}")
    return True

def import_qlib_to_csv():
    """将Qlib数据导出为CSV"""
    print("开始将Qlib数据导出为CSV...")

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
        {"symbol": "sh600000", "output_symbol": "600000", "exchange": "SSE", "interval": "d"},
        {"symbol": "sz000001", "output_symbol": "000001", "exchange": "SZSE", "interval": "d"}
    ]

    # 创建输出目录
    output_dir = "data/csv"
    os.makedirs(output_dir, exist_ok=True)

    for case in test_cases:
        symbol = case["symbol"]
        output_symbol = case["output_symbol"]
        exchange = case["exchange"]
        interval = case["interval"]

        print(f"\n导出 {symbol} 数据...")

        # 设置日期范围（最近一年）
        end_date = datetime(2020, 9, 25)  # 使用qlib数据的最后一个交易日
        start_date = datetime(2019, 9, 25)  # 最近一年的数据

        # 读取数据
        df = read_symbol_data(qlib_dir, symbol, start_date, end_date)

        if df.empty:
            print(f"未读取到数据: {symbol}")
            continue

        print(f"读取到 {len(df)} 条数据")

        # 导出到CSV文件
        output_file = os.path.join(output_dir, f"{output_symbol}_{exchange}_{interval}.csv")
        success = export_to_csv(df, output_file)

        if success:
            print(f"成功导出数据: {output_file}")
        else:
            print(f"导出数据失败: {symbol}")

if __name__ == "__main__":
    import_qlib_to_csv()
