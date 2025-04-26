"""
SimpleTrade 策略模块数据模型

定义策略相关的Pydantic数据模型，用于API请求和响应的验证和序列化。
"""

from datetime import date
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# 通用API响应模型
class ApiResponse(BaseModel):
    """API响应模型"""
    success: bool
    message: str
    data: Optional[Any] = None

# 策略参数模型
class StrategyParameter(BaseModel):
    """策略参数模型"""
    type: str
    default: Any
    min: Optional[Any] = None
    max: Optional[Any] = None
    options: Optional[List[str]] = None
    description: str

# 策略模型
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

# 创建策略请求模型
class CreateStrategyRequest(BaseModel):
    """创建策略请求模型"""
    name: str
    description: Optional[str] = None
    type: str
    category: Optional[str] = None
    parameters: Dict[str, Any]

# 创建用户策略请求模型
class CreateUserStrategyRequest(BaseModel):
    """创建用户策略请求模型"""
    user_id: int
    strategy_id: int
    name: str
    parameters: Dict[str, Any]

# 回测请求模型
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

# 用户策略详情模型
class UserStrategyDetail(BaseModel):
    """用户策略详情模型"""
    id: int
    user_id: int
    strategy_id: int
    name: str
    parameters: Dict[str, Any]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: bool

# 回测记录模型
class BacktestRecord(BaseModel):
    """回测记录模型"""
    id: int
    user_id: int
    strategy_id: int
    symbol: str
    exchange: str
    interval: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    initial_capital: Optional[float] = None
    final_capital: Optional[float] = None
    total_return: Optional[float] = None
    annual_return: Optional[float] = None
    max_drawdown: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None 