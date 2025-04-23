"""
SimpleTrade API服务

提供RESTful API服务，用于访问SimpleTrade的功能。
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, APIRouter
# import uvicorn # No longer needed here
from fastapi.middleware.cors import CORSMiddleware
# from simpletrade.services.data_sync_service import run_initial_data_sync # Not used directly here
from simpletrade.config.database import engine, Base
import logging
# from fastapi import FastAPI # Already imported
import asyncio

# +++ 在模块顶部创建 FastAPI 实例 +++
app = FastAPI(title="SimpleTrade API", version="0.1.0")
# +++ 结束 FastAPI 实例创建 +++

# --- test_router definition removed ---

# --- Lifespan Function Removed (using background thread in run_api.py) ---

# --- 修改函数签名，不再接收 app 参数 --- 
# 它将配置在上面定义的全局 app 实例
def configure_server(main_engine=None, event_engine=None):
    """配置全局 FastAPI 应用实例 (app)"""
    logger = logging.getLogger("simpletrade.api.server")
    logger.setLevel(logging.DEBUG) # 保持日志级别
    logger.debug("Configuring global FastAPI app instance (app)...")

    # --- Create Database Tables (if they don't exist) ---
    try:
        logger.info("Attempting to create database tables based on models...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables check/creation complete.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}", exc_info=True)
        # Decide if you want to proceed or raise the error depending on severity
    # --- End Create Database Tables ---

    # --- 添加CORS中间件 (现在配置全局 app) ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有方法
        allow_headers=["*"],  # 允许所有头
    )
    logger.debug("CORS middleware added to global app.")

    # --- 添加路由 (稍后统一更新导入和注册) ---
    # app.include_router(test_router) # Removed definition
    logger.debug("Test API routes will be added later.")

    # --- health_router definition removed ---

    # app.include_router(health_router) # Removed definition
    logger.debug("Health check API route will be added later.")

    # --- 检查和存储 main_engine 到 app.state (保持不变) ---
    if main_engine:
        logger.debug(f"Using provided main_engine: {main_engine}")
        app.state.main_engine = main_engine # 存储到全局 app 的 state
        logger.debug("Main engine stored in global app state.")
        # 检查可用网关 (保持不变)
        try:
            all_gateways = main_engine.get_all_gateway_names()
            logger.debug(f"Available gateways: {all_gateways}")
        except Exception as e:
            logger.warning(f"Could not get gateway names: {e}")
    else:
        logger.warning("No main_engine provided during configuration!") 
        app.state.main_engine = None # 明确设置为空

    # --- 添加其他 API 路由 (现在配置全局 app) ---
    # 数据管理API (稍后更新导入)
    try:
        # TODO: Update import path if data router is moved/proxied
        from simpletrade.apps.st_datamanager.api import router as data_router
        app.include_router(data_router)
        logger.debug("Data management API routes added (placeholder import).")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add data management API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)
        pass # Avoid stopping config due to import error during refactor

    # 微信小程序API (稍后更新导入)
    try:
        # TODO: Update import path if wechat router is moved
        from simpletrade.api.wechat import auth_router, data_router as wechat_data_router
        app.include_router(auth_router)
        app.include_router(wechat_data_router)
        logger.debug("WeChat Mini Program API routes added (placeholder import).")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add WeChat Mini Program API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)
        pass # Avoid stopping config

    # 分析API (稍后更新导入)
    try:
        # TODO: Update import path to routers/analysis.py
        from simpletrade.api.analysis import router as analysis_router # Old path
        app.include_router(analysis_router)
        logger.debug("Analysis API routes added (placeholder import).")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add Analysis API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)
        pass # Avoid stopping config

    # 策略API (稍后更新导入)
    try:
        # TODO: Update import path to routers/strategies.py
        from simpletrade.api.strategies import router as strategies_router # Old path
        app.include_router(strategies_router)
        logger.debug("Strategies API routes added (placeholder import).")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add Strategies API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)
        pass # Avoid stopping config

    # --- 结束路由添加 --- 

    logger.info("Global FastAPI app configuration complete (router includes pending update).")

# --- 不再需要 create_server 函数和全局 server 变量 ---
