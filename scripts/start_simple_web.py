#!/usr/bin/env python
"""
启动简单的Web前端

启动SimpleTrade的API服务器并打开简单的HTML页面。
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

def start_api_server():
    """启动API服务器"""
    print("正在启动API服务器...")

    # 检查依赖是否安装
    missing_deps = []
    try:
        import python_jose
    except ImportError:
        missing_deps.append("python-jose")
    
    try:
        import vnpy_sqlite
    except ImportError:
        missing_deps.append("vnpy_sqlite")
    
    try:
        import python_multipart
    except ImportError:
        missing_deps.append("python-multipart")
    
    if missing_deps:
        print(f"缺少依赖: {', '.join(missing_deps)}")
        print("正在安装缺少的依赖...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_deps, check=True)
            print("依赖安装成功")
        except subprocess.CalledProcessError as e:
            print(f"依赖安装失败: {e}")
            print("请手动安装依赖: pip install " + " ".join(missing_deps))
            return None

    try:
        # 创建一个新的进程来运行API服务器
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "simpletrade.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 等待API服务器启动
        print("等待API服务器启动...")
        start_time = time.time()
        max_wait_time = 10  # 最多等待10秒
        
        while time.time() - start_time < max_wait_time:
            # 检查进程是否还在运行
            if api_process.poll() is not None:
                # 进程已经结束，读取错误信息
                stdout, stderr = api_process.communicate()
                print(f"启动API服务器失败，进程已退出，退出码: {api_process.returncode}")
                print(f"标准输出: {stdout}")
                print(f"错误输出: {stderr}")
                return None
            
            # 尝试连接API服务器
            try:
                import requests
                response = requests.get("http://localhost:8000/docs", timeout=0.5)
                if response.status_code == 200:
                    print("API服务器启动成功，访问 http://localhost:8000/docs 查看API文档")
                    return api_process
            except Exception:
                # 连接失败，继续等待
                pass
            
            time.sleep(0.5)
        
        # 如果超时但进程仍在运行，假设服务器已经启动
        if api_process.poll() is None:
            print("API服务器似乎已经启动，但无法确认。访问 http://localhost:8000/docs 查看API文档")
            return api_process
        else:
            # 进程已经结束，读取错误信息
            stdout, stderr = api_process.communicate()
            print(f"启动API服务器失败，进程已退出，退出码: {api_process.returncode}")
            print(f"标准输出: {stdout}")
            print(f"错误输出: {stderr}")
            return None
    except Exception as e:
        print(f"启动API服务器失败: {e}")
        return None

def main():
    """主函数"""
    print("正在启动SimpleTrade简单Web前端...")

    # 检查requests库是否安装
    try:
        import requests
    except ImportError:
        print("缺少依赖: requests")
        print("正在安装requests...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
            print("requests安装成功")
        except subprocess.CalledProcessError as e:
            print(f"安装requests失败: {e}")
            print("请手动安装requests: pip install requests")
            return

    # 启动API服务器
    api_process = start_api_server()
    if api_process is None:
        print("启动API服务器失败，无法继续")
        return

    # 打开简单的HTML页面
    simple_html_path = os.path.join(ROOT_DIR, "web-frontend", "public", "simple.html")
    if not os.path.exists(simple_html_path):
        print(f"错误: 简单HTML页面不存在: {simple_html_path}")
        api_process.terminate()
        print("已停止API服务器")
        return

    # 打开浏览器
    try:
        print("正在打开浏览器...")
        webbrowser.open(f"file://{simple_html_path}")
    except Exception as e:
        print(f"打开浏览器失败: {e}")
        print(f"请手动打开文件: {simple_html_path}")

    print("\n=== SimpleTrade 简单Web前端已启动 ===")
    print("API服务器地址: http://localhost:8000")
    print("API文档地址: http://localhost:8000/docs")
    print(f"简单HTML页面: file://{simple_html_path}")
    print("按Ctrl+C停止服务\n")

    try:
        # 等待用户按Ctrl+C
        while True:
            # 检查API服务器进程是否还在运行
            if api_process.poll() is not None:
                stdout, stderr = api_process.communicate()
                print("API服务器已经结束，退出码:", api_process.returncode)
                if api_process.returncode != 0:
                    print("API服务器异常退出，错误信息:")
                    print(stderr)
                break

            time.sleep(1)
    except KeyboardInterrupt:
        print("\n接收到Ctrl+C，正在停止服务...")
        api_process.terminate()

    print("服务已停止")

if __name__ == "__main__":
    main()
