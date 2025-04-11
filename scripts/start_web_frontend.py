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
            [sys.executable, "-m", "uvicorn", "simpletrade.api.server:app", "--host", "0.0.0.0", "--port", "8000"],
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

def start_web_frontend():
    """启动Web前端"""
    print("正在启动Web前端...")

    # 检查是否安装了Node.js
    try:
        node_version = subprocess.run(["node", "--version"], check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
        print(f"Node.js版本: {node_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未安装Node.js，请先安装Node.js")
        return None

    # 检查是否安装了npm
    try:
        npm_version = subprocess.run(["npm", "--version"], check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
        print(f"npm版本: {npm_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未安装npm，请先安装npm")
        return None

    # 检查web-frontend目录是否存在
    web_frontend_dir = os.path.join(ROOT_DIR, "web-frontend")
    if not os.path.exists(web_frontend_dir):
        print(f"错误: web-frontend目录不存在: {web_frontend_dir}")
        return None

    # 检查package.json文件是否存在
    package_json_path = os.path.join(web_frontend_dir, "package.json")
    if not os.path.exists(package_json_path):
        print("创建简单的package.json文件...")
        with open(package_json_path, "w") as f:
            f.write('{\n  "name": "simpletrade-web",\n  "version": "0.1.0",\n  "private": true,\n  "scripts": {\n    "serve": "vue-cli-service serve"\n  }\n}')

    # 检查是否安装了依赖
    if not os.path.exists(os.path.join(web_frontend_dir, "node_modules")):
        print("正在安装Web前端依赖...")
        try:
            # 尝试使用cnpm安装依赖（国内镜像）
            try:
                cnpm_version = subprocess.run(["cnpm", "--version"], check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
                print(f"cnpm版本: {cnpm_version}")
                print("使用cnpm安装依赖...")
                subprocess.run(["cnpm", "install"], cwd=web_frontend_dir, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 如果没有cnpm，则尝试安装cnpm
                print("cnpm未安装，尝试安装cnpm...")
                try:
                    subprocess.run(["npm", "install", "-g", "cnpm", "--registry=https://registry.npmmirror.com"], check=True)
                    print("cnpm安装成功，使用cnpm安装依赖...")
                    subprocess.run(["cnpm", "install"], cwd=web_frontend_dir, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"安装cnpm失败: {e}")
                    print("使用npm安装依赖...")
                    # 使用国内镜像
                    subprocess.run(["npm", "install", "--registry=https://registry.npmmirror.com"], cwd=web_frontend_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"安装依赖失败: {e}")
            print("请手动安装依赖: cd web-frontend && npm install --registry=https://registry.npmmirror.com")
            return None

    # 启动Web前端
    try:
        print("正在启动Web前端服务...")
        web_process = subprocess.Popen(
            ["npm", "run", "serve"],
            cwd=web_frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 等待Web前端启动
        print("等待Web前端启动...")
        start_time = time.time()
        max_wait_time = 30  # 最多等待30秒

        while time.time() - start_time < max_wait_time:
            # 检查进程是否还在运行
            if web_process.poll() is not None:
                # 进程已经结束，读取错误信息
                stdout, stderr = web_process.communicate()
                print(f"启动Web前端失败，进程已退出，退出码: {web_process.returncode}")
                print(f"标准输出: {stdout}")
                print(f"错误输出: {stderr}")
                return None

            # 尝试连接Web前端
            try:
                import requests
                response = requests.get("http://localhost:8080", timeout=0.5)
                if response.status_code == 200:
                    print("Web前端启动成功，访问 http://localhost:8080 查看前端界面")
                    return web_process
            except Exception:
                # 连接失败，继续等待
                pass

            time.sleep(0.5)

        # 如果超时但进程仍在运行，假设服务器已经启动
        if web_process.poll() is None:
            print("Web前端似乎已经启动，但无法确认。访问 http://localhost:8080 查看前端界面")
            return web_process
        else:
            # 进程已经结束，读取错误信息
            stdout, stderr = web_process.communicate()
            print(f"启动Web前端失败，进程已退出，退出码: {web_process.returncode}")
            print(f"标准输出: {stdout}")
            print(f"错误输出: {stderr}")
            return None
    except Exception as e:
        print(f"启动Web前端失败: {e}")
        return None

def main():
    """主函数"""
    print("正在启动SimpleTrade Web前端...")

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

    # 启动Web前端
    web_process = start_web_frontend()
    if web_process is None:
        print("启动Web前端失败")
        api_process.terminate()
        print("已停止API服务器")
        return

    # 打开浏览器
    try:
        print("正在打开浏览器...")
        webbrowser.open("http://localhost:8080")
    except Exception as e:
        print(f"打开浏览器失败: {e}")
        print("请手动访问 http://localhost:8080")

    print("\n=== SimpleTrade Web前端已启动 ===")
    print("API服务器地址: http://localhost:8000")
    print("API文档地址: http://localhost:8000/docs")
    print("Web前端地址: http://localhost:8080")
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
                print("正在停止Web前端...")
                web_process.terminate()
                break

            # 检查Web前端进程是否还在运行
            if web_process.poll() is not None:
                stdout, stderr = web_process.communicate()
                print("Web前端已经结束，退出码:", web_process.returncode)
                if web_process.returncode != 0:
                    print("Web前端异常退出，错误信息:")
                    print(stderr)
                print("正在停止API服务器...")
                api_process.terminate()
                break

            time.sleep(1)
    except KeyboardInterrupt:
        print("\n接收到Ctrl+C，正在停止服务...")
        api_process.terminate()
        web_process.terminate()

    print("服务已停止")

if __name__ == "__main__":
    main()
