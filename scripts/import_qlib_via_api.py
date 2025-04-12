"""
通过API导入Qlib数据

使用API接口将qlib格式的数据导入到系统中。
"""

import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

def import_qlib_data():
    """通过API导入Qlib数据"""
    print("开始通过API导入Qlib数据...")
    
    # 设置API地址
    api_url = "http://localhost:8000/api/data/import/qlib"
    
    # 设置qlib数据目录
    qlib_dir = "/Users/chengzheng/.qlib/qlib_data/cn_data"
    
    # 导入数据
    test_cases = [
        {"symbol": "600000", "exchange": "SSE", "interval": "d"},
        {"symbol": "000001", "exchange": "SZSE", "interval": "d"}
    ]
    
    for case in test_cases:
        symbol = case["symbol"]
        exchange = case["exchange"]
        interval = case["interval"]
        
        print(f"\n导入 {symbol}.{exchange} {interval} 数据...")
        
        # 设置日期范围（最近一年）
        end_date = "2020-09-25"  # 使用qlib数据的最后一个交易日
        start_date = "2019-09-25"  # 最近一年的数据
        
        # 准备请求数据
        payload = {
            "qlib_dir": qlib_dir,
            "symbol": symbol,
            "exchange": exchange,
            "interval": interval,
            "start_date": start_date,
            "end_date": end_date
        }
        
        # 发送请求
        try:
            response = requests.post(api_url, json=payload)
            print(f"API响应: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                print(f"成功导入数据: {symbol}.{exchange}")
            else:
                print(f"导入数据失败: {symbol}.{exchange}")
        except Exception as e:
            print(f"请求失败: {str(e)}")

if __name__ == "__main__":
    import_qlib_data()
