"""
SimpleTrade分析API

提供数据分析功能的RESTful API接口。
直接使用vnpy的数据模型和数据管理功能。
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field

# 导入vnpy的数据模型和数据管理功能
from vnpy.trader.object import BarData as VnpyBarData, TickData
from vnpy.trader.constant import Exchange, Interval

# 导入分析功能和数据管理引擎 App
from simpletrade.core.analysis import calculate_indicators, backtest_strategy
from simpletrade.core.analysis.visualization import generate_backtest_report
from simpletrade.services.backtest_service import BacktestService
from simpletrade.apps.st_datamanager.api.routes import get_data_manager_engine # 导入用于依赖注入的函数

# 创建路由器
router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# 数据模型
class IndicatorRequest(BaseModel):
    """技术指标请求"""
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: Optional[str] = None
    indicators: List[Dict[str, Any]]

class BacktestRequest(BaseModel):
    """回测请求"""
    symbol: str
    exchange: str
    interval: str
    start_date: str
    end_date: Optional[str] = None
    strategy_name: str
    strategy_params: Dict[str, Any]
    indicators: Optional[List[Dict[str, Any]]] = None
    initial_capital: float = 100000.0

class ApiResponse(BaseModel):
    """API响应"""
    success: bool
    message: str
    data: Optional[Any] = None

# API路由
@router.get("/indicators", response_model=ApiResponse)
async def get_available_indicators():
    """获取可用的技术指标列表"""
    try:
        # 这里列出所有可用的技术指标
        available_indicators = [
            {
                "name": "SMA",
                "description": "简单移动平均线",
                "parameters": [
                    {"name": "period", "type": "int", "default": 20, "description": "周期"}
                ]
            },
            {
                "name": "EMA",
                "description": "指数移动平均线",
                "parameters": [
                    {"name": "period", "type": "int", "default": 20, "description": "周期"}
                ]
            },
            {
                "name": "RSI",
                "description": "相对强弱指数",
                "parameters": [
                    {"name": "period", "type": "int", "default": 14, "description": "周期"}
                ]
            },
            {
                "name": "MACD",
                "description": "平滑异同移动平均线",
                "parameters": [
                    {"name": "fast_period", "type": "int", "default": 12, "description": "快线周期"},
                    {"name": "slow_period", "type": "int", "default": 26, "description": "慢线周期"},
                    {"name": "signal_period", "type": "int", "default": 9, "description": "信号周期"}
                ]
            },
            {
                "name": "BOLL",
                "description": "布林线",
                "parameters": [
                    {"name": "period", "type": "int", "default": 20, "description": "周期"},
                    {"name": "std_dev", "type": "float", "default": 2.0, "description": "标准差倍数"}
                ]
            },
            {
                "name": "KDJ",
                "description": "KDJ随机指标",
                "parameters": [
                    {"name": "k_period", "type": "int", "default": 9, "description": "K线周期"},
                    {"name": "d_period", "type": "int", "default": 3, "description": "D线周期"},
                    {"name": "j_period", "type": "int", "default": 3, "description": "J线周期"}
                ]
            }
        ]

        return {
            "success": True,
            "message": f"获取可用指标成功，共 {len(available_indicators)} 个",
            "data": available_indicators
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取可用指标失败: {str(e)}"
        }

@router.post("/indicators", response_model=ApiResponse)
async def calculate_technical_indicators(request: IndicatorRequest, engine = Depends(get_data_manager_engine)):
    """计算技术指标"""
    if not engine:
        logger.error("Data manager engine not available.")
        raise HTTPException(status_code=500, detail="数据管理引擎不可用")
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)
        interval_obj = Interval(request.interval)
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.now()
        if request.end_date:
            end = datetime.strptime(request.end_date, "%Y-%m-%d")

        # 加载数据 (使用注入的引擎)
        bars: List[VnpyBarData] = engine.get_bar_data(
            symbol=request.symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            start=start,
            end=end
        )

        if not bars:
            return {
                "success": False,
                "message": "未找到符合条件的数据"
            }

        # 计算技术指标
        df = calculate_indicators(bars, request.indicators)

        # 转换为JSON可序列化格式
        result = []
        for index, row in df.iterrows():
            data = {
                "datetime": index.strftime("%Y-%m-%d %H:%M:%S"),
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"]
            }

            # 添加技术指标
            for col in df.columns:
                if col not in ["open", "high", "low", "close", "volume", "open_interest"]:
                    data[col] = row[col]

            result.append(data)

        return {
            "success": True,
            "message": f"计算技术指标成功，共 {len(result)} 条数据",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"计算技术指标失败: {str(e)}"
        }

@router.post("/backtest", response_model=ApiResponse)
async def run_strategy_backtest(request: BacktestRequest, engine = Depends(get_data_manager_engine)):
    """运行策略回测"""
    if not engine:
        logger.error("Data manager engine not available.")
        raise HTTPException(status_code=500, detail="数据管理引擎不可用")
    try:
        # 解析参数
        exchange_obj = Exchange(request.exchange)
        interval_obj = Interval(request.interval)
        start = datetime.strptime(request.start_date, "%Y-%m-%d")
        end = datetime.now()
        if request.end_date:
            end = datetime.strptime(request.end_date, "%Y-%m-%d")

        # 加载数据 (使用注入的引擎)
        bars: List[VnpyBarData] = engine.get_bar_data(
            symbol=request.symbol,
            exchange=exchange_obj,
            interval=interval_obj,
            start=start,
            end=end
        )

        if not bars:
            return {
                "success": False,
                "message": "未找到符合条件的数据"
            }

        # 运行回测
        result = backtest_strategy(
            bars=bars,
            strategy_name=request.strategy_name,
            strategy_params=request.strategy_params,
            indicators=request.indicators,
            initial_capital=request.initial_capital
        )

        if not result:
            return {
                "success": False,
                "message": "回测失败"
            }

        # 获取回测结果
        backtest_result = result.to_dict()

        # 获取交易记录
        trades = []
        for index, row in result.df.iterrows():
            if row["position_change"] != 0:
                trade = {
                    "datetime": index.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "买入" if row["position_change"] > 0 else "卖出",
                    "price": row["close"],
                    "profit": row["trade_profit"] if "trade_profit" in row else 0
                }
                trades.append(trade)

        # 获取资金曲线
        equity_curve = []
        for index, row in result.df.iterrows():
            if "capital" in row:
                point = {
                    "datetime": index.strftime("%Y-%m-%d %H:%M:%S"),
                    "capital": row["capital"],
                    "drawdown": row["drawdown"] if "drawdown" in row else 0,
                    "drawdown_pct": row["drawdown_pct"] if "drawdown_pct" in row else 0
                }
                equity_curve.append(point)

        return {
            "success": True,
            "message": "回测成功",
            "data": {
                "summary": backtest_result,
                "trades": trades,
                "equity_curve": equity_curve
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"回测失败: {str(e)}"
        }
