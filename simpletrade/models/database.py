"""
数据库模型模块

定义SQLAlchemy ORM模型。
"""

import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Date, Numeric, func, Index
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, VARCHAR

from simpletrade.config.database import Base

class JSONType(TypeDecorator):
    """自定义JSON类型"""
    impl = VARCHAR(4096)  # 指定最大长度为4096字符

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Symbol(Base):
    """交易品种模型"""
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )

class Strategy(Base):
    """策略模型"""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    type = Column(String(50), nullable=False)  # 'basic', 'advanced', 'component'
    complexity = Column(Integer, default=1)    # 1-5 复杂度评分
    resource_requirement = Column(Integer, default=1)  # 1-5 资源需求评分
    code = Column(Text)
    parameters = Column(JSONType)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    identifier = Column(String(100), index=True, nullable=True)

    user_strategies = relationship("UserStrategy", back_populates="strategy")
    backtest_records = relationship("BacktestRecord", back_populates="strategy")

    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )

class UserStrategy(Base):
    """用户策略模型"""
    __tablename__ = "user_strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    parameters = Column(JSONType)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    strategy = relationship("Strategy", back_populates="user_strategies")

    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )

class BacktestRecord(Base):
    """回测记录模型"""
    __tablename__ = "backtest_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    exchange = Column(String(20), nullable=False)
    interval = Column(String(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(Numeric(20, 2), nullable=False)
    final_capital = Column(Numeric(20, 2), nullable=False)
    total_return = Column(Numeric(10, 4), nullable=False)
    annual_return = Column(Numeric(10, 4))
    max_drawdown = Column(Numeric(10, 4))
    sharpe_ratio = Column(Numeric(10, 4))
    results = Column(JSONType)
    created_at = Column(DateTime, default=datetime.utcnow)

    strategy = relationship("Strategy", back_populates="backtest_records")

    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )

class DataImportLog(Base):
    """数据导入日志/状态表"""
    __tablename__ = "data_import_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True, comment="数据来源 (e.g., 'qlib', 'csv', 'yahoo')")
    symbol = Column(String(50), nullable=False, index=True)
    exchange = Column(String(50), nullable=False, index=True)
    interval = Column(String(10), nullable=False, index=True)
    # 记录从源导入到VnPy数据库的数据开始日期
    last_begin_date = Column(DateTime, nullable=True, comment="导入数据的开始日期")
    # 记录从源导入到VnPy数据库的数据结束日期
    last_end_date = Column(DateTime, nullable=True, comment="导入数据的结束日期")
    # 记录上次尝试同步的时间
    last_attempt_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="上次尝试同步时间")
    # 记录同步状态 (e.g., 'idle', 'syncing', 'success', 'failed')
    status = Column(String(20), nullable=False, default='idle', comment="同步状态")
    # 记录相关信息或错误消息
    message = Column(String(500), nullable=True, comment="同步消息或错误")

    __table_args__ = (
        # 创建联合唯一索引确保同一来源/品种/交易所/周期的记录唯一
        Index('uix_data_import_target', 'source', 'symbol', 'exchange', 'interval', unique=True),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'},
    )

    def __repr__(self):
        return f"<DataImportLog(source='{self.source}', symbol='{self.symbol}', exchange='{self.exchange}', interval='{self.interval}', range='{self.last_begin_date} to {self.last_end_date}', status='{self.status}')>"

# 注意: 添加新模型后, 可能需要数据库迁移 (如果使用 Alembic) 或手动创建表。
