from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, date

class BacktestReportConfigModel(BaseModel):
    """回测报告中的配置信息模型"""
    strategy_id: Optional[str] = None
    strategy_name: Optional[str] = None
    class_name: Optional[str] = None
    symbol: str
    exchange: str
    interval: str
    start_date: date
    end_date: date
    capital: float
    rate: float
    slippage: float
    mode: str
    parameters: Dict[str, Any]

    class Config:
        # 允许额外的字段
        extra = "ignore"

class EquityCurvePointModel(BaseModel):
    """资金曲线上单点的数据模型"""
    date: date # 或者 datetime，取决于回测引擎的输出精度
    equity: float

    class Config:
        # 允许额外的字段
        extra = "ignore"

class TradeDetailOutputModel(BaseModel):
    """回测报告中单笔交易的详细信息模型"""
    datetime: datetime
    symbol: str
    exchange: str
    direction: str # e.g., "多", "空" or "long", "short"
    offset: str    # e.g., "开", "平" or "open", "close"
    price: float
    volume: float
    pnl: Optional[float] = None # 单笔盈亏
    # commission: Optional[float] = None # 手续费 (如果回测引擎提供)
    # slippage_cost: Optional[float] = None # 滑点成本 (如果回测引擎提供)

    class Config:
        # 允许额外的字段
        extra = "ignore"

class BacktestReportDataModel(BaseModel):
    """完整回测报告的数据模型"""
    backtest_id: str
    ran_at: datetime # 回测执行的时间戳
    config: BacktestReportConfigModel
    summary_stats: Dict[str, Any] # Key-value 形式的统计指标
    equity_curve: List[EquityCurvePointModel]
    trades: List[TradeDetailOutputModel]
    # logs: Optional[List[str]] = None # 可选的回测日志

    class Config:
        # 允许额外的字段
        extra = "ignore"
        # 允许从字典创建模型
        orm_mode = True

class BacktestRecordOutput(BaseModel): # 用于 /api/backtest/records/{record_id}
    """单个回测记录（不含完整资金曲线和交易列表，用于列表和概览）"""
    id: str  # 通常是数据库中的id，或者一个唯一标识符
    strategy_name: Optional[str]
    symbol: str
    exchange: str
    interval: str
    start_date: date
    end_date: date
    ran_at: datetime
    total_return: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    # ... 其他关键摘要指标

    class Config:
        orm_mode = True

class PaginatedBacktestRecordsResponse(BaseModel):
    """分页回测记录响应模型"""
    total: int
    records: List[BacktestRecordOutput]
