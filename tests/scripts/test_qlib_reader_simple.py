"""
测试Qlib数据读取

用于测试读取qlib格式数据的功能。
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
        print(f"文件: {file_path}")
        print(f"开始索引: {start_index}")
        
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

def test_qlib_reader():
    """测试Qlib数据读取"""
    print("开始测试Qlib数据读取...")
    
    # 设置qlib数据目录
    qlib_dir = "/Users/chengzheng/.qlib/qlib_data/cn_data"
    
    # 测试读取日历
    calendar = read_calendar(qlib_dir)
    print(f"读取到 {len(calendar)} 个交易日")
    if calendar:
        print(f"第一个交易日: {calendar[0]}")
        print(f"最后一个交易日: {calendar[-1]}")
    
    # 测试读取单个数据文件
    symbol = "sh600000"
    field = "close"
    file_path = os.path.join(qlib_dir, 'features', symbol, f"{field}.day.bin")
    
    if os.path.exists(file_path):
        print(f"\n读取文件: {file_path}")
        df = read_qlib_bin_file(file_path)
        print(f"读取到 {len(df)} 条数据")
        print("前5条数据:")
        print(df.head())
        
        # 将索引转换为日期
        if calendar:
            # 创建日期映射字典，将数字索引映射到日期
            date_map = {i: pd.Timestamp(date) for i, date in enumerate(calendar)}
            
            # 将索引转换为日期
            df['datetime'] = df.index.map(lambda x: date_map.get(x, pd.NaT))
            
            # 删除无效日期
            df = df.dropna(subset=['datetime'])
            
            print("\n转换日期后的前5条数据:")
            print(df.head())
    else:
        print(f"文件不存在: {file_path}")

if __name__ == "__main__":
    test_qlib_reader()
