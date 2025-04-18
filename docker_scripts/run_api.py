import uvicorn
import logging
import sys
from pathlib import Path
import argparse
from fastapi import FastAPI # 导入 FastAPI

print("====== [run_api.py] Script Started ======") # DEBUG

# Add project root to sys.path to allow imports like simpletrade.core
project_root = Path(__file__).parent.parent # 因为脚本现在在 docker_scripts 下，所以需要 parent.parent
sys.path.insert(0, str(project_root))
print(f"====== [run_api.py] Project root added to sys.path: {project_root} ======") # DEBUG

# --- 创建 FastAPI 应用实例 (移到顶层) ---
app = FastAPI(title="SimpleTrade API", version="0.1.0")
print("====== [run_api.py] Top-level FastAPI app instance created ======") # DEBUG

# Configure logging (可以保留或移除)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
# print("====== [run_api.py] Logging configured ======")

# --- 尝试导入和初始化引擎 --- 
try:
    print("====== [run_api.py] Importing vnpy.event.EventEngine... ======") # DEBUG
    from vnpy.event import EventEngine
    print("====== [run_api.py] Importing simpletrade.core.engine.STMainEngine... ======") # DEBUG
    from simpletrade.core.engine import STMainEngine
    # 从 simpletrade.api.server 导入修改后的 configure_server 函数
    print("====== [run_api.py] Importing simpletrade.api.server.configure_server... ======") # DEBUG
    from simpletrade.api.server import configure_server 
    print("====== [run_api.py] Imports successful ======") # DEBUG

    # --- 初始化主引擎 (无 UI 依赖的关键部分) ---
    main_engine = None
    event_engine = None
    print("====== [run_api.py] Initializing EventEngine... ======") # DEBUG
    event_engine = EventEngine()
    print("====== [run_api.py] EventEngine initialized. ======") # DEBUG
    print("====== [run_api.py] Initializing STMainEngine (headless)... ======") # DEBUG
    main_engine = STMainEngine(event_engine)
    print("====== [run_api.py] Headless STMainEngine initialized successfully. ======") # DEBUG

    # --- 配置 FastAPI 应用 --- 
    print("====== [run_api.py] Configuring FastAPI server instance... ======") # DEBUG
    # 调用 configure_server 配置顶层的 app 实例
    configure_server(app=app, main_engine=main_engine, event_engine=event_engine) 
    print("====== [run_api.py] FastAPI server instance configured. ======") # DEBUG

except Exception as e:
    # 如果在导入、引擎初始化或服务器配置阶段出错，打印错误并退出
    print(f"====== [run_api.py] FATAL ERROR during setup: {e} ======")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)

# --- 解析命令行参数 (移到 setup 之后, uvicorn 启动之前) ---
parser = argparse.ArgumentParser(description="Run SimpleTrade API Server")
parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
# 添加 --reload-dir 参数
parser.add_argument("--reload-dir", type=str, default=None, help="Directory to watch for changes") 
args = parser.parse_args()
print(f"====== [run_api.py] Reload mode: {args.reload} ======") # DEBUG
print(f"====== [run_api.py] Reload directory: {args.reload_dir} ======") # DEBUG

# --- 启动 Uvicorn (现在应该在 try 块外部) ---
# 只有 setup 成功才会执行到这里
if __name__ == "__main__": # 添加 main guard
    print("====== [run_api.py] Starting Uvicorn server... ======") # DEBUG
    
    # 构建 uvicorn 参数字典
    uvicorn_params = {
        "host": "0.0.0.0",
        "port": 8003,
        "log_level": "info",
        "reload": args.reload
    }
    
    # 如果指定了 reload_dir，则添加到参数中
    if args.reload_dir:
        uvicorn_params["reload_dirs"] = [args.reload_dir]
        
    uvicorn.run(
        "docker_scripts.run_api:app", # <--- 修改导入字符串!
        **uvicorn_params # 使用解包传递参数
    )
    # Code below uvicorn.run() will likely not execute until server stops
    print("====== [run_api.py] Uvicorn finished (should not happen if running normally) ======") # DEBUG

# --- (旧的启动逻辑已移除或整合到上面) ---
# if main_engine:
#     try:
#         ...
#     except Exception as e:
#         ...
# else:
#     ... 