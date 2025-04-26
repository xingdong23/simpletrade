"""
SimpleTrade 核心服务器模块

提供RESTful API服务器初始化和配置功能。
"""

import logging
import traceback
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from simpletrade.config.database import engine, Base

# 创建FastAPI应用实例
app = FastAPI(title="SimpleTrade API", version="0.1.0")

# 获取日志记录器
logger = logging.getLogger("simpletrade.core.server")
logger.setLevel(logging.DEBUG)

def configure_server(main_engine=None, event_engine=None):
    """
    配置FastAPI应用实例
    
    Args:
        main_engine: 主引擎实例
        event_engine: 事件引擎实例
    """
    logger.debug("开始配置FastAPI应用...")

    # 初始化数据库表
    _initialize_database()
    
    # 配置CORS中间件
    _configure_cors()
    
    # 存储引擎实例
    _setup_engines(main_engine, event_engine)
    
    # 注册API路由
    _register_routes()
    
    logger.info("FastAPI应用配置完成")

def _initialize_database():
    """初始化数据库表"""
    try:
        logger.info("创建数据库表...")
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建/检查完成")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}", exc_info=True)
        # 这里不抛出异常，让应用继续启动，因为可能只是部分表创建失败

def _configure_cors():
    """配置CORS中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源，生产环境应该限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug("CORS中间件配置完成")

def _setup_engines(main_engine, event_engine):
    """
    设置引擎实例到app.state
    
    Args:
        main_engine: 主引擎实例
        event_engine: 事件引擎实例
    """
    # 存储主引擎
    if main_engine:
        logger.debug(f"使用主引擎: {main_engine}")
        app.state.main_engine = main_engine
        
        # 检查可用网关
        try:
            all_gateways = main_engine.get_all_gateway_names()
            logger.debug(f"可用网关: {all_gateways}")
        except Exception as e:
            logger.warning(f"无法获取网关名称: {e}")
    else:
        logger.warning("未提供主引擎!")
        app.state.main_engine = None
    
    # 存储事件引擎
    if event_engine:
        app.state.event_engine = event_engine
        logger.debug("事件引擎已存储")
    else:
        app.state.event_engine = None
        logger.warning("未提供事件引擎!")

def _register_routes():
    """注册所有API路由"""
    _register_data_routes()
    _register_wechat_routes()
    _register_analysis_routes()
    _register_strategy_routes()

def _register_data_routes():
    """注册数据管理API路由"""
    try:
        from simpletrade.apps.st_datamanager.api import router as data_router
        app.include_router(data_router)
        logger.debug("数据管理API路由已添加")
    except Exception as e:
        _log_router_error("数据管理API", e)

def _register_wechat_routes():
    """注册微信小程序API路由"""
    try:
        from simpletrade.api.wechat import auth_router, data_router as wechat_data_router
        app.include_router(auth_router)
        app.include_router(wechat_data_router)
        logger.debug("微信小程序API路由已添加")
    except Exception as e:
        _log_router_error("微信小程序API", e)

def _register_analysis_routes():
    """注册分析API路由"""
    try:
        from simpletrade.apps.st_analysis.api import router as analysis_router
        app.include_router(analysis_router)
        logger.debug("分析API路由已添加")
    except Exception as e:
        _log_router_error("分析API", e)

def _register_strategy_routes():
    """注册策略API路由"""
    try:
        from simpletrade.api.routers.strategies import router as strategies_router
        app.include_router(strategies_router)
        logger.debug("策略API路由已添加")
    except Exception as e:
        _log_router_error("策略API", e)

def _log_router_error(router_name, error):
    """记录路由器注册错误"""
    error_msg = f"{router_name}路由注册失败: {error}\n{traceback.format_exc()}"
    logger.error(error_msg) 