#!/usr/bin/env python
"""
简化版数据管理应用测试脚本

用于测试数据管理应用的 API 和消息功能，不依赖于 vnpy。
"""

import sys
from pathlib import Path
import os

# 添加项目根目录到 Python 路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

def test_api_simple():
    """测试 API 功能（简化版）"""
    print("测试 API 功能（简化版）")
    
    try:
        from fastapi import FastAPI
        import uvicorn
    except ImportError:
        print("请先安装 FastAPI 和 uvicorn：")
        print("pip install fastapi uvicorn")
        return
    
    app = FastAPI(title="SimpleTrade API Test")
    
    @app.get("/")
    def read_root():
        return {"message": "SimpleTrade API 测试服务已启动"}
    
    @app.get("/api/data/test")
    def test_data_api():
        return {
            "success": True,
            "message": "数据管理 API 测试成功",
            "data": [
                {"symbol": "AAPL", "exchange": "SMART", "interval": "1d", "count": 100},
                {"symbol": "MSFT", "exchange": "SMART", "interval": "1d", "count": 100}
            ]
        }
    
    print("API 服务已启动，访问 http://localhost:8000/docs 查看 API 文档")
    uvicorn.run(app, host="0.0.0.0", port=8000)

def test_message_simple():
    """测试消息指令功能（简化版）"""
    print("测试消息指令功能（简化版）")
    print("输入消息指令进行测试，输入'exit'退出")
    print("示例: /data query")
    
    # 简单的消息处理函数
    def process_message(message):
        if message.startswith("/data"):
            parts = message.split()
            if len(parts) < 2:
                return "无效的命令格式。使用 `/data help` 获取帮助。"
            
            cmd = parts[1].lower()
            
            if cmd == "query":
                return """可用数据列表:
1. AAPL.SMART - 1d - 100条 (2023-01-01 至 2023-04-10)
2. MSFT.SMART - 1d - 100条 (2023-01-01 至 2023-04-10)
"""
            elif cmd == "help":
                return """
数据管理命令帮助:

/data query - 查询数据
/data help - 显示帮助信息
"""
            else:
                return f"未知命令: {cmd}。使用 `/data help` 获取帮助。"
        
        return "未知命令。使用 `/help` 获取帮助。"
    
    # 交互式测试循环
    while True:
        message = input("> ")
        if message.lower() == "exit":
            break
        
        result = process_message(message)
        print(result or "无响应")

if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "api":
            test_api_simple()
        elif sys.argv[1] == "message":
            test_message_simple()
        else:
            print(f"未知的测试类型: {sys.argv[1]}")
            print("可用的测试类型: api, message")
    else:
        print("请指定测试类型: api 或 message")
        print("示例: python scripts/test_datamanager_simple.py api")
        print("示例: python scripts/test_datamanager_simple.py message")
