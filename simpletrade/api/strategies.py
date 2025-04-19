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

from simpletrade.config.database import get_db
from simpletrade.models.database import Strategy, UserStrategy, BacktestRecord
from simpletrade.services.strategy_service import StrategyService
from simpletrade.services.backtest_service import BacktestService
from simpletrade.services.monitor_service import MonitorService
# from simpletrade.core.engine import STMainEngine # 类型提示已通过下方导入

# 移除全局导入
# from simpletrade.main import main_engine as global_main_engine
from simpletrade.core.engine import STMainEngine # 导入类型提示
from simpletrade.strategies import get_strategy_class_names

# 获取 logger 实例
logger = logging.getLogger(__name__)

# --- 依赖注入函数定义 (移到前面) ---

def get_main_engine(request: Request) -> STMainEngine:
    """依赖函数：从 FastAPI app state 获取主引擎实例"""
    if hasattr(request.app.state, 'main_engine') and request.app.state.main_engine:
        return request.app.state.main_engine
    else:
        # 如果引擎不在 state 中，说明启动时存储失败或未存储
        raise RuntimeError("Main engine not found in app state. Check server startup.")

def get_strategy_service(main_engine: STMainEngine = Depends(get_main_engine)) -> StrategyService:
    return StrategyService(main_engine=main_engine)

def get_monitor_service(main_engine: STMainEngine = Depends(get_main_engine)) -> MonitorService:
    return MonitorService(main_engine=main_engine)

def get_backtest_service() -> BacktestService:
    return BacktestService()

# --- 创建路由器 --- 
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

# API路由
@router.get("/types", response_model=ApiResponse)
async def get_strategy_types_api(
    db: Session = Depends(get_db),
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
    db: Session = Depends(get_db),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取策略列表"""
    try:
        # 将 db 会话传递给服务方法
        strategies = strategy_service.get_strategies(db, type, category)

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
async def get_strategy(
    strategy_id: int, 
    db: Session = Depends(get_db),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取策略详情，并从文件加载策略代码"""
    try:
        strategy = strategy_service.get_strategy(db, strategy_id)

        if not strategy:
            # 返回 404 更符合 RESTful 规范
            raise HTTPException(status_code=404, detail=f"未找到ID为 {strategy_id} 的策略")

        # --- 从文件加载代码 --- 
        strategy_code = None
        file_path_str = ""
        # 假设模型中已有 identifier 属性
        if hasattr(strategy, 'identifier') and strategy.identifier:
            try:
                # 假设工作区根目录是基础路径
                base_path = Path('.') 
                strategies_dir = base_path / "simpletrade" / "strategies"
                file_path = strategies_dir / f"{strategy.identifier}.py"
                file_path_str = str(file_path)

                if file_path.is_file():
                    strategy_code = file_path.read_text(encoding='utf-8')
                    logger.info(f"成功加载策略代码文件: {file_path_str}")
                else:
                    logger.warning(f"策略代码文件未找到: {file_path_str}")
            except FileNotFoundError:
                 logger.warning(f"策略代码文件未找到: {file_path_str}")
            except Exception as e:
                logger.error(f"读取策略代码文件失败 ({file_path_str}): {e}\n{traceback.format_exc()}")
        else:
             logger.warning(f"策略 {strategy.id} ({strategy.name}) 没有有效的 identifier 字段，无法加载代码。")
        # --- 代码加载结束 --- 

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
            "identifier": strategy.identifier if hasattr(strategy, 'identifier') else None,
            "complexity": strategy.complexity,
            "resource_requirement": strategy.resource_requirement,
            "parameters": strategy.parameters,
            "code": strategy_code
        }

        # 添加策略类详细信息
        if strategy_details:
            strategy_dict["class_details"] = strategy_details

        return {
            "success": True,
            "message": f"获取策略详情成功",
            "data": strategy_dict
        }
    except HTTPException as http_exc:
        # 重新抛出 HTTPException 以便 FastAPI 处理
        raise http_exc
    except Exception as e:
        logger.error(f"获取策略详情失败 (ID: {strategy_id}): {e}\n{traceback.format_exc()}")
        # 对于其他内部错误，也抛出 HTTPException
        raise HTTPException(status_code=500, detail=f"获取策略详情时发生内部错误")

@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_user_strategies(
    user_id: int, 
    db: Session = Depends(get_db),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取用户策略列表 (包含状态)"""
    try:
        # StrategyService 现在直接返回字典列表，包含状态
        user_strategies_data = strategy_service.get_user_strategies(db, user_id)

        # 如果没有用户策略，返回空列表
        if not user_strategies_data:
            return {
                "success": True,
                "message": f"用户 {user_id} 没有策略",
                "data": []
            }
        
        # 直接返回 service 层处理好的数据
        return {
            "success": True,
            "message": f"获取用户策略成功，共 {len(user_strategies_data)} 个",
            "data": user_strategies_data
        }
    except Exception as e:
        # 添加更详细的错误日志
        import traceback
        logger.error(f"Failed to get user strategies for user {user_id}: {e}\n{traceback.format_exc()}")
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
async def init_strategy(
    user_strategy_id: int, 
    strategy_service: StrategyService = Depends(get_strategy_service)
):
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
