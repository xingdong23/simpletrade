"""
SimpleTrade消息系统应用

提供消息处理功能，支持通过消息指令控制系统。
同时提供消息处理的基础接口，包括命令处理器和消息处理器的基类。
"""

from pathlib import Path

from simpletrade.core.app import STBaseApp
from .engine import STMessageEngine
from .base import CommandProcessor, MessageProcessor

APP_NAME = "st_message"

class STMessageApp(STBaseApp):
    """SimpleTrade消息系统应用"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "ST消息系统"
    engine_class = STMessageEngine
    widget_class = None  # 不需要图形界面

# 导出基础接口
__all__ = ["STMessageApp", "CommandProcessor", "MessageProcessor"]
