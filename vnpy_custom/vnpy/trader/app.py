"""
应用模块基类
"""

from abc import ABC
from pathlib import Path
from typing import Dict, List, Optional, Callable

class BaseApp(ABC):
    """应用模块基类"""
    
    app_name: str = ""
    app_module: str = ""
    app_path: Path = None
    display_name: str = ""
    engine_class: type = None
    widget_name: str = ""
    icon_name: str = ""
