"""
将CSV数据导入到数据库

将CSV格式的数据导入到系统数据库中。
"""

import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

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

def convert_csv_to_bars(csv_file, symbol, exchange, interval):
    """将CSV数据转换为BarData列表"""
    print(f"转换CSV文件: {csv_file}")
    
    # 读取CSV数据
    df = pd.read_csv(csv_file)
    print(f"读取到 {len(df)} 条数据")
    
    # 打印列名
    print(f"列名: {df.columns.tolist()}")
    
    # 转换为BarData列表
    bars = []
    for _, row in df.iterrows():
        # 创建BarData对象
        bar = BarData(
            symbol=symbol,
            exchange=exchange,
            datetime=datetime.strptime(row['datetime'], '%Y-%m-%d'),
            interval=interval,
            gateway_name="CSV"
        )
        
        # 设置价格和成交量数据
        field_mapping = {
            'open': 'open_price',
            'high': 'high_price',
            'low': 'low_price',
            'close': 'close_price',
            'volume': 'volume',
            'factor': 'open_interest'
        }
        
        for csv_field, bar_field in field_mapping.items():
            if csv_field in row:
                setattr(bar, bar_field, float(row[csv_field]))
        
        # 确保必要字段都有值
        required_fields = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
        if all(hasattr(bar, field) and getattr(bar, field) is not None for field in required_fields):
            bars.append(bar)
    
    print(f"转换得到 {len(bars)} 条BarData")
    return bars

def import_csv_to_database():
    """将CSV数据导入到数据库"""
    print("开始将CSV数据导入到数据库...")
    
    # 获取数据库对象
    database_manager = get_database()
    
    # 设置CSV数据目录
    csv_dir = "test_data/qlib_data"
    
    # 导入数据
    test_cases = [
        {"csv_file": "sh600000.csv", "symbol": "600000", "exchange": Exchange.SSE, "interval": Interval.DAILY},
        {"csv_file": "sz000001.csv", "symbol": "000001", "exchange": Exchange.SZSE, "interval": Interval.DAILY}
    ]
    
    for case in test_cases:
        csv_file = os.path.join(csv_dir, case["csv_file"])
        symbol = case["symbol"]
        exchange = case["exchange"]
        interval = case["interval"]
        
        print(f"\n导入 {symbol}.{exchange.value} {interval.value} 数据...")
        
        if not os.path.exists(csv_file):
            print(f"CSV文件不存在: {csv_file}")
            continue
        
        # 转换为BarData列表
        bars = convert_csv_to_bars(csv_file, symbol, exchange, interval)
        
        if not bars:
            print(f"转换数据失败: {csv_file}")
            continue
        
        # 将数据保存到数据库
        database_manager.save_bar_data(bars)
        print(f"成功将 {len(bars)} 条数据保存到数据库")
        
        # 打印前5条数据
        for i, bar in enumerate(bars[:5]):
            if i >= 5:
                break
            print(f"{i+1}. {bar.datetime.strftime('%Y-%m-%d')}: 开{bar.open_price:.4f} 高{bar.high_price:.4f} 低{bar.low_price:.4f} 收{bar.close_price:.4f} 量{bar.volume:.0f}")

if __name__ == "__main__":
    import_csv_to_database()
