"""
SimpleTrade数据管理应用

提供数据管理功能，包括数据下载、导入、导出、查看和管理。
扩展vnpy_datamanager，添加API接口和消息指令处理功能。
"""

from pathlib import Path

from simpletrade.core.app import STBaseApp
from .engine import STDataManagerEngine

APP_NAME = "st_datamanager"

class STDataManagerApp(STBaseApp):
    """SimpleTrade数据管理应用"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "ST数据管理"
    engine_class = STDataManagerEngine
    widget_class = None  # 不需要图形界面
