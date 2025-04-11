"""
SimpleTrade数据管理API

提供数据管理功能的RESTful API接口。
直接使用vnpy的数据模型和数据管理功能。
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from fastapi import APIRouter, Query, Path, Body, HTTPException, Depends
from pydantic import BaseModel, Field

# 导入vnpy的数据模型和数据管理功能
from vnpy.trader.object import BarData, TickData
from vnpy.trader.constant import Exchange, Interval

# 导入我们的数据管理器
from simpletrade.core.data import DataManager

# 创建数据管理器实例
data_manager = DataManager()

# 配置日志记录
import logging
import traceback # 导入 traceback 模块
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/data", tags=["data"])

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

class DownloadRequestModel(BaseModel):
    """下载请求模型"""
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: Optional[str] = None

class ImportRequestModel(BaseModel):
    """导入请求模型"""
    file_path: str
    symbol: str
    exchange: str
    interval: str
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    datetime_column: str = "datetime"
    open_column: str = "open"
    high_column: str = "high"
    low_column: str = "low"
    close_column: str = "close"
    volume_column: str = "volume"
    open_interest_column: str = "open_interest"

class ExportRequestModel(BaseModel):
    """导出请求模型"""
    file_path: str
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: str

class DeleteRequestModel(BaseModel):
    """删除请求模型"""
    symbol: str
    exchange: str
    interval: Optional[str] = None

class ApiResponseModel(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None

# API路由
@router.get("/symbols", response_model=ApiResponseModel)
async def get_symbols():
    """获取交易品种列表"""
    try:
        # 直接返回一些示例交易品种
        # 由于数据库可能为空，我们返回一些示例数据
        result = [
            {"symbol": "AAPL", "exchange": "SMART"},
            {"symbol": "MSFT", "exchange": "SMART"},
            {"symbol": "GOOG", "exchange": "SMART"},
            {"symbol": "AMZN", "exchange": "SMART"},
            {"symbol": "FB", "exchange": "SMART"},
            {"symbol": "BABA", "exchange": "SMART"},
            {"symbol": "TSLA", "exchange": "SMART"},
            {"symbol": "BTC", "exchange": "BINANCE"},
            {"symbol": "ETH", "exchange": "BINANCE"},
            {"symbol": "IF2306", "exchange": "CFFEX"}
        ]

        return {
            "success": True,
            "message": f"获取交易品种列表成功，共 {len(result)} 个",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取交易品种列表失败: {str(e)}"
        }

@router.get("/overview", response_model=ApiResponseModel)
async def get_data_overview():
    """获取数据概览"""
    logger.info("Entering get_data_overview function...")
    try:
        logger.info("获取数据概览请求开始...")
        
        # 获取K线数据概览
        logger.info("正在获取K线数据概览...")
        bar_overviews = data_manager.get_bar_overview()
        logger.info(f"获取K线数据概览完成，共 {len(bar_overviews)} 条.")

        # 获取Tick数据概览
        logger.info("正在获取Tick数据概览...")
        tick_overviews = data_manager.get_tick_overview()
        logger.info(f"获取Tick数据概览完成，共 {len(tick_overviews)} 条.")

        # 转换为API模型
        result = []

        for overview in bar_overviews:
            result.append({
                "symbol": overview.symbol,
                "exchange": overview.exchange.value,
                "interval": overview.interval.value,
                "count": overview.count,
                "start": overview.start.strftime("%Y-%m-%d %H:%M:%S"),
                "end": overview.end.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "bar"
            })

        for overview in tick_overviews:
            result.append({
                "symbol": overview.symbol,
                "exchange": overview.exchange.value,
                "count": overview.count,
                "start": overview.start.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "end": overview.end.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "type": "tick"
            })
        
        logger.info("数据概览转换完成，准备返回响应.")
        return {
            "success": True,
            "message": "获取数据概览成功",
            "data": result
        }
    except Exception as e:
        # 记录详细的错误信息和堆栈跟踪
        logger.error(f"获取数据概览时捕获到异常: {e}") # 使用 logger.error
        traceback.print_exc() # 强制打印堆栈信息到 stderr
        # 重新抛出异常，让 FastAPI 的默认错误处理也能捕获并可能记录（可选）
        # raise e 
        # 或者直接返回错误响应
        return {
            "success": False,
            # 返回更通用的错误信息给前端，避免泄露过多细节
            "message": "获取数据概览失败，服务器内部错误。"
        }

@router.get("/bars", response_model=ApiResponseModel)
async def get_bars(
    symbol: str,
    exchange: str,
    interval: str,
    start_date: str,
    end_date: Optional[str] = None
):
    """获取K线数据"""
    try:
        # 解析参数
        exchange_obj = Exchange(exchange)
        interval_obj = Interval(interval)
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.now()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")

        # 查询数据
        bars = data_manager.load_bar_data(
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

@router.get("/ticks", response_model=ApiResponseModel)
async def get_ticks(
    symbol: str,
    exchange: str,
    start_date: str,
    end_date: Optional[str] = None
):
    """获取Tick数据"""
    try:
        # 解析参数
        exchange_obj = Exchange(exchange)
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.now()
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")

        # 查询数据
        ticks = data_manager.load_tick_data(
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

@router.post("/import", response_model=ApiResponseModel)
async def import_data(request: ImportRequestModel):
    """导入数据"""
    try:
        # 导入数据
        success, msg, count = data_manager.import_bar_data_from_csv(
            file_path=request.file_path,
            symbol=request.symbol,
            exchange=request.exchange,
            interval=request.interval,
            datetime_format=request.datetime_format,
            datetime_column=request.datetime_column,
            open_column=request.open_column,
            high_column=request.high_column,
            low_column=request.low_column,
            close_column=request.close_column,
            volume_column=request.volume_column,
            open_interest_column=request.open_interest_column
        )

        return {
            "success": success,
            "message": msg,
            "data": {"count": count}
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"导入数据失败: {str(e)}"
        }

@router.post("/export", response_model=ApiResponseModel)
async def export_data(request: ExportRequestModel):
    """导出数据"""
    try:
        # 解析参数
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")

        # 导出数据
        success, msg, count = data_manager.export_bar_data_to_csv(
            file_path=request.file_path,
            symbol=request.symbol,
            exchange=request.exchange,
            interval=request.interval,
            start=start,
            end=end
        )

        return {
            "success": success,
            "message": msg,
            "data": {"count": count}
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"导出数据失败: {str(e)}"
        }

@router.post("/delete", response_model=ApiResponseModel)
async def delete_data(request: DeleteRequestModel):
    """删除数据"""
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)

        # 删除数据
        if request.interval:
            interval_obj = Interval(request.interval)
            count = data_manager.delete_bar_data(
                symbol=request.symbol,
                exchange=exchange_obj,
                interval=interval_obj
            )
            return {
                "success": True,
                "message": f"成功删除 {count} 条K线数据",
                "data": {"count": count}
            }
        else:
            count = data_manager.delete_tick_data(
                symbol=request.symbol,
                exchange=exchange_obj
            )
            return {
                "success": True,
                "message": f"成功删除 {count} 条Tick数据",
                "data": {"count": count}
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"删除数据失败: {str(e)}"
        }
