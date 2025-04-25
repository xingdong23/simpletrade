"""
SimpleTrade回测应用

提供策略回测功能。
"""

from pathlib import Path

from simpletrade.core.app import STBaseApp
from .engine import STBacktestEngine
from .service import BacktestService
from .ui import STBacktestWidget

APP_NAME = "st_backtest"

class STBacktestApp(STBaseApp):
    """SimpleTrade回测应用"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "ST回测"
    engine_class = STBacktestEngine
    widget_class = None  # 当前不需要图形界面 