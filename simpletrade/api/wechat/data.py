"""
SimpleTrade微信小程序数据接口

提供微信小程序数据接口，用于数据查询和管理。
直接使用vnpy的数据模型和数据管理功能。
"""


# 添加vnpy源码路径
import sys
from pathlib import Path

# 添加vnpy源码目录到Python路径
VNPY_CUSTOM_DIR = Path(__file__).parent
while VNPY_CUSTOM_DIR.name != "simpletrade" and VNPY_CUSTOM_DIR != VNPY_CUSTOM_DIR.parent:
    VNPY_CUSTOM_DIR = VNPY_CUSTOM_DIR.parent
VNPY_CUSTOM_DIR = VNPY_CUSTOM_DIR.parent / "vnpy_custom"
if VNPY_CUSTOM_DIR.exists() and str(VNPY_CUSTOM_DIR) not in sys.path:
    sys.path.insert(0, str(VNPY_CUSTOM_DIR))
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field

# 导入vnpy的数据模型和数据管理功能
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval
# # Ensure consistent vnpy import path (should be vnpy.vnpy.*)
# # from vnpy.vnpy.trader.object import BarData, TickData
# # from vnpy.vnpy.trader.constant import Exchange, Interval
# # try:
# #     from vnpy.trader.object import BarData, TickData

# 导入我们的数据管理器和认证功能
# Remove import of deleted DataManager
# from simpletrade.core.data import DataManager
from .auth import get_current_user
# Import the engine getter for dependency injection
from simpletrade.apps.st_datamanager.api.routes import get_data_manager_engine

# 创建数据管理器实例
# data_manager = DataManager()
# Data manager engine will be injected via Depends

# 创建路由器
router = APIRouter(prefix="/api/wechat/data", tags=["wechat_data"])

# 数据模型
class BarDataModel(BaseModel):
    """K线数据模型"""
    datetime: str
    open: float = Field(..., alias="open_price")
    high: float = Field(..., alias="high_price")
    low: float = Field(..., alias="low_price")
    close: float = Field(..., alias="close_price")
    volume: float
    open_interest: float

    class Config:
        allow_population_by_field_name = True

class DataOverviewModel(BaseModel):
    """数据概览模型"""
    symbol: str
    exchange: str
    interval: Optional[str] = None
    count: int
    start: str
    end: str
    type: str

class ApiResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None

# API路由
@router.get("/overview", response_model=ApiResponse)
async def get_data_overview(
    current_user: dict = Depends(get_current_user),
    engine = Depends(get_data_manager_engine) # Inject engine
):
    """获取数据概览"""
    if not engine:
        raise HTTPException(status_code=500, detail="数据管理引擎不可用")
    try:
        # Use engine to get data overview
        available_data = engine.get_available_data()

        # # 获取K线数据概览 (Old logic, replaced by get_available_data)
        # bar_overviews = data_manager.get_bar_overview()
        # # 获取Tick数据概览
        # tick_overviews = data_manager.get_tick_overview()
        #
        # # 转换为API模型
        # result = []
        #
        # for overview in bar_overviews:
        #     result.append({
        #         "symbol": overview.symbol,
        #         "exchange": overview.exchange.value,
        #         "interval": overview.interval.value,
        #         "count": overview.count,
        #         "start": overview.start.strftime("%Y-%m-%d %H:%M:%S"),
        #         "end": overview.end.strftime("%Y-%m-%d %H:%M:%S"),
        #         "type": "bar"
        #     })
        #
        # for overview in tick_overviews:
        #     result.append({
        #         "symbol": overview.symbol,
        #         "exchange": overview.exchange.value,
        #         "count": overview.count,
        #         "start": overview.start.strftime("%Y-%m-%d %H:%M:%S.%f"),
        #         "end": overview.end.strftime("%Y-%m-%d %H:%M:%S.%f"),
        #         "type": "tick"
        #     })

        return {
            "success": True,
            "message": "获取数据概览成功",
            "data": available_data # Return data from engine
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取数据概览失败: {str(e)}"
        }

@router.get("/bars", response_model=ApiResponse)
async def get_bars(
    symbol: str,
    exchange: str,
    interval: str,
    start_date: str,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    engine = Depends(get_data_manager_engine) # Inject engine
):
    """获取K线数据"""
    if not engine:
        raise HTTPException(status_code=500, detail="数据管理引擎不可用")
    try:
        # 解析参数
        exchange_obj = Exchange(exchange)
        interval_obj = Interval(interval)
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.now()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")

        # 查询数据 (Use engine)
        bars = engine.get_bar_data(
            symbol=symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            start=start,
            end=end
        )

        # 转换为API模型
        result = []
        for bar in bars:
            result.append({
                "datetime": bar.datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "open_price": bar.open_price,
                "high_price": bar.high_price,
                "low_price": bar.low_price,
                "close_price": bar.close_price,
                "volume": bar.volume,
                "open_interest": bar.open_interest
            })

        return {
            "success": True,
            "message": f"获取K线数据成功，共 {len(result)} 条",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取K线数据失败: {str(e)}"
        }

@router.get("/ticks", response_model=ApiResponse)
async def get_ticks(
    symbol: str,
    exchange: str,
    start_date: str,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    engine = Depends(get_data_manager_engine) # Inject engine
):
    """获取Tick数据"""
    if not engine:
        raise HTTPException(status_code=500, detail="数据管理引擎不可用")
    try:
        # 解析参数
        exchange_obj = Exchange(exchange)
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.now()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")

        # 查询数据 (Use engine)
        ticks = engine.get_tick_data(
            symbol=symbol,
            exchange=exchange_obj,
            start=start,
            end=end
        )

        # 转换为API模型
        result = []
        for tick in ticks:
            result.append({
                "datetime": tick.datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "last_price": tick.last_price,
                "volume": tick.volume,
                "open_interest": tick.open_interest,
                "bid_price_1": tick.bid_price_1,
                "ask_price_1": tick.ask_price_1,
                "bid_volume_1": tick.bid_volume_1,
                "ask_volume_1": tick.ask_volume_1
            })

        return {
            "success": True,
            "message": f"获取Tick数据成功，共 {len(result)} 条",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取Tick数据失败: {str(e)}"
        }
