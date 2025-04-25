"""
SimpleTrade策略API

提供策略相关的RESTful API接口。
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from datetime import date
from sqlalchemy.orm import Session
import logging
import traceback
from pathlib import Path

# TODO: Update imports after moving files
from simpletrade.api.deps import get_db # Correct path for dependency injection
from simpletrade.models.database import Strategy, UserStrategy, BacktestRecord
from simpletrade.services.strategy_service import StrategyService
from simpletrade.apps.st_backtest.service import BacktestService
from simpletrade.services.monitor_service import MonitorService
# from simpletrade.core.engine import STMainEngine # Type hint handled below

# TODO: Check if global engine import is still needed/correct after initialization refactor
# from simpletrade.main import main_engine as global_main_engine 
from simpletrade.core.engine import STMainEngine # For type hinting
from simpletrade.strategies import get_strategy_class_names
# from simpletrade.models.user import User # Commenting out as model doesn't exist

# 获取 logger 实例
logger = logging.getLogger(__name__)

# --- 依赖注入函数定义 (移到前面) ---
# TODO: Move these dependencies to simpletrade/api/deps.py
def get_main_engine(request: Request) -> STMainEngine:
    """依赖函数：从 FastAPI app state 获取主引擎实例"""
    if hasattr(request.app.state, 'main_engine') and request.app.state.main_engine:
        return request.app.state.main_engine
    else:
        # If engine not in state, something went wrong during startup
        raise RuntimeError("Main engine not found in app state. Check server startup.")

def get_strategy_service():
    """获取策略服务"""
    try:
        service = StrategyService()
        yield service
    finally:
        pass

def get_monitor_service(main_engine: STMainEngine = Depends(get_main_engine)) -> MonitorService:
    return MonitorService(main_engine=main_engine)

def get_backtest_service(main_engine = Depends(get_main_engine)):
    """获取回测服务"""
    try:
        # 尝试通过主引擎获取回测引擎
        backtest_engine = main_engine.engines.get("st_backtest")
        service = BacktestService(backtest_engine)
        yield service
    except Exception as e:
        # 如果无法获取，回退到创建独立的服务实例
        logger.warning(f"Unable to get backtest engine from main_engine: {e}, creating standalone service")
        service = BacktestService()
        yield service

# --- 创建路由器 --- 
router = APIRouter(
    prefix="/strategies",
    tags=["strategies"],
    dependencies=[Depends(get_main_engine)],
)

# 数据模型
# TODO: Move these Pydantic models to simpletrade/api/schemas/strategy.py
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

class CreateStrategyRequest(BaseModel):
    """创建策略请求模型"""
    name: str
    description: Optional[str] = None
    type: str
    category: Optional[str] = None
    parameters: Dict[str, Any]

class CreateUserStrategyRequest(BaseModel):
    """创建用户策略请求模型"""
    user_id: int
    strategy_id: int
    name: str
    parameters: Dict[str, Any]

class BacktestRequest(BaseModel):
    """运行回测请求模型"""
    user_id: int
    strategy_id: int
    symbol: str
    exchange: str
    interval: str
    start_date: date
    end_date: date
    initial_capital: float
    parameters: Optional[Dict[str, Any]] = Field(None, description="用户自定义策略参数，覆盖默认值")
    rate: float = Field(..., description="手续费率 (例如 0.0001 for 0.01%)")
    slippage: float = Field(..., description="滑点大小 (例如 0.2)")

# API路由
@router.get("/types", response_model=ApiResponse)
async def get_strategy_types_api(
    db: Session = Depends(get_db), # TODO: Update import from deps
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取数据库中所有活跃策略的不重复类型列表"""
    try:
        types = strategy_service.get_strategy_types(db)
        return {"success": True, "message": "获取策略类型成功", "data": types}
    except Exception as e:
        logger.error(f"Failed to get strategy types: {e}\n{traceback.format_exc()}")
        return {"success": False, "message": f"获取策略类型失败: {str(e)}"}

@router.get("/", response_model=ApiResponse)
async def get_strategies(
    type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db), # TODO: Update import from deps
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取策略列表"""
    try:
        # Pass db session to service method
        strategies = strategy_service.get_strategies(db, type, category)

        # If no strategies, return empty list
        if not strategies:
            return {
                "success": True,
                "message": "没有找到符合条件的策略",
                "data": []
            }

        # Convert DB objects to dictionaries
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
async def get_strategy(
    strategy_id: int, 
    db: Session = Depends(get_db), # TODO: Update import from deps
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取策略详情，并从文件加载策略代码"""
    try:
        strategy = strategy_service.get_strategy(db, strategy_id)

        if not strategy:
            raise HTTPException(status_code=404, detail=f"未找到ID为 {strategy_id} 的策略")

        # --- Load code from file (using more robust path finding) --- 
        strategy_code = None
        file_path_str = ""
        if hasattr(strategy, 'identifier') and strategy.identifier:
            try:
                # --- Locate strategies directory based on current file (__file__) --- 
                current_file_path = Path(__file__).resolve() # Get absolute path of routers/strategies.py
                # simpletrade/api/routers/strategies.py -> simpletrade/api/routers/ -> simpletrade/api/ -> simpletrade/
                simpletrade_root = current_file_path.parent.parent.parent 
                strategies_dir = simpletrade_root / "strategies"
                # --------------------------------------------------------------------
                
                file_path = strategies_dir / f"{strategy.identifier}.py"
                file_path_str = str(file_path)

                if file_path.is_file():
                    strategy_code = file_path.read_text(encoding='utf-8')
                    logger.info(f"成功加载策略代码文件: {file_path_str}")
                else:
                    logger.warning(f"策略代码文件未找到 (检查路径): {file_path_str}") # Updated log message
            except FileNotFoundError:
                 logger.warning(f"策略代码文件未找到 (FileNotFoundError): {file_path_str}")
            except Exception as e:
                logger.error(f"读取策略代码文件失败 ({file_path_str}): {e}\n{traceback.format_exc()}")
        else:
             logger.warning(f"策略 {strategy.id} ({strategy.name}) 没有有效的 identifier 字段，无法加载代码。")
        # --- Code loading end --- 

        # Get strategy class details
        strategy_details = None
        for detail in strategy_service.get_strategy_details():
            if detail["class_name"] == strategy.type:
                strategy_details = detail
                break

        # Convert DB object to dictionary
        strategy_dict = {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "category": strategy.category,
            "type": strategy.type,
            "identifier": strategy.identifier if hasattr(strategy, 'identifier') else None,
            "complexity": strategy.complexity,
            "resource_requirement": strategy.resource_requirement,
            "parameters": strategy.parameters,
            "code": strategy_code
        }

        # Add strategy class details
        if strategy_details:
            strategy_dict["class_details"] = strategy_details

        return {
            "success": True,
            "message": f"获取策略详情成功",
            "data": strategy_dict
        }
    except HTTPException as http_exc:
        # Re-raise HTTPException for FastAPI to handle
        raise http_exc
    except Exception as e:
        logger.error(f"获取策略详情失败 (ID: {strategy_id}): {e}\n{traceback.format_exc()}")
        # For other internal errors, raise HTTPException as well
        raise HTTPException(status_code=500, detail=f"获取策略详情时发生内部错误")

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_user_strategies(
    user_id: int, 
    db: Session = Depends(get_db), # TODO: Update import from deps
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取用户策略列表"""
    try:
        user_strategies = strategy_service.get_user_strategies(db, user_id)
        return {"success": True, "message": "获取用户策略成功", "data": user_strategies}
    except Exception as e:
        logger.error(f"Failed to get user strategies for user {user_id}: {e}\n{traceback.format_exc()}")
        return {"success": False, "message": f"获取用户策略失败: {str(e)}"}

@router.post("/create", response_model=ApiResponse)
async def create_strategy(request: CreateStrategyRequest, strategy_service: StrategyService = Depends(get_strategy_service)):
    """创建新策略（非用户特定的）"""
    try:
        # 假设 StrategyService 有一个 create_strategy 方法
        # 注意：当前 models.database.Strategy 似乎没有 db 参数，可能需要调整
        # created_strategy = strategy_service.create_strategy(request.name, request.description, ...)
        
        # 占位符响应 - 需要实现 StrategyService.create_strategy
        # return {"success": True, "message": "策略创建成功 (占位符)", "data": {"id": 1, **request.dict()}}
        raise NotImplementedError("Strategy creation service endpoint not fully implemented.")
    except Exception as e:
        logger.error(f"Failed to create strategy: {e}\n{traceback.format_exc()}")
        return {"success": False, "message": f"创建策略失败: {str(e)}"}


@router.post("/user/create", response_model=ApiResponse)
async def create_user_strategy(request: CreateUserStrategyRequest, strategy_service: StrategyService = Depends(get_strategy_service)):
    """创建用户策略实例"""
    try:
        # 传递所有参数给服务层方法
        user_strategy = strategy_service.create_user_strategy(
            user_id=request.user_id, 
            strategy_id=request.strategy_id, 
            name=request.name, 
            parameters=request.parameters
        )
        
        if not user_strategy:
            raise HTTPException(status_code=400, detail="创建用户策略失败")
        
        # 将UserStrategy对象转换为可序列化的字典
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
        
        # 返回创建成功的对象信息
        return {
            "success": True, 
            "message": "用户策略创建成功", 
            "data": user_strategy_dict # 返回字典而不是对象
        }
    except ValueError as ve:
        # 捕获服务层可能抛出的特定错误 (例如，策略ID不存在)
        logger.warning(f"Failed to create user strategy due to value error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to create user strategy: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"创建用户策略时发生内部错误")

@router.post("/user/{user_strategy_id}/start", response_model=ApiResponse)
async def start_strategy(
    user_strategy_id: int,
    strategy_service: StrategyService = Depends(get_strategy_service),
    monitor_service: MonitorService = Depends(get_monitor_service)
):
    """启动用户策略实例（在监视器中）"""
    try:
        # 1. 获取用户策略配置 (需要从数据库或其他地方获取)
        # user_strategy_config = strategy_service.get_user_strategy_config(user_strategy_id)
        # if not user_strategy_config:
        #     raise HTTPException(status_code=404, detail="User strategy not found")

        # 2. 调用监控服务启动策略
        # monitor_service.start_strategy_monitor(user_strategy_id, user_strategy_config)
        
        # 占位符响应
        return {"success": True, "message": f"策略 {user_strategy_id} 启动请求已发送 (占位符)"}
        # raise NotImplementedError("Start strategy endpoint not fully implemented.")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Failed to start strategy {user_strategy_id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"启动策略时发生内部错误")

@router.post("/user/{user_strategy_id}/stop", response_model=ApiResponse)
async def stop_strategy(
    user_strategy_id: int,
    strategy_service: StrategyService = Depends(get_strategy_service),
    monitor_service: MonitorService = Depends(get_monitor_service)
):
    """停止用户策略实例（在监视器中）"""
    try:
        # 调用监控服务停止策略
        # monitor_service.stop_strategy_monitor(user_strategy_id)
        
        # 占位符响应
        return {"success": True, "message": f"策略 {user_strategy_id} 停止请求已发送 (占位符)"}
        # raise NotImplementedError("Stop strategy endpoint not fully implemented.")

    except Exception as e:
        logger.error(f"Failed to stop strategy {user_strategy_id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"停止策略时发生内部错误")

@router.get("/monitor", response_model=ApiResponse)
async def get_all_monitors(monitor_service: MonitorService = Depends(get_monitor_service)):
    """获取所有正在监控的策略状态"""
    try:
        # status = monitor_service.get_all_monitor_status()
        # return {"success": True, "message": "获取监控状态成功", "data": status}
        raise NotImplementedError("Get all monitors endpoint not fully implemented.")
    except Exception as e:
        logger.error(f"Failed to get all monitor statuses: {e}\n{traceback.format_exc()}")
        return {"success": False, "message": f"获取监控状态失败: {str(e)}"}

@router.get("/monitor/{user_strategy_id}", response_model=ApiResponse)
async def get_monitor(user_strategy_id: int, monitor_service: MonitorService = Depends(get_monitor_service)):
    """获取单个策略的监控状态"""
    try:
        # status = monitor_service.get_monitor_status(user_strategy_id)
        # if status is None:
        #     raise HTTPException(status_code=404, detail="Monitor not found for strategy")
        # return {"success": True, "message": "获取监控状态成功", "data": status}
        raise NotImplementedError("Get monitor endpoint not fully implemented.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Failed to get monitor status for {user_strategy_id}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"获取监控状态时发生内部错误")

@router.post("/backtest", response_model=ApiResponse)
async def run_backtest(request: BacktestRequest, backtest_service: BacktestService = Depends(get_backtest_service)):
    """运行策略回测"""
    try:
        # 调用回测服务
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
         logger.warning(f"Backtest failed due to invalid input: {ve}")
         raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Backtest failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"运行回测时发生内部错误: {str(e)}")

@router.get("/backtest/records", response_model=ApiResponse)
async def get_backtest_records(
    user_id: Optional[int] = None,
    strategy_id: Optional[int] = None,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取回测记录列表"""
    try:
        records = backtest_service.get_backtest_records(user_id, strategy_id)

        # 如果没有记录，返回空列表
        if not records:
            return {
                "success": True,
                "message": "没有找到符合条件的回测记录",
                "data": []
            }

        # 将数据库对象转换为字典列表 (如果服务层还没有做)
        record_list = []
        for r in records:
            record_dict = {
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
                "results": r.results, # 假设 results 已经是可序列化的 (e.g., dict)
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            record_list.append(record_dict)

        return {
            "success": True,
            "message": f"获取回测记录成功，共 {len(record_list)} 条",
            "data": record_list
        }
    except Exception as e:
        logger.error(f"获取回测记录失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取回测记录时发生内部错误")

@router.get("/backtest/records/{record_id}", response_model=ApiResponse)
async def get_backtest_record(record_id: int, backtest_service: BacktestService = Depends(get_backtest_service)):
    """获取单个回测记录详情"""
    try:
        record = backtest_service.get_backtest_record(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="未找到指定的回测记录")
        
        # 将数据库对象转换为字典 (如果服务层还没有做)
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
            "results": record.results, # 假设 results 已经是可序列化的 (e.g., dict)
            "created_at": record.created_at.isoformat() if record.created_at else None
        }

        return {"success": True, "message": "获取回测记录详情成功", "data": record_dict}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"获取回测记录 {record_id} 失败: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="获取回测记录详情时发生内部错误") 