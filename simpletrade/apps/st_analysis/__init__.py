"""
SimpleTrade分析应用

提供数据分析功能，包括技术指标计算、策略回测和可视化分析。
"""

from pathlib import Path

from simpletrade.core.app import STBaseApp
from .engine import STAnalysisEngine

APP_NAME = "st_analysis"

class STAnalysisApp(STBaseApp):
    """SimpleTrade分析应用"""

    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "ST分析"
    engine_class = STAnalysisEngine
    widget_class = None  # 不需要图形界面
