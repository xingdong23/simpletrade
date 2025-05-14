#!/usr/bin/env python3
"""
修复ArrayManager类中的技术指标计算函数，使用pandas-ta替代talib
"""

import os
import re
from pathlib import Path

# 配置
VNPY_CUSTOM_DIR = Path("/Users/chengzheng/workspace/trade/simpletrade/vnpy_custom")
UTILITY_FILE = VNPY_CUSTOM_DIR / "vnpy" / "trader" / "utility.py"

def fix_array_manager():
    """修复ArrayManager类中的技术指标计算函数"""
    if not UTILITY_FILE.exists():
        print(f"未找到utility.py文件: {UTILITY_FILE}")
        return False
    
    print(f"修复ArrayManager类: {UTILITY_FILE}")
    
    # 读取文件内容
    with open(UTILITY_FILE, "r") as f:
        content = f.read()
    
    # 替换导入语句
    content = re.sub(
        r"import talib",
        "# import talib  # 已替换为pandas-ta\nimport pandas as pd\nimport pandas_ta as ta",
        content
    )
    
    # 添加辅助函数
    helper_functions = """
# 辅助函数，将numpy数组转换为pandas Series
def _to_series(array):
    return pd.Series(array)
"""
    
    # 在ArrayManager类定义前添加辅助函数
    content = re.sub(
        r"class ArrayManager\(object\):",
        helper_functions + "\n\nclass ArrayManager(object):",
        content
    )
    
    # 替换技术指标计算函数
    replacements = [
        # SMA
        (r"talib\.SMA\(([^,]+), ([^)]+)\)", r"ta.sma(_to_series(\1), length=\2).values"),
        # EMA
        (r"talib\.EMA\(([^,]+), ([^)]+)\)", r"ta.ema(_to_series(\1), length=\2).values"),
        # KAMA
        (r"talib\.KAMA\(([^,]+), ([^)]+)\)", r"ta.kama(_to_series(\1), length=\2).values"),
        # WMA
        (r"talib\.WMA\(([^,]+), ([^)]+)\)", r"ta.wma(_to_series(\1), length=\2).values"),
        # APO
        (r"talib\.APO\(([^,]+), ([^,]+), ([^,]+), talib\.MA_Type\(([^)]+)\)\)", 
         r"ta.apo(_to_series(\1), fast=\2, slow=\3).values"),
        # CMO
        (r"talib\.CMO\(([^,]+), ([^)]+)\)", r"ta.cmo(_to_series(\1), length=\2).values"),
        # MACD
        (r"talib\.MACD\(([^,]+), ([^,]+), ([^,]+), ([^)]+)\)",
         r"ta.macd(_to_series(\1), fast=\2, slow=\3, signal=\4).values"),
        # MACD返回值
        (r"macd, signal, hist = self\.macd\(([^,]+), ([^,]+), ([^,]+), array=True\)",
         r"macd_result = ta.macd(_to_series(self.close), fast=\1, slow=\2, signal=\3)\n        macd = macd_result[f\"MACD_{\1}_{\2}_{\3}\"].values\n        signal = macd_result[f\"MACDs_{\1}_{\2}_{\3}\"].values\n        hist = macd_result[f\"MACDh_{\1}_{\2}_{\3}\"].values"),
        # RSI
        (r"talib\.RSI\(([^,]+), ([^)]+)\)", r"ta.rsi(_to_series(\1), length=\2).values"),
        # BOLL
        (r"talib\.BBANDS\(([^,]+), ([^,]+), ([^,]+), ([^)]+)\)",
         r"ta.bbands(_to_series(\1), length=\2, std=\3).values"),
        # BOLL返回值
        (r"up, middle, low = self\.boll\(([^,]+), ([^,]+), array=True\)",
         r"boll_result = ta.bbands(_to_series(self.close), length=\1, std=\2)\n        up = boll_result[f\"BBU_{\1}_{\2}\"].values\n        middle = boll_result[f\"BBM_{\1}_{\2}\"].values\n        low = boll_result[f\"BBL_{\1}_{\2}\"].values"),
        # ATR
        (r"talib\.ATR\(([^,]+), ([^,]+), ([^,]+), ([^)]+)\)",
         r"ta.atr(_to_series(\1), _to_series(\2), _to_series(\3), length=\4).values"),
        # CCI
        (r"talib\.CCI\(([^,]+), ([^,]+), ([^,]+), ([^)]+)\)",
         r"ta.cci(_to_series(\1), _to_series(\2), _to_series(\3), length=\4).values"),
        # ADX
        (r"talib\.ADX\(([^,]+), ([^,]+), ([^,]+), ([^)]+)\)",
         r"ta.adx(_to_series(\1), _to_series(\2), _to_series(\3), length=\4).values"),
    ]
    
    # 应用替换
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # 写入修改后的内容
    with open(UTILITY_FILE, "w") as f:
        f.write(content)
    
    print(f"已修复ArrayManager类: {UTILITY_FILE}")
    return True

def main():
    """主函数"""
    success = fix_array_manager()
    
    if success:
        print("修复完成！")
    else:
        print("修复失败！")

if __name__ == "__main__":
    main()
