"""
SimpleTrade数据管理API路由

定义数据管理的RESTful API路由。
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Query, Path, Body, HTTPException, Depends
from pydantic import BaseModel, Field

from vnpy.trader.constant import Exchange, Interval

import logging
import traceback

from simpletrade.apps.st_datamanager import STDataManagerApp # 导入 App 类

# 创建路由器
router = APIRouter(prefix="/api/data", tags=["data"])

# 数据模型
class BarData(BaseModel):
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

class DataOverview(BaseModel):
    """数据概览模型"""
    symbol: str
    exchange: str
    interval: Optional[str] = None
    count: int
    start: str
    end: str
    type: str

class DownloadRequest(BaseModel):
    """下载请求模型"""
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: Optional[str] = None

class ImportRequest(BaseModel):
    """导入请求模型"""
    file_path: str
    symbol: str
    exchange: str
    interval: str
    datetime_head: str
    open_head: str
    high_head: str
    low_head: str
    close_head: str
    volume_head: str
    open_interest_head: str
    datetime_format: str = "%Y-%m-%d %H:%M:%S"

class ExportRequest(BaseModel):
    """导出请求模型"""
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: str
    file_path: str

class DeleteRequest(BaseModel):
    """删除请求模型"""
    symbol: str
    exchange: str
    interval: Optional[str] = None

class ApiResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None

# 依赖注入：获取数据管理引擎
logger = logging.getLogger(__name__)

def get_data_manager_engine():
    """获取数据管理引擎"""
    # 这里需要从全局获取引擎实例
    # 实际实现时需要根据SimpleTrade的架构调整
    from simpletrade.main import main_engine
    # 使用 App 类的 __name__ 属性来获取实例
    engine_instance = main_engine.get_engine(STDataManagerApp.__name__)
    logger.info(f"get_data_manager_engine called. Requested engine name: {STDataManagerApp.__name__}, got instance: {engine_instance}")
    return engine_instance

# API路由
@router.get("/overview", response_model=ApiResponse)
async def get_data_overview(
    # engine = Depends(get_data_manager_engine) # 暂时注释掉依赖注入
):
    """获取数据概览 - [调试模式：直接返回成功]"""
    logger.info(f"Entering st_datamanager get_data_overview [DEBUG MODE]")
    # logger.info(f"Engine instance: {engine}")
    # if not engine:
    #     logger.error("Dependency injection returned None for engine!")
    #     raise HTTPException(status_code=500, detail="Data manager engine not available.")
    try:
        # logger.info(f"Calling engine.get_available_data() on {engine}...")
        # data = engine.get_available_data()
        # logger.info(f"engine.get_available_data() returned: {data}")
        data = [] # 直接返回空列表
        logger.info("Returning empty data in debug mode.")
        return {
            "success": True,
            "message": "获取数据概览成功 (调试模式)",
            "data": data
        }
    except Exception as e:
        logger.error(f"Error in st_datamanager get_data_overview: {e}")
        traceback.print_exc() # 强制打印堆栈
        raise HTTPException(status_code=500, detail="获取数据概览时发生服务器内部错误。") # 返回通用错误信息

@router.get("/bars", response_model=ApiResponse)
async def get_bars(
    symbol: str,
    exchange: str,
    interval: str,
    start_date: str,
    end_date: Optional[str] = None,
    engine = Depends(get_data_manager_engine)
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
        
        # 获取数据
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
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/download", response_model=ApiResponse)
async def download_data(
    request: DownloadRequest,
    engine = Depends(get_data_manager_engine)
):
    """下载历史数据"""
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)
        interval_obj = Interval(request.interval)
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.now()
        if request.end_date:
            end = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        # 下载数据
        success = engine.download_bar_data(
            symbol=request.symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            start=start,
            end=end
        )
        
        if success:
            return {
                "success": True,
                "message": f"成功下载 {request.symbol}.{request.exchange} 的 {request.interval} 数据"
            }
        else:
            return {
                "success": False,
                "message": f"下载 {request.symbol}.{request.exchange} 的 {request.interval} 数据失败"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import", response_model=ApiResponse)
async def import_data(
    request: ImportRequest,
    engine = Depends(get_data_manager_engine)
):
    """导入数据"""
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)
        interval_obj = Interval(request.interval)
        
        # 导入数据
        success, msg = engine.import_data_from_csv(
            file_path=request.file_path,
            symbol=request.symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            datetime_head=request.datetime_head,
            open_head=request.open_head,
            high_head=request.high_head,
            low_head=request.low_head,
            close_head=request.close_head,
            volume_head=request.volume_head,
            open_interest_head=request.open_interest_head,
            datetime_format=request.datetime_format
        )
        
        return {
            "success": success,
            "message": msg
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export", response_model=ApiResponse)
async def export_data(
    request: ExportRequest,
    engine = Depends(get_data_manager_engine)
):
    """导出数据"""
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)
        interval_obj = Interval(request.interval)
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        # 导出数据
        success, msg = engine.export_data_to_csv(
            symbol=request.symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            start=start,
            end=end,
            file_path=request.file_path
        )
        
        return {
            "success": success,
            "message": msg
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete", response_model=ApiResponse)
async def delete_data(
    request: DeleteRequest,
    engine = Depends(get_data_manager_engine)
):
    """删除数据"""
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)
        
        # 删除数据
        if request.interval:
            interval_obj = Interval(request.interval)
            success, msg = engine.delete_bar_data(
                symbol=request.symbol,
                exchange=exchange_obj,
                interval=interval_obj
            )
        else:
            success, msg = engine.delete_tick_data(
                symbol=request.symbol,
                exchange=exchange_obj
            )
        
        return {
            "success": success,
            "message": msg
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
