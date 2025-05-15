"""
CTA策略模块
"""

from pathlib import Path

from vnpy.trader.app import BaseApp
from vnpy.trader.constant import Direction
from vnpy.trader.object import TickData, BarData, TradeData, OrderData
from vnpy.trader.utility import BarGenerator, ArrayManager

from .base import (
    APP_NAME,
    StopOrder,
    StopOrderStatus,
    EngineType,
    STOPORDER_PREFIX,
    CtaTemplate,
    CtaSignal,
    TargetPosTemplate
)
from .engine import CtaEngine
from .backtesting import BacktestingEngine, OptimizationSetting

class CtaStrategyApp(BaseApp):
    """CTA策略应用"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "CTA策略"
    engine_class = CtaEngine
    widget_name = "CtaManager"
    icon_name = "cta.ico"
