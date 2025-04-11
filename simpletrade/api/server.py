"""
SimpleTrade API服务

提供RESTful API服务，用于访问SimpleTrade的功能。
"""

from fastapi import FastAPI, APIRouter
import uvicorn

class APIServer:
    """SimpleTrade API服务"""

    def __init__(self, host="0.0.0.0", port=8000):
        """初始化"""
        self.host = host
        self.port = port
        self.app = FastAPI(title="SimpleTrade API", version="0.1.0")
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

def create_server(main_engine=None, event_engine=None):
    """创建API服务器"""
    server = APIServer()

    # 添加数据管理API路由
    try:
        from simpletrade.apps.st_datamanager.api import router as data_router
        server.add_router(data_router)
        print("Data management API routes added.")
    except Exception as e:
        print(f"Failed to add data management API routes: {e}")

    # 添加独立数据API路由
    try:
        from simpletrade.api.data import router as core_data_router
        server.add_router(core_data_router)
        print("Core data API routes added.")
    except Exception as e:
        print(f"Failed to add core data API routes: {e}")

    # 添加微信小程序API路由
    try:
        from simpletrade.api.wechat import auth_router, data_router as wechat_data_router
        server.add_router(auth_router)
        server.add_router(wechat_data_router)
        print("WeChat Mini Program API routes added.")
    except Exception as e:
        print(f"Failed to add WeChat Mini Program API routes: {e}")

    # 添加分析API路由
    try:
        from simpletrade.api.analysis import router as analysis_router
        server.add_router(analysis_router)
        print("Analysis API routes added.")
    except Exception as e:
        print(f"Failed to add Analysis API routes: {e}")

    return server

# 创建FastAPI应用实例，用于uvicorn直接运行
server = create_server()
app = server.app
