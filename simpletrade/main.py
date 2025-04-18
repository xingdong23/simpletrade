"""
SimpleTrade主程序入口

启动SimpleTrade交易平台。
"""

import sys
import os
import logging
from pathlib import Path

# --- Add vendors directory to sys.path ---
# This allows importing modules like vnpy_tiger located in the vendors directory.
project_root = Path(__file__).parent.parent.absolute()
vendors_path = project_root / "vendors"
if vendors_path.exists() and str(vendors_path) not in sys.path:
    sys.path.insert(0, str(vendors_path))
    print(f"[INFO] Added vendors path to sys.path: {vendors_path}")
# --- End sys.path modification ---

# --- Remove Debugging Imports and sys.path modifications ---
# # --- Remove Debugging Imports ---
# # try:
# #     import vnpy
# #     print(f\"[DEBUG] Successfully imported vnpy. Path: {vnpy.__path__}\")
# # except ImportError as e:
# #     print(f\"[DEBUG] Failed to import vnpy: {e}\")
# #     # Print sys.path here as well for early diagnosis
# #     print(\"[DEBUG] Current sys.path:\")
# #     for i, p in enumerate(sys.path):
# #         print(f\"  {i}: {p}\")
# # --- End Debugging Imports ---
# 
# # --- Add specific vendor paths to sys.path --- 
# project_root = str(Path(__file__).parent.parent.absolute())
# vendors_dir = os.path.join(project_root, 'vendors')
# 
# # Add the inner vnpy source directory
# vnpy_source_path = os.path.join(vendors_dir, 'vnpy', 'vnpy') 
# print(f\"[DEBUG] Calculated vnpy_source_path: {vnpy_source_path}\") # Debug path calc
# if os.path.exists(vnpy_source_path):
#     if vnpy_source_path not in sys.path:
#         sys.path.insert(0, vnpy_source_path)
#         print(f\"[DEBUG] Inserted {vnpy_source_path} into sys.path\")
#     else:
#         print(f\"[DEBUG] {vnpy_source_path} already in sys.path\")
# else:
#      print(f\"[DEBUG] ERROR: vnpy_source_path does NOT exist: {vnpy_source_path}\")
# 
# # Add vnpy_tiger path
# vnpy_tiger_path = os.path.join(vendors_dir, 'vnpy_tiger')
# if os.path.exists(vnpy_tiger_path):
#     if vnpy_tiger_path not in sys.path:
#         sys.path.insert(0, vnpy_tiger_path)
#         print(f\"[DEBUG] Inserted {vnpy_tiger_path} into sys.path\")
#     else:
#         print(f\"[DEBUG] {vnpy_tiger_path} already in sys.path\")
# else:
#     print(f\"[DEBUG] WARNING: vnpy_tiger_path does NOT exist: {vnpy_tiger_path}\")
# 
# print(\"[DEBUG] sys.path immediately BEFORE importing vnpy.event:\")
# for i, p in enumerate(sys.path):
#     print(f\"  {i}: {p}\")
# # --- End sys.path modification ---

# Use standard vnpy import 
from vnpy.event import EventEngine
# # Try importing vnpy.event
# try:
#     from vnpy.event import EventEngine
#     print(\"[DEBUG] Successfully imported EventEngine from vnpy.event\")
# except ImportError as e:
#     print(f\"[DEBUG] FAILED to import EventEngine from vnpy.event: {e}\")
#     print(\"[DEBUG] sys.path AT THE TIME OF FAILURE:\")
#     for i, p in enumerate(sys.path):
#         print(f\"  {i}: {p}\")
#     # Optionally re-raise or exit if needed
#     # raise e

# Continue with other imports...
from simpletrade.core.engine import STMainEngine

# 导入SimpleTrade应用
from simpletrade.apps.st_trader import STTraderApp
from simpletrade.apps.st_datamanager import STDataManagerApp
from simpletrade.apps.st_message import STMessageApp

# 导入外部模块
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 修改为DEBUG级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("simpletrade.main")

# Remove debug sys.path print
# # Display Python search paths (Remove this one, moved to earlier debug print)
# # logger.debug("Python search paths (in main.py):")
# # for i, path in enumerate(sys.path):
# #     logger.debug(f"  {i}: {path}")

try:
    from vnpy_datamanager import DataManagerApp
    logger.info("vnpy_datamanager imported successfully.")
except ImportError:
    logger.warning("Warning: vnpy_datamanager not found. Please install it first.")
    DataManagerApp = None

try:
    from vnpy_ib import IbGateway
    logger.info("vnpy_ib imported successfully.")
except ImportError:
    logger.warning("Warning: vnpy_ib not found. Please install it first.")
    IbGateway = None

try:
    logger.info("Attempting to import vnpy_tiger...")
    from vnpy_tiger import TigerGateway
    logger.info("vnpy_tiger imported successfully.")
except ImportError as e:
    logger.error(f"Warning: vnpy_tiger not found. Error: {e}")
    logger.warning("Please install it first.")
    TigerGateway = None

# --- 全局引擎实例 ---
# 创建事件引擎
event_engine = EventEngine()
logger.info("Global Event engine created.")

# 创建SimpleTrade主引擎
main_engine = STMainEngine(event_engine)
logger.info("Global Main engine created.")

# --- 全局 App 和 Gateway 注册 ---
logger.info("Registering gateways and apps globally...")
# 注册IB网关
if IbGateway:
    main_engine.add_gateway(IbGateway)
    logger.info("Global: IB Gateway registered.")

# 注册老虎证券网关
if TigerGateway:
    main_engine.add_gateway(TigerGateway)
    logger.info("Global: Tiger Gateway registered.")

    # 尝试连接老虎证券网关
    try:
        import json
        from pathlib import Path

        # 读取老虎证券配置文件
        tiger_config_path = Path.home().joinpath(".vnpy", "connect_tiger.json")
        if tiger_config_path.exists():
            with open(tiger_config_path, "r") as f:
                tiger_configs = json.load(f)
                if tiger_configs and isinstance(tiger_configs, list) and len(tiger_configs) > 0:
                    tiger_config = tiger_configs[0]
                    logger.info(f"Found Tiger config: {tiger_config['tiger_id']}, {tiger_config['account']}")

                    # 连接老虎证券网关
                    setting = {
                        "tiger_id": tiger_config["tiger_id"],
                        "account": tiger_config["account"],
                        "private_key": tiger_config["private_key"],
                        "server": "标准",  # 标准服务器
                        "language": "中文"   # 中文
                    }
                    main_engine.connect(setting, "TIGER")
                    logger.info("Tiger Gateway connected.")
        else:
            logger.warning(f"Tiger config file not found: {tiger_config_path}")
    except Exception as e:
        logger.error(f"Failed to connect Tiger Gateway: {e}")
else:
    logger.warning("Tiger Gateway not registered due to import failure.")

# 加载消息系统应用（先加载，便于其他应用注册消息处理器）
main_engine.add_app(STMessageApp)
logger.info("Global: ST Message app loaded.")

# 加载SimpleTrade应用
main_engine.add_app(STTraderApp)
logger.info("Global: ST Trader app loaded.")

# 加载ST数据管理应用
main_engine.add_app(STDataManagerApp)
logger.info("Global: ST Data Manager app loaded.")

# 加载原始数据管理应用（如果可用）
if DataManagerApp:
    main_engine.add_app(DataManagerApp)
    logger.info("Global: Original Data Manager app loaded.")

# 加载vnpy内置应用（按需选择）
try:
    main_engine.add_app("cta_strategy")  # CTA策略
    logger.info("Global: CTA Strategy app loaded.")
except Exception as e:
    logger.error(f"Global: Failed to load CTA Strategy app: {e}")
logger.info("Global registration complete.")
# --- 结束 全局 App 和 Gateway 注册 ---

def main():
    """SimpleTrade主程序入口 (主要用于非API模式或测试)"""
    logger.info("Starting SimpleTrade main function (non-API mode)...")

    # --- 使用全局引擎实例 ---
    # 引擎和 App 已在全局范围初始化和注册
    # --- 结束 使用全局引擎实例 ---

    logger.info("SimpleTrade main function setup complete! (Engine and apps already initialized)")

    # 保持主程序运行 (如果需要)
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down SimpleTrade...")
        main_engine.close()
        logger.info("SimpleTrade shutdown completed.")

    return main_engine, event_engine

if __name__ == "__main__":
    main()
