"""
数据库模型模块

定义SQLAlchemy ORM模型。
"""

import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Date, Numeric
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
