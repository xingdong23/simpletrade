"""
SimpleTrade消息系统应用

提供消息处理功能，支持通过消息指令控制系统。
"""

from pathlib import Path

from simpletrade.core.app import STBaseApp
from .engine import STMessageEngine

APP_NAME = "st_message"

class STMessageApp(STBaseApp):
    """SimpleTrade消息系统应用"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "ST消息系统"
    engine_class = STMessageEngine
    widget_class = None  # 不需要图形界面
