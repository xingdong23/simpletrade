"""
数据相关API路由定义
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from simpletrade.core.database import get_db
from simpletrade.models.database import DataImportLog
from simpletrade.api.schemas.common import ApiResponse

router = APIRouter(
    prefix="/data",
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