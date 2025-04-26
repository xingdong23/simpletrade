from simpletrade.config.database import SessionLocal # Need SessionLocal
import logging
import traceback
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def get_db():
    """FastAPI 依赖项：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def handle_api_exception(func_name: str, exc: Exception) -> None:
    """统一处理API异常并记录日志"""
    error_msg = f"{func_name}失败: {exc}\n{traceback.format_exc()}"
    logger.error(error_msg)
    if isinstance(exc, HTTPException):
        raise exc
    raise HTTPException(status_code=500, detail=f"操作失败: {str(exc)}")

# Add other dependencies here later if needed
# e.g., def get_current_user(...) 