"""
SimpleTrade策略API

提供策略相关的RESTful API接口。
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
import logging
from typing import Optional, List
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database
from vnpy.trader.object import ContractData

from simpletrade.api.deps import get_db, handle_api_exception
from simpletrade.api.schemas.strategy import (
    ApiResponse,
    CreateUserStrategyRequest,
    BacktestRequest,
    BacktestRecord,
    PaginatedBacktestRecordsResponse
)
from simpletrade.api.schemas.backtest_report import BacktestReportDataModel
from simpletrade.apps.st_backtest.service import BacktestService
from simpletrade.core.engine import STMainEngine
from simpletrade.services.monitor_service import MonitorService
from simpletrade.services.strategy_service import StrategyService
from simpletrade.models.database import Strategy  # 添加Strategy模型的导入

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

# Define the response model for an interval option
class IntervalResponse(BaseModel):
    value: str
    label: str

# Define the response model for an exchange item
class ExchangeItem(BaseModel):
    name: str
    value: str

# Define the response model for a symbol item
class SymbolItem(BaseModel):
    name: str
    symbol: str
    exchange: str

# ---------------- 策略管理API ----------------

@router.get("/available-intervals", response_model=ApiResponse[List[IntervalResponse]])
async def get_available_intervals_endpoint():
    """
    获取可用的K线周期列表。
    """
    intervals_data = [
        {"value": "1m", "label": "1分钟"},
        {"value": "5m", "label": "5分钟"},
        {"value": "15m", "label": "15分钟"},
        {"value": "30m", "label": "30分钟"},
        {"value": "1h", "label": "1小时"},
        {"value": "1d", "label": "日线"},
        # {"value": "tick", "label": "Tick"}, # Future: if tick data selection is needed here
    ]
    return ApiResponse(success=True, message="K线周期列表获取成功", data=intervals_data)

@router.get("/available-exchanges", response_model=ApiResponse[List[ExchangeItem]])
async def get_available_exchanges_endpoint():
    """
    获取可用的交易所列表 (从VnPy的Exchange枚举动态生成)。
    """
    exchanges_data = []
    for exchange_member in Exchange:
        # 使用枚举成员的 .name 作为显示名称 (例如 'SSE', 'NASDAQ')
        # 使用枚举成员的 .value 作为实际值 (例如 'SSE', 'NASDAQ')
        # 在 vnpy.trader.constant.Exchange 中, .name 和 .value 通常是相同的字符串
        exchanges_data.append({
            "name": exchange_member.name,  # 例如: 'NASDAQ'
            "value": exchange_member.value # 例如: 'NASDAQ'
        })

    # 按交易所名称排序 (通常是字母顺序)
    exchanges_data.sort(key=lambda x: x["name"])

    return ApiResponse(success=True, message="交易所列表获取成功", data=exchanges_data)

@router.get("/available-symbols", response_model=ApiResponse[List[SymbolItem]])
async def get_available_symbols_endpoint(
    exchange: str,  # From query param ?exchange=NASDAQ
    query: Optional[str] = None, # Optional search query ?query=AAPL
    main_engine: STMainEngine = Depends(get_main_engine) # Or db: Session = Depends(get_db)
):
    """
    获取指定交易所下的可用合约列表。
    可以根据query参数进行模糊搜索。
    NOTE: Current implementation uses placeholder data.
    """
    try:
        symbols_data = []
        # Placeholder data logic - REPLACE WITH ACTUAL DATA SOURCE ACCESS
        # This is to make the endpoint functional and resolve the 422 error.
        # You need to replace this with logic to fetch real contract data from your system.
        placeholder_contracts = {
            "NASDAQ": [
                {"name": "Apple Inc.", "symbol": "AAPL", "exchange": "NASDAQ"},
                {"name": "Microsoft Corp.", "symbol": "MSFT", "exchange": "NASDAQ"},
                {"name": "Amazon.com Inc.", "symbol": "AMZN", "exchange": "NASDAQ"},
                {"name": "Alphabet Inc. Class A", "symbol": "GOOGL", "exchange": "NASDAQ"},
                {"name": "Meta Platforms Inc.", "symbol": "META", "exchange": "NASDAQ"},
            ],
            "SSE": [
                {"name": "贵州茅台", "symbol": "600519", "exchange": "SSE"},
                {"name": "工商银行", "symbol": "601398", "exchange": "SSE"},
            ],
            "SZSE": [
                {"name": "宁德时代", "symbol": "300750", "exchange": "SZSE"},
            ],
            "HKEX": [
                {"name": "腾讯控股", "symbol": "00700", "exchange": "HKEX"},
            ]
            # Add more exchanges and symbols as needed for testing
        }

        if exchange in placeholder_contracts:
            for contract_info in placeholder_contracts[exchange]:
                item = SymbolItem(**contract_info)
                if query:
                    if query.lower() in item.name.lower() or query.lower() in item.symbol.lower():
                        symbols_data.append(item)
                else:
                    symbols_data.append(item)

        if not symbols_data and query:
            return ApiResponse(success=True, message=f"在交易所 {exchange} 未找到符合查询 '{query}' 的合约 (占位符数据)", data=[])
        elif not symbols_data:
            return ApiResponse(success=True, message=f"交易所 {exchange} 下没有配置合约数据 (占位符数据)", data=[])

        return ApiResponse(success=True, message="合约列表获取成功 (占位符数据)", data=symbols_data)

    except Exception as e:
        logger.error("获取合约列表时发生错误: %s", e, exc_info=True)
        # Return a generic error message, or more specific if possible
        return ApiResponse(success=False, message="获取合约列表失败: 服务内部错误", data=None)

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

@router.get("/user/detail/{user_strategy_id}", response_model=ApiResponse)
async def get_user_strategy_detail(
    user_strategy_id: int,
    db: Session = Depends(get_db),
    strategy_service: StrategyService = Depends(get_strategy_service)
):
    """获取单个用户策略详情"""
    try:
        user_strategy = strategy_service.get_user_strategy_detail(db, user_strategy_id)
        if not user_strategy:
            raise HTTPException(status_code=404, detail=f"未找到ID为 {user_strategy_id} 的用户策略")
        return {"success": True, "message": "获取用户策略详情成功", "data": user_strategy}
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_api_exception("获取用户策略详情", e)

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

        # 获取策略模板信息，以便添加类型信息
        db = next(get_db())
        try:
            strategy_template = db.query(Strategy).filter(Strategy.id == user_strategy.strategy_id).first()

            # 获取策略类型，优先使用strategy_type字段
            strategy_type = None
            if strategy_template:
                if hasattr(strategy_template, 'strategy_type') and strategy_template.strategy_type:
                    strategy_type = strategy_template.strategy_type
                elif hasattr(strategy_template, 'type') and strategy_template.type:
                    strategy_type = strategy_template.type.lower()

            # 如果策略类型仍然为空，使用默认的CTA类型
            if not strategy_type:
                strategy_type = "cta"
                logger.warning(f"策略 ID {user_strategy.strategy_id} 的类型为空，使用默认的CTA类型")

            strategy_category = strategy_template.category if strategy_template else None
            strategy_name = strategy_template.name if strategy_template else None
            strategy_identifier = strategy_template.identifier if strategy_template else None
        finally:
            db.close()

        user_strategy_dict = {
            "id": user_strategy.id,
            "user_id": user_strategy.user_id,
            "strategy_id": user_strategy.strategy_id,
            "name": user_strategy.name,
            "parameters": user_strategy.parameters,
            "created_at": user_strategy.created_at.isoformat() if user_strategy.created_at else None,
            "updated_at": user_strategy.updated_at.isoformat() if user_strategy.updated_at else None,
            "is_active": user_strategy.is_active,
            "type": strategy_type,  # 添加策略类型
            "category": strategy_category,  # 添加策略分类
            "strategy_name": strategy_name,  # 添加策略模板名称
            "identifier": strategy_identifier  # 添加策略标识符
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

        # 打印回测结果，帮助调试
        logger.info(f"回测结果: {result}")

        # 确保回测ID在响应中正确返回
        response_data = result.copy() if isinstance(result, dict) else {}

        # 如果有回测ID，将其复制到多个位置
        if "record_id" in response_data:
            record_id = response_data["record_id"]
            # 在根级别也设置回测ID
            response_data["id"] = record_id

            # 如果有统计数据，在统计数据中也设置回测ID
            if "statistics" in response_data and isinstance(response_data["statistics"], dict):
                response_data["statistics"]["record_id"] = record_id
                response_data["statistics"]["id"] = record_id

            # 打印日志，帮助调试
            logger.info(f"回测记录ID: {record_id}")

        return {"success": True, "message": "回测运行成功", "data": response_data}
    except ValueError as ve:
        logger.warning(f"回测参数错误: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        handle_api_exception("运行回测", e)

@router.get("/backtest/records", response_model=ApiResponse[PaginatedBacktestRecordsResponse])
async def get_backtest_records(
    user_id: Optional[int] = None,
    strategy_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取回测记录列表，支持分页"""
    try:
        records_data, total_count = backtest_service.get_backtest_records(
            user_id=user_id,
            strategy_id=strategy_id,
            page=page,
            page_size=page_size
        )

        # 将字典列表转换为 BacktestRecord 模型列表
        typed_records = [BacktestRecord(**record) for record in records_data]

        paginated_response = PaginatedBacktestRecordsResponse(
            total=total_count,
            records=typed_records
        )
        return {"success": True, "message": "获取回测记录列表成功", "data": paginated_response}
    except Exception as e:
        handle_api_exception("获取回测记录列表", e)

@router.get("/backtest/records/{record_id}", response_model=ApiResponse[BacktestRecord])
async def get_backtest_record(
    record_id: str,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取单个回测记录详情"""
    try:
        record_dict = backtest_service.get_backtest_record_detail(record_id)
        if not record_dict:
            raise HTTPException(status_code=404, detail=f"未找到ID为 {record_id} 的回测记录")

        # 将字典转换为 BacktestRecord 模型
        typed_record = BacktestRecord(**record_dict)
        return {"success": True, "message": "获取回测记录详情成功", "data": typed_record}
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_api_exception("获取回测记录详情", e)

@router.get("/backtest/reports/{backtest_id}", response_model=ApiResponse[BacktestReportDataModel])
async def get_backtest_report(
    backtest_id: str,
    backtest_service: BacktestService = Depends(get_backtest_service)
):
    """获取详细的回测报告数据"""
    try:
        report_data = backtest_service.get_backtest_report_data(backtest_id)
        if not report_data:
            raise HTTPException(status_code=404, detail=f"未找到ID为 {backtest_id} 的回测报告")

        return {"success": True, "message": "获取回测报告成功", "data": report_data}
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_api_exception("获取回测报告", e)

@router.get("/stock_data_range", response_model=ApiResponse)
async def get_stock_data_range(
    symbol: str,
    exchange_str: str,
    interval_str: str,
):
    """获取指定股票在VnPy数据库中的K线数据起止日期"""
    try:
        try:
            target_exchange = Exchange(exchange_str.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的交易所代码: {exchange_str}. 可选项: {', '.join([e.value for e in Exchange])}")

        try:
            target_interval = Interval(interval_str.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的K线周期: {interval_str}. 可选项: {', '.join([i.value for i in Interval])}")

        db_manager = get_database()
        if not db_manager:
            logger.error("无法获取VnPy数据库实例")
            raise HTTPException(status_code=500, detail="无法连接到数据服务")

        overviews = db_manager.get_bar_overview()

        found_overview = None
        for overview in overviews:
            if (
                overview.symbol == symbol and
                overview.exchange == target_exchange and
                overview.interval == target_interval
            ):
                found_overview = overview
                break

        if found_overview and found_overview.start and found_overview.end:
            return {
                "success": True,
                "message": "获取股票数据范围成功",
                "data": {
                    "symbol": symbol,
                    "exchange": target_exchange.value,
                    "interval": target_interval.value,
                    "start_date": found_overview.start.strftime("%Y-%m-%d"),
                    "end_date": found_overview.end.strftime("%Y-%m-%d"),
                    "count": found_overview.count
                }
            }
        else:
            return {
                "success": False,
                "message": "未找到指定股票、交易所和周期的数据范围",
                "data": None
            }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"获取股票 {symbol} 数据范围时出错: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取数据范围时发生内部错误: {str(e)}")