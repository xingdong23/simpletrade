"""
API集成测试
"""

import pytest
from datetime import datetime, timedelta
import os
from fastapi.testclient import TestClient

from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval

from simpletrade.core.data import DataManager
from simpletrade.api.data import router as data_router
from fastapi import FastAPI

@pytest.fixture
def test_client(test_db_path):
    """创建测试客户端"""
    # 创建FastAPI应用
    app = FastAPI()
    
    # 添加路由
    app.include_router(data_router)
    
    # 创建测试客户端
    client = TestClient(app)
    
    # 准备测试数据
    manager = DataManager()
    
    # 创建测试数据
    now = datetime.now()
    bar = BarData(
        symbol="TEST",
        exchange=Exchange.NASDAQ,
        datetime=now,
        interval=Interval.DAILY,
        open_price=100.0,
        high_price=110.0,
        low_price=90.0,
        close_price=105.0,
        volume=1000.0,
        open_interest=0.0
    )
    
    # 保存数据
    manager.save_bar_data([bar])
    
    return client

def test_get_overview(test_client):
    """测试获取数据概览API"""
    response = test_client.get("/api/data/overview")
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    # 验证数据
    found = False
    for item in data["data"]:
        if item["symbol"] == "TEST" and item["exchange"] == "NASDAQ" and item["interval"] == "d":
            found = True
            assert item["count"] == 1
            break
    
    assert found, "未找到测试数据"

def test_get_bars(test_client):
    """测试获取K线数据API"""
    # 构建查询参数
    now = datetime.now()
    start_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    
    response = test_client.get(
        f"/api/data/bars?symbol=TEST&exchange=NASDAQ&interval=d&start_date={start_date}&end_date={end_date}"
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    # 验证数据
    assert len(data["data"]) == 1
    bar = data["data"][0]
    assert bar["open_price"] == 100.0
    assert bar["high_price"] == 110.0
    assert bar["low_price"] == 90.0
    assert bar["close_price"] == 105.0
    assert bar["volume"] == 1000.0
