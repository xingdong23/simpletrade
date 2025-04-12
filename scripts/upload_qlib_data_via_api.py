"""
通过API上传Qlib数据

使用API接口将qlib格式的数据上传到系统中。
"""

import os
import sys
import requests
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

def upload_csv_data(csv_file, symbol, exchange, interval):
    """通过API上传CSV数据"""
    print(f"上传数据: {csv_file}")
    
    # 读取CSV数据
    df = pd.read_csv(csv_file)
    print(f"读取到 {len(df)} 条数据")
    
    # 转换为API需要的格式
    data = []
    for _, row in df.iterrows():
        bar_data = {
            "symbol": symbol,
            "exchange": exchange,
            "interval": interval,
            "datetime": row["datetime"],
            "open_price": float(row["open"]),
            "high_price": float(row["high"]),
            "low_price": float(row["low"]),
            "close_price": float(row["close"]),
            "volume": float(row["volume"]),
            "open_interest": float(row.get("factor", 0))
        }
        data.append(bar_data)
    
    # 上传数据
    url = "http://localhost:8000/api/datamanager/bars/upload"
    headers = {"Content-Type": "application/json"}
    payload = {
        "bars": data
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"上传响应: {response.status_code}")
        print(f"响应内容: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"上传失败: {str(e)}")
        return False

def upload_qlib_data():
    """上传Qlib数据"""
    print("开始上传Qlib数据...")
    
    # 设置数据目录
    data_dir = "test_data/qlib_data"
    
    # 上传数据
    test_cases = [
        {"csv_file": "sh600000.csv", "symbol": "600000", "exchange": "SSE", "interval": "d"},
        {"csv_file": "sz000001.csv", "symbol": "000001", "exchange": "SZSE", "interval": "d"}
    ]
    
    for case in test_cases:
        csv_file = os.path.join(data_dir, case["csv_file"])
        symbol = case["symbol"]
        exchange = case["exchange"]
        interval = case["interval"]
        
        print(f"\n上传 {symbol}.{exchange} {interval} 数据...")
        
        if not os.path.exists(csv_file):
            print(f"CSV文件不存在: {csv_file}")
            continue
        
        success = upload_csv_data(csv_file, symbol, exchange, interval)
        
        if success:
            print(f"成功上传数据: {csv_file}")
        else:
            print(f"上传数据失败: {csv_file}")

if __name__ == "__main__":
    upload_qlib_data()
