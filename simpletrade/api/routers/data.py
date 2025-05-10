"""
数据相关API路由定义
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from simpletrade.core.database import get_db
from simpletrade.models.database import DataImportLog, DbBarOverview
from simpletrade.api.schemas.common import ApiResponse
from simpletrade.api.schemas.data import DataRangeDetail

router = APIRouter(
    prefix="/api/data",
    tags=["data"],
)

logger = logging.getLogger(__name__)

@router.get("/available-symbols", response_model=ApiResponse)
async def get_available_symbols(
    exchange: Optional[str] = None,
    interval: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取系统中可用的合约代码列表
    
    Args:
        exchange: 可选，筛选特定交易所的合约
        interval: 可选，筛选特定周期的合约
        
    Returns:
        包含可用合约代码的响应对象
    """
    try:
        # 构建查询
        query = db.query(DataImportLog.symbol).distinct()
        
        # 根据参数筛选
        if exchange:
            query = query.filter(DataImportLog.exchange == exchange)
        if interval:
            query = query.filter(DataImportLog.interval == interval)
            
        # 获取所有唯一的合约代码
        symbols = [row[0] for row in query.all()]
        
        return {
            "success": True,
            "message": f"获取可用合约代码成功，共 {len(symbols)} 个",
            "data": symbols
        }
    except Exception as e:
        logger.error(f"获取可用合约代码失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取可用合约代码失败: {str(e)}")

@router.get("/available-exchanges", response_model=ApiResponse)
async def get_available_exchanges(
    symbol: Optional[str] = None,
    interval: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取系统中可用的交易所列表
    
    Args:
        symbol: 可选，筛选特定合约的交易所
        interval: 可选，筛选特定周期的交易所
        
    Returns:
        包含可用交易所的响应对象
    """
    try:
        # 构建查询
        query = db.query(DataImportLog.exchange).distinct()
        
        # 根据参数筛选
        if symbol:
            query = query.filter(DataImportLog.symbol == symbol)
        if interval:
            query = query.filter(DataImportLog.interval == interval)
            
        # 获取所有唯一的交易所
        exchanges = [row[0] for row in query.all()]
        
        return {
            "success": True,
            "message": f"获取可用交易所成功，共 {len(exchanges)} 个",
            "data": exchanges
        }
    except Exception as e:
        logger.error(f"获取可用交易所失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取可用交易所失败: {str(e)}")

@router.get("/available-intervals", response_model=ApiResponse)
async def get_available_intervals(
    symbol: Optional[str] = None,
    exchange: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取系统中可用的K线周期列表
    
    Args:
        symbol: 可选，筛选特定合约的周期
        exchange: 可选，筛选特定交易所的周期
        
    Returns:
        包含可用K线周期的响应对象
    """
    try:
        # 构建查询
        query = db.query(DataImportLog.interval).distinct()
        
        # 根据参数筛选
        if symbol:
            query = query.filter(DataImportLog.symbol == symbol)
        if exchange:
            query = query.filter(DataImportLog.exchange == exchange)
            
        # 获取所有唯一的K线周期
        intervals = [row[0] for row in query.all()]
        
        return {
            "success": True,
            "message": f"获取可用K线周期成功，共 {len(intervals)} 个",
            "data": intervals
        }
    except Exception as e:
        logger.error(f"获取可用K线周期失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取可用K线周期失败: {str(e)}")

@router.get("/available-data", response_model=ApiResponse)
async def get_available_data(db: Session = Depends(get_db)):
    """
    获取系统中所有可用的数据记录，包括合约、交易所和周期
    
    Returns:
        包含可用数据记录的响应对象
    """
    try:
        # 查询所有数据导入日志记录
        query = db.query(
            DataImportLog.symbol,
            DataImportLog.exchange,
            DataImportLog.interval,
            DataImportLog.last_begin_date,
            DataImportLog.last_end_date,
            DataImportLog.status
        )
        
        # 获取所有记录并格式化
        records = []
        for row in query.all():
            records.append({
                "symbol": row[0],
                "exchange": row[1],
                "interval": row[2],
                "start_date": row[3].isoformat() if row[3] else None,
                "end_date": row[4].isoformat() if row[4] else None,
                "status": row[5]
            })
        
        return {
            "success": True,
            "message": f"获取可用数据记录成功，共 {len(records)} 个",
            "data": records
        }
    except Exception as e:
        logger.error(f"获取可用数据记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取可用数据记录失败: {str(e)}") 

@router.get("/stock-data-range", response_model=ApiResponse[DataRangeDetail])
async def get_stock_data_range(
    symbol: str,
    exchange: str,
    interval: str,
    db: Session = Depends(get_db)
):
    logger.debug(f"API: get_stock_data_range called with symbol={symbol}, exchange={exchange}, interval={interval}")

    # Map frontend interval to backend interval if necessary
    db_interval = interval
    if interval == "1d":
        db_interval = "d"
    # Add other mappings if needed, e.g., "1h" -> "h"

    try:
        record = db.query(
            DbBarOverview.start,
            DbBarOverview.end,
            DbBarOverview.count
        ).filter(
            DbBarOverview.symbol == symbol,
            DbBarOverview.exchange == exchange,
            DbBarOverview.interval == db_interval # Use mapped interval
        ).first()

        if record:
            data_detail = DataRangeDetail(
                symbol=symbol,
                exchange=exchange,
                interval=interval, # Original interval for response
                start_date=record.start.date() if record.start else None, # Convert to date
                end_date=record.end.date() if record.end else None,     # Convert to date
                count=record.count,      # Use 'count' from DbBarOverview
                message="数据范围获取成功"
            )
            logger.debug(f"Data range found: {data_detail}")
            return ApiResponse(success=True, message="数据范围获取成功", data=data_detail)
        else:
            logger.warning(f"No data range record found for {symbol}, {exchange}, {db_interval}")
            data_detail = DataRangeDetail(
                symbol=symbol,
                exchange=exchange,
                interval=interval,
                count=0,
                message="未找到指定条件的数据记录"
            )
            return ApiResponse(success=True, message="未找到指定条件的数据记录", data=data_detail)

    except Exception as e:
        logger.error(f"Error querying stock data range for {symbol}, {exchange}, {interval}: {e}", exc_info=True)
        error_data_detail = DataRangeDetail(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            count=0,
            message=f"查询数据范围时发生服务器错误: {str(e)}"
        )
        return ApiResponse(success=False, message=f"查询数据范围时发生服务器错误: {str(e)}", data=error_data_detail)