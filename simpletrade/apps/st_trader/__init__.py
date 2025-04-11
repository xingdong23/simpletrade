"""
SimpleTrade交易增强应用

提供交易功能的增强，包括订单管理、持仓管理等。
"""

from pathlib import Path

from simpletrade.core.app import STBaseApp
from .engine import STTraderEngine
from .widget import STTraderWidget

APP_NAME = "st_trader"

class STTraderApp(STBaseApp):
    """SimpleTrade交易增强应用"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "ST交易增强"
    engine_class = STTraderEngine
    widget_class = STTraderWidget
