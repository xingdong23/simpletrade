"""
SimpleTrade策略API

提供策略相关的RESTful API接口。
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from simpletrade.api.deps import get_db, handle_api_exception
from simpletrade.api.schemas.strategy import (
    ApiResponse,
    CreateUserStrategyRequest,
    BacktestRequest
)
from simpletrade.apps.st_backtest.service import BacktestService
from simpletrade.core.engine import STMainEngine
from simpletrade.services.monitor_service import MonitorService
from simpletrade.services.strategy_service import StrategyService

# 获取logger实例
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/api/strategies",
    tags=["strategies"],
)

# 依赖注入函数
def get_main_engine(request: Request) -> STMainEngine:
    """从FastAPI app state获取主引擎实例"""
    if hasattr(request.app.state, 'main_engine') and request.app.state.main_engine:
        return request.app.state.main_engine
    raise HTTPException(
        status_code=500, 
        detail="主引擎未初始化，请检查服务器启动流程"
    )

def get_strategy_service(main_engine: STMainEngine = Depends(get_main_engine)) -> StrategyService:
    """获取策略服务"""
    return StrategyService(main_engine)

def get_monitor_service(main_engine: STMainEngine = Depends(get_main_engine)) -> MonitorService:
    """获取监控服务"""
    return MonitorService(main_engine=main_engine)

def get_backtest_service(main_engine: STMainEngine = Depends(get_main_engine)) -> BacktestService:
    """获取回测服务"""
    try:
        backtest_engine = main_engine.engines.get("st_backtest")
        return BacktestService(backtest_engine)
    except Exception as e:
        logger.warning(f"无法从主引擎获取回测引擎: {e}，创建独立服务实例")
        return BacktestService()

# ---------------- 策略管理API ----------------

@router.get("/types", response_model=ApiResponse)
async def get_strategy_types(
    db: Session = Depends(get_db),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取所有可用策略类型"""
    try:
        types = strategy_service.get_strategy_types(db)
        return {"success": True, "message": "获取策略类型成功", "data": types}
    except Exception as e:
        handle_api_exception("获取策略类型", e)

@router.get("/", response_model=ApiResponse)
async def get_strategies(
    type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取策略列表，可按类型和分类过滤"""
    try:
        strategies = strategy_service.get_strategies(db, type, category)
        
        if not strategies:
            return {
                "success": True,
                "message": "没有找到符合条件的策略",
                "data": []
            }

        strategy_list = [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "type": s.type,
                "complexity": s.complexity,
                "resource_requirement": s.resource_requirement,
                "parameters": s.parameters
            } for s in strategies
        ]

        return {
            "success": True,
            "message": f"获取策略成功，共 {len(strategy_list)} 个",
            "data": strategy_list
        }
    except Exception as e:
        handle_api_exception("获取策略列表", e)

@router.get("/{strategy_id}", response_model=ApiResponse)
async def get_strategy(
    strategy_id: int, 
    db: Session = Depends(get_db),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取单个策略详情，包括源代码"""
    try:
        strategy = strategy_service.get_strategy(db, strategy_id)

        if not strategy:
            raise HTTPException(status_code=404, detail=f"未找到ID为 {strategy_id} 的策略")

        # 加载策略代码
        strategy_code = strategy_service.load_strategy_code(strategy)
        
        # 获取策略类详情
        strategy_details = None
        for detail in strategy_service.get_strategy_details():
            if detail["class_name"] == strategy.type:
                strategy_details = detail
                break

        strategy_dict = {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "category": strategy.category,
            "type": strategy.type,
            "identifier": getattr(strategy, 'identifier', None),
            "complexity": strategy.complexity,
            "resource_requirement": strategy.resource_requirement,
            "parameters": strategy.parameters,
            "code": strategy_code
        }

        if strategy_details:
            strategy_dict["class_details"] = strategy_details

        return {
            "success": True,
            "message": "获取策略详情成功",
            "data": strategy_dict
        }
    except Exception as e:
        handle_api_exception("获取策略详情", e)

# ---------------- 用户策略API ----------------

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_user_strategies(
    user_id: int, 
    db: Session = Depends(get_db),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取用户策略列表"""
    try:
        user_strategies = strategy_service.get_user_strategies(db, user_id)
        return {"success": True, "message": "获取用户策略成功", "data": user_strategies}
    except Exception as e:
        handle_api_exception("获取用户策略", e)

@router.post("/user/create", response_model=ApiResponse)
async def create_user_strategy(
    request: CreateUserStrategyRequest, 
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """创建用户策略实例"""
    try:
        user_strategy = strategy_service.create_user_strategy(
            user_id=request.user_id, 
            strategy_id=request.strategy_id, 
            name=request.name, 
            parameters=request.parameters
        )
        
        if not user_strategy:
            raise HTTPException(status_code=400, detail="创建用户策略失败")
        
        user_strategy_dict = {
            "id": user_strategy.id,
            "user_id": user_strategy.user_id,
            "strategy_id": user_strategy.strategy_id,
            "name": user_strategy.name,
            "parameters": user_strategy.parameters,
            "created_at": user_strategy.created_at.isoformat() if user_strategy.created_at else None,
            "updated_at": user_strategy.updated_at.isoformat() if user_strategy.updated_at else None,
            "is_active": user_strategy.is_active
        }
        
        return {
            "success": True, 
            "message": "用户策略创建成功", 
            "data": user_strategy_dict
        }
    except ValueError as ve:
        logger.warning(f"创建用户策略参数错误: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        handle_api_exception("创建用户策略", e)

@router.post("/user/{user_strategy_id}/start", response_model=ApiResponse)
async def start_strategy(
    user_strategy_id: int,
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """启动用户策略实例"""
    try:
        success = strategy_service.start_strategy(user_strategy_id)
        if not success:
            raise HTTPException(status_code=400, detail=f"策略 {user_strategy_id} 启动失败")
        return {"success": True, "message": f"策略 {user_strategy_id} 启动成功"}
    except Exception as e:
        handle_api_exception("启动策略", e)

@router.post("/user/{user_strategy_id}/stop", response_model=ApiResponse)
async def stop_strategy(
    user_strategy_id: int,
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """停止用户策略实例"""
    try:
        success = strategy_service.stop_strategy(user_strategy_id)
        if not success:
            raise HTTPException(status_code=400, detail=f"策略 {user_strategy_id} 停止失败")
        return {"success": True, "message": f"策略 {user_strategy_id} 停止成功"}
    except Exception as e:
        handle_api_exception("停止策略", e)

# ---------------- 回测API ----------------

@router.post("/backtest", response_model=ApiResponse)
async def run_backtest(
    request: BacktestRequest, 
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """运行策略回测"""
    try:
        result = backtest_service.run_backtest(
            strategy_id=request.strategy_id,
            symbol=request.symbol,
            exchange=request.exchange,
            interval=request.interval,
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            rate=request.rate,
            slippage=request.slippage,
            parameters=request.parameters,
            user_id=request.user_id
        )
        return {"success": True, "message": "回测运行成功", "data": result}
    except ValueError as ve:
        logger.warning(f"回测参数错误: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        handle_api_exception("运行回测", e)

@router.get("/backtest/records", response_model=ApiResponse)
async def get_backtest_records(
    user_id: Optional[int] = None,
    strategy_id: Optional[int] = None,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取回测记录列表"""
    try:
        records = backtest_service.get_backtest_records(user_id, strategy_id)

        if not records:
            return {
                "success": True,
                "message": "没有找到符合条件的回测记录",
                "data": []
            }

        record_list = [
            {
                "id": r.id,
                "user_id": r.user_id,
                "strategy_id": r.strategy_id,
                "symbol": r.symbol,
                "exchange": r.exchange,
                "interval": r.interval,
                "start_date": r.start_date.isoformat() if r.start_date else None,
                "end_date": r.end_date.isoformat() if r.end_date else None,
                "initial_capital": float(r.initial_capital) if r.initial_capital is not None else None,
                "final_capital": float(r.final_capital) if r.final_capital is not None else None,
                "total_return": float(r.total_return) if r.total_return is not None else None,
                "annual_return": float(r.annual_return) if r.annual_return is not None else None,
                "max_drawdown": float(r.max_drawdown) if r.max_drawdown is not None else None,
                "sharpe_ratio": float(r.sharpe_ratio) if r.sharpe_ratio is not None else None,
                "results": r.results,
                "created_at": r.created_at.isoformat() if r.created_at else None
            } for r in records
        ]

        return {
            "success": True,
            "message": f"获取回测记录成功，共 {len(record_list)} 条",
            "data": record_list
        }
    except Exception as e:
        handle_api_exception("获取回测记录", e)

@router.get("/backtest/records/{record_id}", response_model=ApiResponse)
async def get_backtest_record(
    record_id: int, 
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取单个回测记录详情"""
    try:
        record = backtest_service.get_backtest_record(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="未找到指定的回测记录")
        
        record_dict = {
            "id": record.id,
            "user_id": record.user_id,
            "strategy_id": record.strategy_id,
            "symbol": record.symbol,
            "exchange": record.exchange,
            "interval": record.interval,
            "start_date": record.start_date.isoformat() if record.start_date else None,
            "end_date": record.end_date.isoformat() if record.end_date else None,
            "initial_capital": float(record.initial_capital) if record.initial_capital is not None else None,
            "final_capital": float(record.final_capital) if record.final_capital is not None else None,
            "total_return": float(record.total_return) if record.total_return is not None else None,
            "annual_return": float(record.annual_return) if record.annual_return is not None else None,
            "max_drawdown": float(record.max_drawdown) if record.max_drawdown is not None else None,
            "sharpe_ratio": float(record.sharpe_ratio) if record.sharpe_ratio is not None else None,
            "results": record.results,
            "created_at": record.created_at.isoformat() if record.created_at else None
        }

        return {"success": True, "message": "获取回测记录详情成功", "data": record_dict}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        handle_api_exception("获取回测记录详情", e) 