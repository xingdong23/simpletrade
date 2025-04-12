#!/usr/bin/env python
"""
vnpy环境配置脚本

用于安装vnpy依赖和配置环境。
"""

import os
import subprocess
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
VNPY_DIR = ROOT_DIR / "vendors" / "vnpy"

def install_dependencies():
    """安装vnpy依赖"""
    # 检查vnpy目录是否存在
    if not VNPY_DIR.exists():
        print(f"Error: vnpy directory not found at {VNPY_DIR}")
        print("Please run 'git submodule update --init' to initialize the vnpy submodule.")
        return False

    # 安装基础依赖
    requirements_file = VNPY_DIR / "requirements.txt"
    if requirements_file.exists():
        print(f"Installing dependencies from {requirements_file}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])

    # 安装额外依赖(按需选择)
    install_talib()
    install_ibapi()

    # 安装外部模块
    install_external_modules()

    print("Dependencies installation completed.")
    return True

def install_talib():
    """安装TA-Lib"""
    try:
        import talib
        print("TA-Lib already installed.")
    except ImportError:
        print("Installing TA-Lib...")
        # 根据操作系统安装TA-Lib
        if sys.platform == "win32":
            # Windows
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--index-url=https://pypi.tuna.tsinghua.edu.cn/simple", "numpy"
            ])
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-f", "https://download.lfd.uci.edu/pythonlibs/archived/cp39/TA_Lib-0.4.24-cp39-cp39-win_amd64.whl", "TA-Lib"
            ])
        elif sys.platform == "darwin":
            # macOS
            try:
                subprocess.check_call(["brew", "install", "ta-lib"])
            except:
                print("Failed to install TA-Lib via brew. Please install it manually.")
                print("brew install ta-lib")

            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "TA-Lib"
            ])
        else:
            # Linux
            try:
                subprocess.check_call(["apt-get", "install", "-y", "ta-lib"])
            except:
                print("Failed to install TA-Lib via apt-get. Please install it manually.")
                print("sudo apt-get install ta-lib")

            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "TA-Lib"
            ])

def install_ibapi():
    """安装IB API"""
    try:
        import ibapi
        print("IB API already installed.")
    except ImportError:
        print("Installing IB API...")
        ibapi_dir = VNPY_DIR / "vnpy" / "api" / "ib" / "ibapi"
        if ibapi_dir.exists():
            os.chdir(ibapi_dir)
            subprocess.check_call([
                sys.executable, "setup.py", "install"
            ])
        else:
            print(f"Warning: IB API directory not found at {ibapi_dir}")

def install_external_modules():
    """安装外部模块"""
    # 第三方依赖目录
    vendors_dir = ROOT_DIR / "vendors"

    # 安装 vnpy_datamanager
    datamanager_dir = vendors_dir / "vnpy_datamanager"
    if datamanager_dir.exists():
        print(f"Installing vnpy_datamanager from {datamanager_dir}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-e", str(datamanager_dir)
        ])
    else:
        print(f"Warning: vnpy_datamanager directory not found at {datamanager_dir}")

    # 安装 vnpy_ib
    ib_dir = vendors_dir / "vnpy_ib"
    if ib_dir.exists():
        print(f"Installing vnpy_ib from {ib_dir}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-e", str(ib_dir)
        ])
    else:
        print(f"Warning: vnpy_ib directory not found at {ib_dir}")

    # 安装 vnpy_tiger
    tiger_dir = vendors_dir / "vnpy_tiger"
    if tiger_dir.exists():
        print(f"Installing vnpy_tiger from {tiger_dir}")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-e", str(tiger_dir)
        ])
    else:
        print(f"Warning: vnpy_tiger directory not found at {tiger_dir}")

if __name__ == "__main__":
    install_dependencies()
