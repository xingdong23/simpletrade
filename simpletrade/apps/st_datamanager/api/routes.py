"""
SimpleTrade数据管理API路由

定义数据管理的RESTful API路由。
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
import os
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, Query, Path, Body, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field

# 导入vnpy相关模块
# Revert to standard vnpy imports
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData as VnpyBarData # Rename to avoid conflict
# # Ensure consistent vnpy import path (should be vnpy.vnpy.*)
# # from vnpy.vnpy.trader.constant import Exchange, Interval
# # from vnpy.vnpy.trader.object import BarData as VnpyBarData # Rename to avoid conflict
# # try:
# #     from vnpy.trader.constant import Exchange, Interval

import logging
import traceback

from simpletrade.apps.st_datamanager import STDataManagerApp # 导入 App 类

# 创建路由器
router = APIRouter(prefix="/api/data", tags=["data"])

# 设置日志
logger = logging.getLogger("simpletrade.apps.st_datamanager.api")

# 数据模型
class ApiResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None

class BarData(BaseModel):
    """K线数据模型"""
    datetime: str
    open_price: float # Field(..., alias="open")
    high_price: float # Field(..., alias="high")
    low_price: float # Field(..., alias="low")
    close_price: float # Field(..., alias="close")
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

class ImportCsvRequestParams(BaseModel):
    """CSV导入请求参数模型 (for query/form data)"""
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

class ImportQlibRequest(BaseModel):
    """导入Qlib数据请求模型"""
    qlib_dir: str
    symbol: str
    exchange: str
    interval: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ExportRequest(BaseModel):
    """导出请求模型"""
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: str
    file_path: str

# 依赖注入：获取数据管理引擎
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 设置为DEBUG级别

def get_data_manager_engine():
    """获取数据管理引擎"""
    # 这里需要从全局获取引擎实例
    # 实际实现时需要根据SimpleTrade的架构调整
    from simpletrade.main import main_engine
    # 使用 App 类的 __name__ 属性来获取实例
    # engine_instance = main_engine.get_engine(STDataManagerApp.__name__)
    # 使用 app_name 属性来获取实例
    engine_instance = main_engine.get_engine(STDataManagerApp.app_name)
    logger.info(f"get_data_manager_engine called. Requested engine name: {STDataManagerApp.app_name}, got instance: {engine_instance}") # 更新日志
    return engine_instance

# API路由
@router.get("/symbols", response_model=ApiResponse)
async def get_symbols():
    """获取可用的交易品种列表"""
    logger.info("Entering get_symbols endpoint")
    try:
        # 从数据库获取交易品种
        from simpletrade.config.database import get_db
        from simpletrade.models.database import Symbol

        db = next(get_db())  # 获取数据库会话
        try:
            db_symbols = db.query(Symbol).filter(Symbol.is_active == True).all()

            # 如果数据库中没有数据，返回测试数据
            if not db_symbols:
                logger.warning("No symbols found in database, returning test data")
                symbols = [
                    {"symbol": "AAPL", "exchange": "SMART", "name": "Apple Inc.", "category": "Stock"},
                    {"symbol": "MSFT", "exchange": "SMART", "name": "Microsoft Corporation", "category": "Stock"},
                    {"symbol": "GOOG", "exchange": "SMART", "name": "Alphabet Inc.", "category": "Stock"},
                    {"symbol": "AMZN", "exchange": "SMART", "name": "Amazon.com, Inc.", "category": "Stock"},
                    {"symbol": "FB", "exchange": "SMART", "name": "Meta Platforms, Inc.", "category": "Stock"}
                ]
            else:
                # 将数据库对象转换为字典
                symbols = [
                    {
                        "symbol": s.symbol,
                        "exchange": s.exchange,
                        "name": s.name,
                        "category": s.category
                    } for s in db_symbols
                ]
        finally:
            db.close()  # 确保关闭会话

        return {
            "success": True,
            "message": f"获取交易品种成功，共 {len(symbols)} 个",
            "data": symbols
        }
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        return {
            "success": False,
            "message": f"获取交易品种失败: {str(e)}"
        }

@router.get("/overview", response_model=ApiResponse)
async def get_data_overview(
    engine = Depends(get_data_manager_engine) # 启用依赖注入
):
    """获取数据概览"""
    logger.info(f"Entering st_datamanager get_data_overview") # 更新日志信息
    if not engine:
        logger.error("Dependency injection returned None for engine!")
        raise HTTPException(status_code=500, detail="Data manager engine not available.")
    try:
        # 直接调用引擎的 get_available_data 方法获取合并后的概览
        logger.info(f"Calling engine.get_available_data() on {engine}...")
        available_data = engine.get_available_data()
        logger.info(f"Available data received: {len(available_data)}")

        # get_available_data 返回的已经是 Dict 列表，可以直接使用
        logger.info("数据概览获取完成，准备返回响应.")
        return {
            "success": True,
            "message": "获取数据概览成功", # 更新成功消息
            "data": available_data # 返回引擎处理好的数据
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

        # 加载数据
        bars: List[VnpyBarData] = engine.get_bar_data(
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
            "message": f"获取K线数据成功，共 {len(bars)} 条",
            "data": result
        }
    except ValueError as ve:
        logger.error(f"Invalid parameter value: {ve}")
        raise HTTPException(status_code=400, detail=f"Invalid parameter value: {ve}")
    except Exception as e:
        logger.error(f"Error getting bars: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="获取K线数据时发生错误")

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
        logger.error(f"Error downloading data: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="下载数据时发生错误")

@router.post("/import/csv", response_model=ApiResponse)
async def import_data_from_csv_upload(
    params: ImportCsvRequestParams = Depends(), # Use Depends for form data or query params
    file: UploadFile = File(...),
    engine = Depends(get_data_manager_engine)
):
    """通过上传CSV文件导入K线数据"""
    if not engine:
        logger.error("Data manager engine not available via dependency injection.")
        raise HTTPException(status_code=500, detail="数据管理引擎不可用")

    # Create a temporary file to store the uploaded content
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            temp_file_path = tmp_file.name
        logger.info(f"Uploaded CSV file saved temporarily to: {temp_file_path}")

        # Parse parameters
        try:
            exchange_obj = Exchange(params.exchange)
            interval_obj = Interval(params.interval)
        except ValueError as e:
            logger.error(f"Invalid exchange or interval: {e}")
            raise HTTPException(status_code=400, detail=f"无效的交易所或周期: {e}")

        # Call the engine's import function with the temporary file path
        success, message = engine.import_data_from_csv(
            file_path=temp_file_path,
            symbol=params.symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            datetime_head=params.datetime_head,
            open_head=params.open_head,
            high_head=params.high_head,
            low_head=params.low_head,
            close_head=params.close_head,
            volume_head=params.volume_head,
            open_interest_head=params.open_interest_head,
            datetime_format=params.datetime_format
        )

        return {
            "success": success,
            "message": message
        }

    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        traceback.print_exc()
        # Ensure detail message is helpful but avoids leaking sensitive info
        error_detail = f"导入CSV文件时发生错误: {type(e).__name__}"
        if isinstance(e, FileNotFoundError):
            error_detail = "处理上传文件时出错"
        elif isinstance(e, HTTPException):
            error_detail = e.detail # Propagate specific HTTP errors
        # Add more specific error handling if needed
        raise HTTPException(status_code=500, detail=error_detail)
    finally:
        # Clean up the temporary file
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Temporary file {temp_file_path} removed.")
            except Exception as cleanup_error:
                logger.error(f"Error removing temporary file {temp_file_path}: {cleanup_error}")
        # Ensure the uploaded file resource is closed
        if file:
            await file.close()

@router.post("/import/qlib", response_model=ApiResponse)
async def import_qlib_data(
    request: ImportQlibRequest,
    engine = Depends(get_data_manager_engine)
):
    """导入Qlib格式数据"""
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)
        interval_obj = Interval(request.interval)

        # 解析日期
        start_date = None
        end_date = None
        if request.start_date:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        if request.end_date:
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d")

        # 导入数据
        success, msg = engine.import_data_from_qlib(
            qlib_dir=request.qlib_dir,
            symbol=request.symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "success": success,
            "message": msg
        }
    except Exception as e:
        logger.error(f"Error importing Qlib data: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="导入Qlib数据时发生错误")

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
        logger.error(f"Error exporting data: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="导出数据时发生错误")

@router.delete("/bar/{exchange}/{symbol}/{interval}", response_model=ApiResponse)
async def delete_bar_data(
    exchange: str = Path(..., title="交易所"),
    symbol: str = Path(..., title="代码"),
    interval: str = Path(..., title="周期"),
    engine = Depends(get_data_manager_engine)
):
    """删除指定的K线数据"""
    if not engine:
        logger.error("Data manager engine not available.")
        raise HTTPException(status_code=500, detail="数据管理引擎不可用")
    try:
        exchange_obj = Exchange(exchange)
        interval_obj = Interval(interval)
    except ValueError as e:
        logger.error(f"Invalid exchange or interval: {e}")
        raise HTTPException(status_code=400, detail=f"无效的交易所或周期: {e}")

    try:
        success, message = engine.delete_bar_data(
            symbol=symbol,
            exchange=exchange_obj,
            interval=interval_obj
        )
        return {"success": success, "message": message}
    except Exception as e:
        logger.error(f"Error deleting bar data: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="删除K线数据时发生错误")

@router.delete("/tick/{exchange}/{symbol}", response_model=ApiResponse)
async def delete_tick_data(
    exchange: str = Path(..., title="交易所"),
    symbol: str = Path(..., title="代码"),
    engine = Depends(get_data_manager_engine)
):
    """删除指定的Tick数据"""
    if not engine:
        logger.error("Data manager engine not available.")
        raise HTTPException(status_code=500, detail="数据管理引擎不可用")
    try:
        exchange_obj = Exchange(exchange)
    except ValueError as e:
        logger.error(f"Invalid exchange: {e}")
        raise HTTPException(status_code=400, detail=f"无效的交易所: {e}")

    try:
        success, message = engine.delete_tick_data(
            symbol=symbol,
            exchange=exchange_obj
        )
        return {"success": success, "message": message}
    except Exception as e:
        logger.error(f"Error deleting tick data: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="删除Tick数据时发生错误")
