"""
SimpleTrade 数据库核心模块

提供数据库连接和会话管理功能。
"""

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 后续会从配置模块导入
from simpletrade.config.settings import DB_CONFIG

logger = logging.getLogger(__name__)

# 创建数据库URL
db_url = f"mysql+pymysql://{DB_CONFIG['DB_USER']}:{DB_CONFIG['DB_PASSWORD']}@{DB_CONFIG['DB_HOST']}:{DB_CONFIG['DB_PORT']}/{DB_CONFIG['DB_NAME']}"

# 创建数据库引擎
try:
    engine = create_engine(
        db_url,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=False
    )
    logger.info("数据库引擎创建成功")
except Exception as e:
    logger.error(f"创建数据库引擎失败: {e}", exc_info=True)
    raise

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话，完成后自动关闭
    
    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    初始化数据库，创建所有表
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表初始化成功")
    except Exception as e:
        logger.error(f"数据库表初始化失败: {e}", exc_info=True)
        raise 