"""
回测API Schema定义
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator

class BacktestRequest(BaseModel):
    """回测请求模型"""
    strategy_id: int = Field(..., description="策略ID")
    symbol: str = Field(..., description="合约代码")
    exchange: str = Field(..., description="交易所")
    interval: str = Field(..., description="K线周期")
    start_date: str = Field(..., description="开始日期 (YYYY-MM-DD)")
    end_date: str = Field(..., description="结束日期 (YYYY-MM-DD)")
    initial_capital: float = Field(100000.0, description="初始资金")
    rate: float = Field(0.0, description="手续费率")
    slippage: float = Field(0.0, description="滑点")
    parameters: Optional[Dict[str, Any]] = Field(None, description="自定义策略参数")
    user_id: Optional[int] = Field(None, description="用户ID")
    
    @validator('start_date', 'end_date')
    def validate_date(cls, v):
        """验证日期格式"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("日期格式必须为YYYY-MM-DD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy_id": 1,
                "symbol": "BTCUSDT",
                "exchange": "BINANCE",
                "interval": "1d",
                "start_date": "2022-01-01",
                "end_date": "2022-12-31",
                "initial_capital": 100000.0,
                "rate": 0.001,
                "slippage": 0.0,
                "parameters": {
                    "fast_window": 5,
                    "slow_window": 20
                },
                "user_id": 1
            }
        }

class BacktestResult(BaseModel):
    """回测结果模型"""
    id: int = Field(..., description="回测记录ID")
    strategy_id: int = Field(..., description="策略ID")
    symbol: str = Field(..., description="合约代码")
    exchange: str = Field(..., description="交易所")
    interval: str = Field(..., description="K线周期")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    initial_capital: float = Field(..., description="初始资金")
    final_capital: float = Field(..., description="最终资金")
    total_return: float = Field(..., description="总收益率")
    annual_return: float = Field(..., description="年化收益率")
    max_drawdown: float = Field(..., description="最大回撤")
    sharpe_ratio: float = Field(..., description="夏普比率")
    total_trades: int = Field(..., description="总交易次数")
    win_trades: int = Field(..., description="盈利交易次数")
    loss_trades: int = Field(..., description="亏损交易次数")
    win_rate: float = Field(..., description="胜率")
    trade_records: Optional[List[Dict[str, Any]]] = Field(None, description="交易记录")
    equity_curve: Optional[Dict[str, Any]] = Field(None, description="权益曲线")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "strategy_id": 1,
                "symbol": "BTCUSDT",
                "exchange": "BINANCE",
                "interval": "1d",
                "start_date": "2022-01-01",
                "end_date": "2022-12-31",
                "initial_capital": 100000.0,
                "final_capital": 120000.0,
                "total_return": 0.2,
                "annual_return": 0.3,
                "max_drawdown": 0.1,
                "sharpe_ratio": 1.5,
                "total_trades": 50,
                "win_trades": 30,
                "loss_trades": 20,
                "win_rate": 0.6,
                "trade_records": None,
                "equity_curve": None
            }
        } 