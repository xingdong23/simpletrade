"""
将Qlib数据导入到数据库

使用QlibDataImporter将qlib格式的数据导入到系统数据库中。
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
root_path = str(Path(__file__).parent.parent)
sys.path.append(root_path)

from simpletrade.apps.st_datamanager.importers.qlib_importer import QlibDataImporter
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import database_manager

def import_qlib_to_database():
    """将Qlib数据导入到数据库"""
    print("开始将Qlib数据导入到数据库...")
    
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
    
    # 导入数据
    test_cases = [
        {"symbol": "600000", "exchange": Exchange.SSE, "interval": Interval.DAILY},
        {"symbol": "000001", "exchange": Exchange.SZSE, "interval": Interval.DAILY}
    ]
    
    for case in test_cases:
        symbol = case["symbol"]
        exchange = case["exchange"]
        interval = case["interval"]
        
        print(f"\n导入 {symbol}.{exchange.value} {interval.value} 数据...")
        
        # 设置日期范围（最近一年）
        end_date = datetime(2020, 9, 25)  # 使用qlib数据的最后一个交易日
        start_date = datetime(2019, 9, 25)  # 最近一年的数据
        
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
        
        if success and bars:
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
