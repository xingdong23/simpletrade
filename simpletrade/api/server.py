"""
SimpleTrade API服务

提供RESTful API服务，用于访问SimpleTrade的功能。
"""

import os  # 添加这行导入
import sys
from pathlib import Path
from fastapi import FastAPI, APIRouter
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from simpletrade.services.data_sync_service import run_initial_data_sync # Import the sync function
# Import database engine and Base
from simpletrade.config.database import engine, Base
import logging # Re-add missing import
from fastapi import FastAPI # Ensure FastAPI is imported
import asyncio # Re-import asyncio
# APIServer 类不再需要，因为 app 是外部传入的
# class APIServer:
#     ...

# 创建一个简单的测试路由
test_router = APIRouter(prefix="/api/test", tags=["test"])

@test_router.get("/hello")
async def hello():
    return {"message": "Hello from SimpleTrade API!"}

@test_router.get("/info")
async def info():
    return {
        "status": "ok",
        "version": "0.1.0",
        "api": "SimpleTrade API",
        "time": "2024-04-17"
    }

# --- Lifespan Function Removed (using background thread in run_api.py) ---

# 修改函数签名，接收 FastAPI app 实例
def configure_server(app: FastAPI, main_engine=None, event_engine=None):
    """配置现有的 FastAPI 应用实例"""
    logger = logging.getLogger("simpletrade.api.server")
    logger.setLevel(logging.DEBUG) # 保持日志级别
    logger.debug("Configuring FastAPI app instance...")

    # --- Create Database Tables (if they don't exist) ---
    try:
        logger.info("Attempting to create database tables based on models...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables check/creation complete.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}", exc_info=True)
        # Decide if you want to proceed or raise the error depending on severity
    # --- End Create Database Tables ---

    # 添加CORS中间件 (移到这里配置)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有方法
        allow_headers=["*"],  # 允许所有头
    )
    logger.debug("CORS middleware added.")

    # 添加测试路由
    app.include_router(test_router)
    print("Test API routes added successfully.")

    # 添加健康检查路由
    health_router = APIRouter(prefix="/api/health", tags=["health"])

    @health_router.get("/")
    async def health_check():
        return {"status": "ok", "message": "API服务正常运行"}

    app.include_router(health_router)
    print("Health check API route added.")

    # 检查main_engine是否已初始化
    if main_engine:
        logger.debug(f"Using provided main_engine: {main_engine}")
    else:
        # 如果没有 main_engine，可能需要引发错误或有默认行为
        logger.warning("No main_engine provided during configuration!") 

    # 将 main_engine 存储到 app state 中，供依赖注入使用
    # app = server.app # app 是传入的
    app.state.main_engine = main_engine
    logger.debug("Main engine stored in app state.")

    # 检查可用的网关
    try:
        if main_engine:
             all_gateways = main_engine.get_all_gateway_names()
             logger.debug(f"Available gateways: {all_gateways}")
        else:
             logger.warning("Cannot get gateway names without main_engine.")
    except Exception as e:
        logger.warning(f"Could not get gateway names (might be harmless): {e}")

    # 添加数据管理API路由
    try:
        from simpletrade.apps.st_datamanager.api import router as data_router
        app.include_router(data_router)
        logger.debug("Data management API routes added.")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add data management API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)

    # 添加微信小程序API路由
    try:
        from simpletrade.api.wechat import auth_router, data_router as wechat_data_router
        app.include_router(auth_router)
        app.include_router(wechat_data_router)
        print("WeChat Mini Program API routes added.")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add WeChat Mini Program API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)

    # 添加分析API路由
    try:
        from simpletrade.api.analysis import router as analysis_router
        app.include_router(analysis_router)
        print("Analysis API routes added.")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add Analysis API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)

    # 添加策略API路由
    try:
        from simpletrade.api.strategies import router as strategies_router
        app.include_router(strategies_router)
        print("Strategies API routes added.")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add Strategies API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)

    # 不再需要返回 server 对象
    # return server

# 移除全局服务器和 app 创建
# server = create_server()
# app = server.app
