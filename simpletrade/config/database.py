"""
数据库配置模块

提供数据库连接配置和连接池管理。
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# 导入配置
from simpletrade.config.settings import DB_CONFIG

# 设置日志
logger = logging.getLogger("simpletrade.config.database")

# 从配置文件获取数据库连接参数
DB_USER = DB_CONFIG["DB_USER"]
DB_PASSWORD = DB_CONFIG["DB_PASSWORD"]
DB_HOST = DB_CONFIG["DB_HOST"]
DB_PORT = DB_CONFIG["DB_PORT"]
DB_NAME = DB_CONFIG["DB_NAME"]
POOL_SIZE = DB_CONFIG["POOL_SIZE"]
MAX_OVERFLOW = DB_CONFIG["MAX_OVERFLOW"]
POOL_RECYCLE = DB_CONFIG["POOL_RECYCLE"]
ECHO = DB_CONFIG["ECHO"]

# 构建数据库连接URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 记录数据库连接信息
logger.info(f"Connecting to database: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,
    echo=ECHO  # 设置为True可以查看SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类，用于创建模型类
Base = declarative_base()

def get_db():
    """FastAPI 依赖项：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
