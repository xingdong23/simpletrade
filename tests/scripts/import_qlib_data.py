"""
导入Qlib数据

用于将qlib格式的数据导入到数据库中。
"""

import os
import sys
import struct
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

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

def read_calendar(qlib_dir):
    """读取交易日历"""
    calendar_path = os.path.join(qlib_dir, 'calendars', 'day.txt')
    if not os.path.exists(calendar_path):
        return []
    
    with open(calendar_path, 'r') as f:
        calendar = [line.strip() for line in f if line.strip()]
    
    return calendar

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

def import_qlib_data():
    """导入Qlib数据"""
    print("开始导入Qlib数据...")
    
    # 设置qlib数据目录
    qlib_dir = "/Users/chengzheng/.qlib/qlib_data/cn_data"
    
    # 测试读取日历
    calendar = read_calendar(qlib_dir)
    print(f"读取到 {len(calendar)} 个交易日")
    if calendar:
        print(f"第一个交易日: {calendar[0]}")
        print(f"最后一个交易日: {calendar[-1]}")
    
    # 测试读取品种数据
    test_symbols = ["sh600000", "sz000001"]
    
    for symbol in test_symbols:
        print(f"\n导入 {symbol} 数据...")
        
        # 设置日期范围（最近一年）
        end_date = datetime(2020, 9, 25)  # 使用qlib数据的最后一个交易日
        start_date = datetime(2019, 9, 25)  # 最近一年的数据
        
        # 读取数据
        df = read_symbol_data(qlib_dir, symbol, start_date, end_date)
        
        print(f"读取到 {len(df)} 条数据")
        if not df.empty:
            print("数据字段:")
            for col in df.columns:
                print(f"  - {col}")
            
            print("\n前5条数据:")
            print(df.head())
            
            # 保存数据到CSV文件
            output_dir = "test_data/qlib_data"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"{symbol}.csv")
            df.to_csv(output_file)
            print(f"数据已保存到: {output_file}")

if __name__ == "__main__":
    import_qlib_data()
