"""
SimpleTrade分析应用API路由
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from vnpy.trader.constant import Exchange, Interval

# 创建路由器
router = APIRouter(
    prefix="/api/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)

# 依赖注入：获取分析引擎
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_analysis_engine():
    """获取分析引擎"""
    # 这里需要从全局获取引擎实例
    from simpletrade.main import main_engine
    from simpletrade.apps.st_analysis import STAnalysisApp
    engine_instance = main_engine.get_engine(STAnalysisApp.app_name)
    logger.info(f"get_analysis_engine called. Requested engine name: {STAnalysisApp.app_name}, got instance: {engine_instance}")
    return engine_instance

# 模型定义
class IndicatorRequest(BaseModel):
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: str
    indicators: List[str] = ["ma", "macd", "rsi"]

class BacktestRequest(BaseModel):
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: str
    strategy_params: Dict[str, Any]

# 路由定义
@router.post("/indicators")
async def calculate_indicators(
    request: IndicatorRequest,
    engine = Depends(get_analysis_engine)
):
    """计算技术指标"""
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)
        interval_obj = Interval(request.interval)
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        # 获取数据
        data_engine = engine.main_engine.get_engine("st_datamanager")
        if not data_engine:
            raise HTTPException(status_code=500, detail="无法获取数据管理引擎")
        
        bars = data_engine.get_bar_data(
            symbol=request.symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            start=start,
            end=end
        )
        
        if not bars:
            raise HTTPException(status_code=404, detail="未找到符合条件的数据")
        
        # 计算指标
        df = engine.calculate_indicators(bars, request.indicators)
        
        # 转换为JSON格式
        df.index = df.index.astype(str)  # 将datetime索引转换为字符串
        result = df.to_dict(orient="index")
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.exception("计算指标出错")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backtest")
async def backtest_strategy(
    request: BacktestRequest,
    engine = Depends(get_analysis_engine)
):
    """回测策略"""
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)
        interval_obj = Interval(request.interval)
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.strptime(request.end_date, "%Y-%m-%d")
        
        # 获取数据
        data_engine = engine.main_engine.get_engine("st_datamanager")
        if not data_engine:
            raise HTTPException(status_code=500, detail="无法获取数据管理引擎")
        
        bars = data_engine.get_bar_data(
            symbol=request.symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            start=start,
            end=end
        )
        
        if not bars:
            raise HTTPException(status_code=404, detail="未找到符合条件的数据")
        
        # 回测策略
        results = engine.backtest_strategy(bars, request.strategy_params)
        
        # 处理DataFrame
        if "data" in results:
            df = results["data"]
            df.index = df.index.astype(str)  # 将datetime索引转换为字符串
            results["data"] = df.to_dict(orient="index")
        
        return {
            "success": True,
            "data": results
        }
    except Exception as e:
        logger.exception("回测出错")
        raise HTTPException(status_code=500, detail=str(e))
