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
class APIServer:
    """SimpleTrade API服务"""

    def __init__(self, host="0.0.0.0", port=8000):
        """初始化"""
        self.host = host
        self.port = port
        self.app = FastAPI(title="SimpleTrade API", version="0.1.0")

        # 添加CORS中间件，允许所有来源的跨域请求
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 允许所有来源
            allow_credentials=True,
            allow_methods=["*"],  # 允许所有方法
            allow_headers=["*"],  # 允许所有头
        )

        self.routers = []

    def add_router(self, router: APIRouter):
        """添加路由器"""
        self.app.include_router(router)
        self.routers.append(router)

    def start(self):
        """启动服务"""
        uvicorn.run(self.app, host=self.host, port=self.port)

    def stop(self):
        """停止服务"""
        # uvicorn没有提供优雅停止的API，这里只是占位
        pass

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

def create_server(main_engine=None, event_engine=None):
    """创建API服务器"""
    import logging
    logger = logging.getLogger("simpletrade.api.server")
    logger.setLevel(logging.DEBUG)

    server = APIServer()
    logger.debug("API Server created")

    # 添加测试路由
    server.add_router(test_router)
    print("Test API routes added successfully.")

    # 添加健康检查路由
    health_router = APIRouter(prefix="/api/health", tags=["health"])

    @health_router.get("/")
    async def health_check():
        return {"status": "ok", "message": "API服务正常运行"}

    server.add_router(health_router)
    print("Health check API route added.")

    # 检查main_engine是否已初始化
    if main_engine:
        logger.debug(f"Using provided main_engine: {main_engine}")
    else:
        logger.debug("No main_engine provided, using global instance from simpletrade.main")
        try:
            from simpletrade.main import main_engine as global_main_engine
            main_engine = global_main_engine
            logger.debug(f"Global main_engine loaded: {main_engine}")

            # 检查可用的网关
            all_gateways = main_engine.get_all_gateway_names()
            logger.debug(f"Available gateways: {all_gateways}")
        except Exception as e:
            logger.error(f"Failed to load global main_engine: {e}")

    # 添加数据管理API路由
    try:
        from simpletrade.apps.st_datamanager.api import router as data_router
        server.add_router(data_router)
        logger.debug("Data management API routes added.")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add data management API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)

    # 添加微信小程序API路由
    try:
        from simpletrade.api.wechat import auth_router, data_router as wechat_data_router
        server.add_router(auth_router)
        server.add_router(wechat_data_router)
        print("WeChat Mini Program API routes added.")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add WeChat Mini Program API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)

    # 添加分析API路由
    try:
        from simpletrade.api.analysis import router as analysis_router
        server.add_router(analysis_router)
        print("Analysis API routes added.")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add Analysis API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)

    # 添加策略API路由
    try:
        from simpletrade.api.strategies import router as strategies_router
        server.add_router(strategies_router)
        print("Strategies API routes added.")
    except Exception as e:
        import traceback
        error_msg = f"Failed to add Strategies API routes: {e}\n{traceback.format_exc()}"
        logger.error(error_msg)
        print(error_msg)

    return server

# 创建FastAPI应用实例，用于uvicorn直接运行
server = create_server()
app = server.app
