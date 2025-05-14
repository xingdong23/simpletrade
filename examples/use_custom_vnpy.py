#!/usr/bin/env python3
"""
使用修改后的vnpy示例

这个示例展示了如何使用修改后的vnpy，不依赖TA-Lib。
"""

import sys
import os
from pathlib import Path

# 添加自定义vnpy目录到Python路径
VNPY_CUSTOM_DIR = Path("/Users/chengzheng/workspace/trade/simpletrade/vnpy_custom")
sys.path.insert(0, str(VNPY_CUSTOM_DIR))

# 导入必要的模块
import numpy as np
import pandas as pd
import pandas_ta as ta

# 导入修改后的vnpy模块
from vnpy.trader.utility import ArrayManager

def test_array_manager():
    """测试修改后的ArrayManager类"""
    print("测试修改后的ArrayManager类...")
    
    # 创建ArrayManager实例
    am = ArrayManager(size=100)
    
    # 创建模拟数据
    class Bar:
        def __init__(self, open_price, high_price, low_price, close_price, volume):
            self.open_price = open_price
            self.high_price = high_price
            self.low_price = low_price
            self.close_price = close_price
            self.volume = volume
    
    # 生成随机数据
    np.random.seed(42)
    for i in range(100):
        close = 100 + np.random.randn() * 10
        high = close + abs(np.random.randn()) * 5
        low = close - abs(np.random.randn()) * 5
        open_price = low + (high - low) * np.random.rand()
        volume = np.random.randint(1000, 10000)
        
        bar = Bar(open_price, high, low, close, volume)
        am.update_bar(bar)
    
    # 测试技术指标
    print("SMA(10):", am.sma(10))
    print("EMA(10):", am.ema(10))
    print("MACD:", am.macd(12, 26, 9))
    print("RSI(14):", am.rsi(14))
    print("BOLL(20, 2):", am.boll(20, 2))
    print("ATR(14):", am.atr(14))
    
    print("测试完成！")

def main():
    """主函数"""
    test_array_manager()

if __name__ == "__main__":
    main()
