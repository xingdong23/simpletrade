"""
SimpleTrade策略API

提供策略相关的RESTful API接口。
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from simpletrade.config.database import get_db
from simpletrade.models.database import Strategy, UserStrategy, BacktestRecord
from simpletrade.services.strategy_service import StrategyService
from simpletrade.services.backtest_service import BacktestService
from simpletrade.services.monitor_service import MonitorService
from simpletrade.core.engine import STMainEngine

# 创建路由器
router = APIRouter(prefix="/api/strategies", tags=["strategies"])

# 数据模型
class ApiResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None

class StrategyParameter(BaseModel):
    """策略参数模型"""
    type: str
    default: Any
    min: Optional[Any] = None
    max: Optional[Any] = None
    options: Optional[List[str]] = None
    description: str

class StrategyModel(BaseModel):
    """策略模型"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    type: str
    complexity: int
    resource_requirement: int
    parameters: Dict[str, StrategyParameter]

# API路由
@router.get("/", response_model=ApiResponse)
async def get_strategies(
    type: Optional[str] = None,
    category: Optional[str] = None,
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取策略列表"""
    try:
        # 使用策略服务获取策略列表
        strategies = strategy_service.get_strategies(type, category)

        # 如果没有策略，返回空列表
        if not strategies:
            return {
                "success": True,
                "message": "没有找到符合条件的策略",
                "data": []
            }

        # 将数据库对象转换为字典
        strategy_list = []
        for s in strategies:
            strategy_dict = {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "type": s.type,
                "complexity": s.complexity,
                "resource_requirement": s.resource_requirement,
                "parameters": s.parameters
            }
            strategy_list.append(strategy_dict)

        return {
            "success": True,
            "message": f"获取策略成功，共 {len(strategy_list)} 个",
            "data": strategy_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取策略失败: {str(e)}"
        }

@router.get("/{strategy_id}", response_model=ApiResponse)
async def get_strategy(strategy_id: int, strategy_service: StrategyService = Depends(get_strategy_service)):
    """获取策略详情"""
    try:
        # 使用策略服务获取策略详情
        strategy = strategy_service.get_strategy(strategy_id)

        if not strategy:
            return {
                "success": False,
                "message": f"未找到ID为 {strategy_id} 的策略"
            }

        # 获取策略类详细信息
        strategy_details = None
        for detail in strategy_service.get_strategy_details():
            if detail["class_name"] == strategy.type:
                strategy_details = detail
                break

        # 将数据库对象转换为字典
        strategy_dict = {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "category": strategy.category,
            "type": strategy.type,
            "complexity": strategy.complexity,
            "resource_requirement": strategy.resource_requirement,
            "parameters": strategy.parameters,
            "code": strategy.code
        }

        # 添加策略类详细信息
        if strategy_details:
            strategy_dict["class_details"] = strategy_details

        return {
            "success": True,
            "message": f"获取策略详情成功",
            "data": strategy_dict
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取策略详情失败: {str(e)}"
        }

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_user_strategies(user_id: int, strategy_service: StrategyService = Depends(get_strategy_service)):
    """获取用户策略列表"""
    try:
        # 使用策略服务获取用户策略列表
        user_strategies = strategy_service.get_user_strategies(user_id)

        # 如果没有用户策略，返回空列表
        if not user_strategies:
            return {
                "success": True,
                "message": f"用户 {user_id} 没有策略",
                "data": []
            }

        # 将数据库对象转换为字典
        strategies = []
        for us in user_strategies:
            strategy = us.strategy
            strategy_dict = {
                "id": us.id,
                "name": us.name,
                "strategy_id": strategy.id,
                "strategy_name": strategy.name,
                "category": strategy.category,
                "type": strategy.type,
                "complexity": strategy.complexity,
                "resource_requirement": strategy.resource_requirement,
                "parameters": us.parameters
            }
            strategies.append(strategy_dict)

        return {
            "success": True,
            "message": f"获取用户策略成功，共 {len(strategies)} 个",
            "data": strategies
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取用户策略失败: {str(e)}"
        }

@router.post("/create", response_model=ApiResponse)
async def create_strategy(request: CreateStrategyRequest, strategy_service: StrategyService = Depends(get_strategy_service)):
    """创建策略"""
    try:
        # 创建策略
        strategy = strategy_service.create_strategy(
            name=request.name,
            description=request.description,
            type=request.type,
            category=request.category,
            parameters=request.parameters
        )

        if not strategy:
            return {
                "success": False,
                "message": "创建策略失败"
            }

        return {
            "success": True,
            "message": "创建策略成功",
            "data": {
                "id": strategy.id,
                "name": strategy.name,
                "type": strategy.type
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"创建策略失败: {str(e)}"
        }

@router.post("/user/create", response_model=ApiResponse)
async def create_user_strategy(request: CreateUserStrategyRequest, strategy_service: StrategyService = Depends(get_strategy_service)):
    """创建用户策略"""
    try:
        # 创建用户策略
        user_strategy = strategy_service.create_user_strategy(
            user_id=request.user_id,
            strategy_id=request.strategy_id,
            name=request.name,
            parameters=request.parameters
        )

        if not user_strategy:
            return {
                "success": False,
                "message": "创建用户策略失败"
            }

        return {
            "success": True,
            "message": "创建用户策略成功",
            "data": {
                "id": user_strategy.id,
                "name": user_strategy.name,
                "strategy_id": user_strategy.strategy_id
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"创建用户策略失败: {str(e)}"
        }

@router.post("/user/{user_strategy_id}/init", response_model=ApiResponse)
async def init_strategy(user_strategy_id: int, strategy_service: StrategyService = Depends(get_strategy_service)):
    """初始化策略"""
    try:
        # 初始化策略
        result = strategy_service.init_strategy(user_strategy_id)

        if not result:
            return {
                "success": False,
                "message": "初始化策略失败"
            }

        return {
            "success": True,
            "message": "初始化策略成功"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"初始化策略失败: {str(e)}"
        }

@router.post("/user/{user_strategy_id}/start", response_model=ApiResponse)
async def start_strategy(
    user_strategy_id: int,
    strategy_service: StrategyService = Depends(get_strategy_service),
    monitor_service: MonitorService = Depends(get_monitor_service)
):
    """启动策略"""
    try:
        # 获取用户策略
        user_strategy = strategy_service.get_user_strategy(user_strategy_id)
        if not user_strategy:
            return {
                "success": False,
                "message": f"未找到ID为 {user_strategy_id} 的用户策略"
            }

        # 启动策略
        result = strategy_service.start_strategy(user_strategy_id)

        if not result:
            return {
                "success": False,
                "message": "启动策略失败"
            }

        # 开始监控策略
        strategy_config = strategy_service.load_user_strategy(user_strategy_id)
        monitor_service.start_monitor(user_strategy_id, strategy_config["strategy_name"])

        return {
            "success": True,
            "message": "启动策略成功"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"启动策略失败: {str(e)}"
        }

@router.post("/user/{user_strategy_id}/stop", response_model=ApiResponse)
async def stop_strategy(
    user_strategy_id: int,
    strategy_service: StrategyService = Depends(get_strategy_service),
    monitor_service: MonitorService = Depends(get_monitor_service)
):
    """停止策略"""
    try:
        # 停止策略
        result = strategy_service.stop_strategy(user_strategy_id)

        if not result:
            return {
                "success": False,
                "message": "停止策略失败"
            }

        # 停止监控策略
        monitor_service.stop_monitor(user_strategy_id)

        return {
            "success": True,
            "message": "停止策略成功"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"停止策略失败: {str(e)}"
        }

@router.get("/monitor", response_model=ApiResponse)
async def get_all_monitors(monitor_service: MonitorService = Depends(get_monitor_service)):
    """获取所有策略监控信息"""
    try:
        # 获取所有策略监控信息
        monitors = monitor_service.get_all_monitors()

        return {
            "success": True,
            "message": f"获取策略监控信息成功，共 {len(monitors)} 个",
            "data": monitors
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取策略监控信息失败: {str(e)}"
        }

@router.get("/monitor/{user_strategy_id}", response_model=ApiResponse)
async def get_monitor(user_strategy_id: int, monitor_service: MonitorService = Depends(get_monitor_service)):
    """获取策略监控信息"""
    try:
        # 获取策略监控信息
        monitor = monitor_service.get_monitor(user_strategy_id)

        if not monitor:
            return {
                "success": False,
                "message": f"未找到ID为 {user_strategy_id} 的策略监控信息"
            }

        return {
            "success": True,
            "message": "获取策略监控信息成功",
            "data": monitor.to_dict()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取策略监控信息失败: {str(e)}"
        }

@router.post("/backtest", response_model=ApiResponse)
async def run_backtest(request: BacktestRequest, backtest_service: BacktestService = Depends(get_backtest_service)):
    """运行回测"""
    try:
        # 运行回测
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
            size=request.size,
            pricetick=request.pricetick,
            user_id=request.user_id
        )

        if not result["success"]:
            return result

        return {
            "success": True,
            "message": "回测成功",
            "data": result["data"]
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"运行回测失败: {str(e)}"
        }

@router.get("/backtest/records", response_model=ApiResponse)
async def get_backtest_records(
    user_id: Optional[int] = None,
    strategy_id: Optional[int] = None,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取回测记录"""
    try:
        # 获取回测记录
        records = backtest_service.get_backtest_records(user_id, strategy_id)

        # 如果没有回测记录，返回空列表
        if not records:
            return {
                "success": True,
                "message": "没有找到符合条件的回测记录",
                "data": []
            }

        # 将数据库对象转换为字典
        record_list = []
        for record in records:
            record_dict = {
                "id": record.id,
                "user_id": record.user_id,
                "strategy_id": record.strategy_id,
                "symbol": record.symbol,
                "exchange": record.exchange,
                "interval": record.interval,
                "start_date": record.start_date.strftime("%Y-%m-%d"),
                "end_date": record.end_date.strftime("%Y-%m-%d"),
                "initial_capital": float(record.initial_capital),
                "final_capital": float(record.final_capital),
                "total_return": float(record.total_return),
                "annual_return": float(record.annual_return) if record.annual_return else None,
                "max_drawdown": float(record.max_drawdown) if record.max_drawdown else None,
                "sharpe_ratio": float(record.sharpe_ratio) if record.sharpe_ratio else None,
                "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            record_list.append(record_dict)

        return {
            "success": True,
            "message": f"获取回测记录成功，共 {len(record_list)} 个",
            "data": record_list
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取回测记录失败: {str(e)}"
        }

@router.get("/backtest/records/{record_id}", response_model=ApiResponse)
async def get_backtest_record(record_id: int, backtest_service: BacktestService = Depends(get_backtest_service)):
    """获取回测记录详情"""
    try:
        # 获取回测记录
        record = backtest_service.get_backtest_record(record_id)

        if not record:
            return {
                "success": False,
                "message": f"未找到ID为 {record_id} 的回测记录"
            }

        # 将数据库对象转换为字典
        record_dict = {
            "id": record.id,
            "user_id": record.user_id,
            "strategy_id": record.strategy_id,
            "symbol": record.symbol,
            "exchange": record.exchange,
            "interval": record.interval,
            "start_date": record.start_date.strftime("%Y-%m-%d"),
            "end_date": record.end_date.strftime("%Y-%m-%d"),
            "initial_capital": float(record.initial_capital),
            "final_capital": float(record.final_capital),
            "total_return": float(record.total_return),
            "annual_return": float(record.annual_return) if record.annual_return else None,
            "max_drawdown": float(record.max_drawdown) if record.max_drawdown else None,
            "sharpe_ratio": float(record.sharpe_ratio) if record.sharpe_ratio else None,
            "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "results": record.results
        }

        return {
            "success": True,
            "message": "获取回测记录详情成功",
            "data": record_dict
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取回测记录详情失败: {str(e)}"
        }
