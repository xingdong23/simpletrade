"""
将CSV数据导入到SQLite数据库

直接使用sqlite3将CSV格式的数据导入到系统数据库中。
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

def convert_csv_to_db_format(csv_file, symbol, exchange, interval):
    """将CSV数据转换为数据库格式"""
    print(f"转换CSV文件: {csv_file}")
    
    # 读取CSV数据
    df = pd.read_csv(csv_file)
    print(f"读取到 {len(df)} 条数据")
    
    # 打印列名
    print(f"列名: {df.columns.tolist()}")
    
    # 创建结果列表
    result = []
    for _, row in df.iterrows():
        # 解析日期时间
        dt = datetime.strptime(row['datetime'], '%Y-%m-%d')
        
        # 创建数据记录
        record = {
            "symbol": symbol,
            "exchange": exchange,
            "interval": interval,
            "datetime": dt.strftime('%Y-%m-%d %H:%M:%S'),
            "open_price": float(row['open']),
            "high_price": float(row['high']),
            "low_price": float(row['low']),
            "close_price": float(row['close']),
            "volume": float(row['volume']),
            "open_interest": float(row.get('factor', 0))
        }
        
        result.append(record)
    
    print(f"转换得到 {len(result)} 条记录")
    return result

def import_to_sqlite(db_path, records):
    """将记录导入到SQLite数据库"""
    print(f"导入数据到数据库: {db_path}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bar_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        exchange TEXT,
        interval TEXT,
        datetime TEXT,
        open_price REAL,
        high_price REAL,
        low_price REAL,
        close_price REAL,
        volume REAL,
        open_interest REAL
    )
    ''')
    
    # 插入数据
    for record in records:
        cursor.execute('''
        INSERT INTO bar_data (
            symbol, exchange, interval, datetime,
            open_price, high_price, low_price, close_price,
            volume, open_interest
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record['symbol'], record['exchange'], record['interval'], record['datetime'],
            record['open_price'], record['high_price'], record['low_price'], record['close_price'],
            record['volume'], record['open_interest']
        ))
    
    # 提交事务
    conn.commit()
    
    # 关闭连接
    conn.close()
    
    print(f"成功导入 {len(records)} 条记录到数据库")

def import_csv_to_sqlite():
    """将CSV数据导入到SQLite数据库"""
    print("开始将CSV数据导入到SQLite数据库...")
    
    # 设置数据库路径
    db_path = "data.db"
    
    # 设置CSV数据目录
    csv_dir = "test_data/qlib_data"
    
    # 导入数据
    test_cases = [
        {"csv_file": "sh600000.csv", "symbol": "600000", "exchange": "SSE", "interval": "d"},
        {"csv_file": "sz000001.csv", "symbol": "000001", "exchange": "SZSE", "interval": "d"}
    ]
    
    for case in test_cases:
        csv_file = os.path.join(csv_dir, case["csv_file"])
        symbol = case["symbol"]
        exchange = case["exchange"]
        interval = case["interval"]
        
        print(f"\n导入 {symbol}.{exchange} {interval} 数据...")
        
        if not os.path.exists(csv_file):
            print(f"CSV文件不存在: {csv_file}")
            continue
        
        # 转换为数据库格式
        records = convert_csv_to_db_format(csv_file, symbol, exchange, interval)
        
        if not records:
            print(f"转换数据失败: {csv_file}")
            continue
        
        # 导入到数据库
        import_to_sqlite(db_path, records)
        
        # 打印前5条数据
        for i, record in enumerate(records[:5]):
            if i >= 5:
                break
            print(f"{i+1}. {record['datetime']}: 开{record['open_price']:.4f} 高{record['high_price']:.4f} 低{record['low_price']:.4f} 收{record['close_price']:.4f} 量{record['volume']:.0f}")

if __name__ == "__main__":
    import_csv_to_sqlite()
