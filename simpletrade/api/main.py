"""
SimpleTrade API 主程序入口
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from simpletrade.core.logging import configure_logging, get_logger
from simpletrade.core.exceptions import SimpleTradeError, handle_exception
from simpletrade.api.schemas.common import ErrorResponse
from simpletrade.api.routers import data

# 配置日志
configure_logging()
logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="SimpleTrade API",
    description="SimpleTrade交易系统API",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(data.router)

# 添加请求计时中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加处理时间头部的中间件"""
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as exc:
        # 异常记录和包装
        logger.error(f"处理请求时出错: {exc}", exc_info=True)
        process_time = time.time() - start_time
        
        # 将异常转换为SimpleTradeError
        st_error = handle_exception(exc, log_exception=True, reraise=False)
        
        # 返回JSON错误响应
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                success=False,
                message=st_error.message,
                code=st_error.code,
                details=st_error.details
            ).dict(),
            headers={"X-Process-Time": str(process_time)}
        )

# 全局异常处理
@app.exception_handler(SimpleTradeError)
async def simpletrade_exception_handler(request: Request, exc: SimpleTradeError):
    """处理SimpleTradeError异常"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message=exc.message,
            code=exc.code,
            details=exc.details
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理FastAPI的HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            code=f"HTTP{exc.status_code}",
            details={"headers": dict(exc.headers or {})}
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有其他异常"""
    # 转换为SimpleTradeError
    st_error = handle_exception(exc, log_exception=True, reraise=False)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message=st_error.message,
            code=st_error.code,
            details=st_error.details
        ).dict()
    )

# 根路由
@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "SimpleTrade API",
        "version": "0.1.0",
        "status": "running"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """API健康检查"""
    return {"status": "ok"} 