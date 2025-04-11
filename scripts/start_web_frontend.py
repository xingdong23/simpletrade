#!/usr/bin/env python
"""
启动Web前端

启动SimpleTrade的Web前端和后端API服务。
"""

import sys
import os
import subprocess
import time
from pathlib import Path
import webbrowser

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

def start_api_server():
    """启动API服务器"""
    print("正在启动API服务器...")

    try:
        # 创建一个新的进程来运行API服务器
        api_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "simpletrade.api.server:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 等待API服务器启动
        time.sleep(2)

        # 检查进程是否还在运行
        if api_process.poll() is not None:
            # 进程已经结束，读取错误信息
            _, stderr = api_process.communicate()
            print(f"启动API服务器失败: {stderr.decode('utf-8')}")
            return None

        print("API服务器启动成功，访问 http://localhost:8000/docs 查看API文档")
        return api_process
    except Exception as e:
        print(f"启动API服务器失败: {e}")
        return None

def start_web_frontend():
    """启动Web前端"""
    print("正在启动Web前端...")

    # 检查是否安装了Node.js
    try:
        subprocess.run(["node", "--version"], check=True, stdout=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未安装Node.js，请先安装Node.js")
        return None

    # 检查是否安装了npm
    try:
        subprocess.run(["npm", "--version"], check=True, stdout=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未安装npm，请先安装npm")
        return None

    # 检查是否安装了依赖
    if not os.path.exists(os.path.join(ROOT_DIR, "web-frontend", "node_modules")):
        print("正在安装Web前端依赖...")
        try:
            # 尝试使用cnpm安装依赖（国内镜像）
            try:
                subprocess.run(["cnpm", "--version"], check=True, stdout=subprocess.PIPE)
                print("使用cnpm安装依赖...")
                subprocess.run(["cnpm", "install"], cwd=os.path.join(ROOT_DIR, "web-frontend"), check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 如果没有cnpm，则使用npm
                print("使用npm安装依赖...")
                subprocess.run(["npm", "install"], cwd=os.path.join(ROOT_DIR, "web-frontend"), check=True)
        except subprocess.CalledProcessError as e:
            print(f"安装依赖失败: {e}")
            print("请手动安装依赖: cd web-frontend && npm install")
            return None

    # 创建简单的package.json文件（如果不存在）
    package_json_path = os.path.join(ROOT_DIR, "web-frontend", "package.json")
    if not os.path.exists(package_json_path):
        print("创建简单的package.json文件...")
        with open(package_json_path, "w") as f:
            f.write('{\n  "name": "simpletrade-web",\n  "version": "0.1.0",\n  "private": true,\n  "scripts": {\n    "serve": "vue-cli-service serve"\n  }\n}')

    # 启动Web前端
    try:
        web_process = subprocess.Popen(
            ["npm", "run", "serve"],
            cwd=os.path.join(ROOT_DIR, "web-frontend")
        )
        print("Web前端启动成功，访问 http://localhost:8080 查看前端界面")
        return web_process
    except Exception as e:
        print(f"启动Web前端失败: {e}")
        return None

    # 等待Web前端启动
    time.sleep(5)

    return web_process

def main():
    """主函数"""
    print("正在启动SimpleTrade Web前端...")

    # 启动API服务器
    api_process = start_api_server()
    if api_process is None:
        print("启动API服务器失败，无法继续")
        return

    # 启动Web前端
    web_process = start_web_frontend()
    if web_process is None:
        print("启动Web前端失败")
        api_process.terminate()
        print("已停止API服务器")
        return

    # 等待一下，确保Web前端已经启动
    time.sleep(5)

    # 打开浏览器
    try:
        webbrowser.open("http://localhost:8080")
    except Exception as e:
        print(f"打开浏览器失败: {e}")
        print("请手动访问 http://localhost:8080")

    print("SimpleTrade Web前端已启动")
    print("API服务器地址: http://localhost:8000")
    print("Web前端地址: http://localhost:8080")
    print("按Ctrl+C停止服务")

    try:
        # 等待用户按Ctrl+C
        while True:
            # 检查进程是否还在运行
            if api_process.poll() is not None:
                print("API服务器已经结束，正在停止Web前端...")
                web_process.terminate()
                break

            if web_process.poll() is not None:
                print("Web前端已经结束，正在停止API服务器...")
                api_process.terminate()
                break

            time.sleep(1)
    except KeyboardInterrupt:
        print("正在停止服务...")
        api_process.terminate()
        web_process.terminate()

    print("服务已停止")

if __name__ == "__main__":
    main()
