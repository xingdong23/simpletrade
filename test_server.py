import logging
import sys

# 配置日志
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stdout)])

# 尝试导入 vnpy_tiger
try:
    print("Attempting to import vnpy_tiger...")
    import vnpy_tiger
    print("vnpy_tiger imported successfully.")
except ImportError as e:
    print(f"Error importing vnpy_tiger: {e}")

# 导入 main 模块
try:
    print("Importing simpletrade.main...")
    from simpletrade.main import main_engine, event_engine
    print("simpletrade.main imported successfully.")
except Exception as e:
    print(f"Error importing simpletrade.main: {e}")
    import traceback
    traceback.print_exc()

# 启动 API 服务器
try:
    print("Starting API server...")
    from simpletrade.api.server import app
    print("API server created successfully.")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
except Exception as e:
    print(f"Error starting API server: {e}")
    import traceback
    traceback.print_exc()
