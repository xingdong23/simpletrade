#!/usr/bin/env python3
"""
修改vnpy源码，移除TA-Lib依赖

这个脚本会自动修改vnpy源码中的TA-Lib依赖，替换为pandas-ta的调用。
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

# 配置
VNPY_REPO = "https://github.com/vnpy/vnpy.git"
VNPY_CUSTOM_DIR = Path("/Users/chengzheng/workspace/trade/simpletrade/vnpy_custom")
BACKUP_DIR = Path("/Users/chengzheng/workspace/trade/simpletrade/vnpy_backup")

def clone_vnpy():
    """克隆vnpy仓库"""
    if not VNPY_CUSTOM_DIR.exists():
        print(f"克隆vnpy仓库到 {VNPY_CUSTOM_DIR}...")
        subprocess.run(["git", "clone", VNPY_REPO, VNPY_CUSTOM_DIR])
    else:
        print(f"vnpy目录已存在: {VNPY_CUSTOM_DIR}")

def backup_vnpy():
    """备份vnpy源码"""
    if not BACKUP_DIR.exists():
        print(f"备份vnpy源码到 {BACKUP_DIR}...")
        shutil.copytree(VNPY_CUSTOM_DIR, BACKUP_DIR)
    else:
        print(f"备份目录已存在: {BACKUP_DIR}")

def find_talib_files():
    """查找使用talib的文件"""
    print("查找使用talib的文件...")
    result = subprocess.run(
        ["grep", "-r", "import talib", VNPY_CUSTOM_DIR],
        capture_output=True,
        text=True
    )
    
    files = []
    for line in result.stdout.splitlines():
        if ":" in line:
            file_path = line.split(":")[0]
            files.append(file_path)
    
    return files

def modify_array_manager():
    """修改ArrayManager类"""
    utility_file = VNPY_CUSTOM_DIR / "vnpy" / "trader" / "utility.py"
    
    if not utility_file.exists():
        print(f"未找到ArrayManager类文件: {utility_file}")
        return
    
    print(f"修改ArrayManager类: {utility_file}")
    
    # 读取文件内容
    with open(utility_file, "r") as f:
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
    
    # 在类定义前添加辅助函数
    content = re.sub(
        r"class ArrayManager\(object\):",
        helper_functions + "\n\nclass ArrayManager(object):",
        content
    )
    
    # 替换TA-Lib函数调用
    replacements = [
        # SMA
        (r"talib\.SMA\(array, n\)", "ta.sma(_to_series(array), length=n).values"),
        # EMA
        (r"talib\.EMA\(array, n\)", "ta.ema(_to_series(array), length=n).values"),
        # MACD
        (r"talib\.MACD\(array, fast_period, slow_period, signal_period\)",
         "ta.macd(_to_series(array), fast=fast_period, slow=slow_period, signal=signal_period).values.T"),
        # RSI
        (r"talib\.RSI\(array, n\)", "ta.rsi(_to_series(array), length=n).values"),
        # BOLL
        (r"talib\.BBANDS\(array, n, dev, dev\)",
         "ta.bbands(_to_series(array), length=n, std=dev).values.T"),
        # ATR
        (r"talib\.ATR\(high, low, close, n\)",
         "ta.atr(_to_series(high), _to_series(low), _to_series(close), length=n).values"),
        # CCI
        (r"talib\.CCI\(high, low, close, n\)",
         "ta.cci(_to_series(high), _to_series(low), _to_series(close), length=n).values"),
        # ADX
        (r"talib\.ADX\(high, low, close, n\)",
         "ta.adx(_to_series(high), _to_series(low), _to_series(close), length=n).values"),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # 写入修改后的内容
    with open(utility_file, "w") as f:
        f.write(content)
    
    print(f"已修改ArrayManager类: {utility_file}")

def modify_other_files(files):
    """修改其他使用talib的文件"""
    for file_path in files:
        if not os.path.exists(file_path):
            continue
        
        print(f"修改文件: {file_path}")
        
        # 读取文件内容
        with open(file_path, "r") as f:
            content = f.read()
        
        # 替换导入语句
        content = re.sub(
            r"import talib",
            "# import talib  # 已替换为pandas-ta\nimport pandas as pd\nimport pandas_ta as ta",
            content
        )
        
        # 写入修改后的内容
        with open(file_path, "w") as f:
            f.write(content)
        
        print(f"已修改文件: {file_path}")

def create_init_file():
    """创建__init__.py文件，导入修改后的vnpy模块"""
    init_file = Path("/Users/chengzheng/workspace/trade/simpletrade/vnpy_custom/__init__.py")
    
    print(f"创建__init__.py文件: {init_file}")
    
    content = """"""
    
    with open(init_file, "w") as f:
        f.write(content)
    
    print(f"已创建__init__.py文件: {init_file}")

def update_requirements():
    """更新requirements.txt文件，添加pandas-ta依赖"""
    req_file = Path("/Users/chengzheng/workspace/trade/simpletrade/requirements.txt")
    
    if not req_file.exists():
        print(f"未找到requirements.txt文件: {req_file}")
        return
    
    print(f"更新requirements.txt文件: {req_file}")
    
    # 读取文件内容
    with open(req_file, "r") as f:
        content = f.read()
    
    # 添加pandas-ta依赖
    if "pandas-ta" not in content:
        content += "\n# 替代TA-Lib的依赖\npandas-ta>=0.3.14b0\n"
    
    # 写入修改后的内容
    with open(req_file, "w") as f:
        f.write(content)
    
    print(f"已更新requirements.txt文件: {req_file}")

def main():
    """主函数"""
    # 克隆vnpy仓库
    clone_vnpy()
    
    # 备份vnpy源码
    backup_vnpy()
    
    # 查找使用talib的文件
    talib_files = find_talib_files()
    print(f"找到 {len(talib_files)} 个使用talib的文件")
    
    # 修改ArrayManager类
    modify_array_manager()
    
    # 修改其他使用talib的文件
    modify_other_files(talib_files)
    
    # 创建__init__.py文件
    create_init_file()
    
    # 更新requirements.txt文件
    update_requirements()
    
    print("修改完成！")

if __name__ == "__main__":
    main()
