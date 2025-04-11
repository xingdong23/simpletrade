#!/usr/bin/env python
"""
vnpy更新脚本

用于更新vnpy源码。
"""

import os
import subprocess
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
VNPY_DIR = ROOT_DIR / "vnpy"

def update_vnpy(target_version=None):
    """
    更新vnpy源码

    参数:
        target_version (str, optional): 目标版本，如v4.0.0，默认为None

    返回:
        bool: 是否成功
    """
    # 检查vnpy目录是否存在
    if not VNPY_DIR.exists():
        print(f"Error: vnpy directory not found at {VNPY_DIR}")
        print("Please run 'git submodule update --init' to initialize the vnpy submodule.")
        return False

    # 进入vnpy目录
    cwd = Path.cwd()
    os.chdir(VNPY_DIR)

    try:
        # 获取当前版本
        current_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"]
        ).decode("utf-8").strip()
        print(f"Current vnpy commit: {current_commit}")

        # 获取远程更新
        subprocess.check_call(["git", "fetch", "origin"])

        if target_version:
            # 切换到指定版本
            subprocess.check_call(["git", "checkout", target_version])
            print(f"Switched to vnpy version: {target_version}")
        else:
            # 获取最新版本
            subprocess.check_call(["git", "checkout", "master"])
            subprocess.check_call(["git", "pull"])
            latest_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"]
            ).decode("utf-8").strip()
            print(f"Updated to latest vnpy commit: {latest_commit}")

        # 返回项目根目录
        os.chdir(cwd)

        # 更新子模块引用
        subprocess.check_call(
            ["git", "add", "vnpy"],
            cwd=ROOT_DIR
        )

        print("vnpy update completed. Please commit the changes.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error updating vnpy: {e}")
        # 返回项目根目录
        os.chdir(cwd)
        return False

if __name__ == "__main__":
    # 解析命令行参数
    target_version = None
    if len(sys.argv) > 1:
        target_version = sys.argv[1]

    update_vnpy(target_version)
