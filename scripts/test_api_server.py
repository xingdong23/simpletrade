#!/usr/bin/env python
"""
测试API服务器

启动一个简化版的API服务器，只包含基本功能，不依赖于talib。
"""

import sys
import os
from pathlib import Path
import logging
import uvicorn
from fastapi import FastAPI, APIRouter

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_api_server")

# 创建FastAPI应用
app = FastAPI(title="SimpleTrade API (Test)", version="0.1.0")

# 添加CORS中间件
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建测试路由
test_router = APIRouter(prefix="/api/test", tags=["test"])

@test_router.get("/hello")
async def hello():
    return {"message": "Hello from SimpleTrade API!"}

@test_router.get("/info")
async def info():
    return {
        "status": "ok",
        "version": "0.1.0",
        "api": "SimpleTrade API (Test)",
        "time": "2024-04-17"
    }

# 创建健康检查路由
health_router = APIRouter(prefix="/api/health", tags=["health"])

@health_router.get("/")
async def health_check():
    return {"status": "ok", "message": "API服务正常运行"}

# 创建数据路由
data_router = APIRouter(prefix="/api/data", tags=["data"])

@data_router.get("/symbols")
async def get_symbols():
    """获取可用的交易品种列表"""
    # 返回一些测试数据
    symbols = [
        {"symbol": "AAPL", "exchange": "SMART", "name": "Apple Inc."},
        {"symbol": "MSFT", "exchange": "SMART", "name": "Microsoft Corporation"},
        {"symbol": "GOOG", "exchange": "SMART", "name": "Alphabet Inc."},
        {"symbol": "AMZN", "exchange": "SMART", "name": "Amazon.com, Inc."},
        {"symbol": "FB", "exchange": "SMART", "name": "Meta Platforms, Inc."}
    ]
    return {
        "success": True,
        "message": f"获取交易品种成功，共 {len(symbols)} 个",
        "data": symbols
    }

@data_router.get("/bars/{symbol}")
async def get_bars(symbol: str, exchange: str = "SMART", interval: str = "1d", limit: int = 100):
    """获取K线数据"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 生成一些测试数据
    end_date = datetime.now()
    dates = [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(limit)]
    dates.reverse()

    # 生成随机价格
    np.random.seed(42)  # 固定随机种子，使结果可重现
    close_prices = np.random.normal(100, 5, limit).cumsum()
    close_prices = np.abs(close_prices) + 50  # 确保价格为正

    # 生成其他价格
    open_prices = close_prices * np.random.uniform(0.98, 1.02, limit)
    high_prices = np.maximum(close_prices, open_prices) * np.random.uniform(1.0, 1.05, limit)
    low_prices = np.minimum(close_prices, open_prices) * np.random.uniform(0.95, 1.0, limit)
    volumes = np.random.randint(1000, 10000, limit)

    # 创建K线数据
    bars = []
    for i in range(limit):
        bar = {
            "datetime": dates[i],
            "open": round(open_prices[i], 2),
            "high": round(high_prices[i], 2),
            "low": round(low_prices[i], 2),
            "close": round(close_prices[i], 2),
            "volume": int(volumes[i])
        }
        bars.append(bar)

    return {
        "success": True,
        "message": f"获取K线数据成功，共 {len(bars)} 条",
        "data": bars
    }

# 添加路由
app.include_router(test_router)
app.include_router(health_router)
app.include_router(data_router)

if __name__ == "__main__":
    print("启动测试API服务器...")
    logger.info("启动测试API服务器...")
    print("API服务器地址: http://localhost:8000")
    print("API文档地址: http://localhost:8000/docs")
    print("健康检查地址: http://localhost:8000/api/health")
    print("测试接口地址: http://localhost:8000/api/test/hello")
    print("按Ctrl+C停止服务")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
