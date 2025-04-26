#!/usr/bin/env python
"""
数据管理应用测试脚本

用于测试数据管理应用的功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

from vnpy.event import EventEngine
from simpletrade.core.engine import STMainEngine
from simpletrade.apps.st_datamanager import STDataManagerApp
from simpletrade.apps.st_message import STMessageApp
from simpletrade.apps.st_message.test import run_interactive_test

def test_api():
    """测试API功能"""
    print("测试API功能")
    print("启动API服务...")

    # 创建引擎
    event_engine = EventEngine()
    main_engine = STMainEngine(event_engine)

    # 加载应用
    main_engine.add_app(STMessageApp)
    main_engine.add_app(STDataManagerApp)

    # 启动API服务
    from simpletrade.core.server import app, configure_server
    configure_server(main_engine, event_engine)
    
    # 需要使用uvicorn手动启动服务
    import uvicorn
    print("API服务已配置，启动uvicorn...")
    print("API服务已启动，访问 http://localhost:8000/docs 查看API文档")
    
    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=8000)

def test_message():
    """测试消息指令功能"""
    print("测试消息指令功能")

    # 创建引擎
    event_engine = EventEngine()
    main_engine = STMainEngine(event_engine)

    # 加载应用
    main_engine.add_app(STMessageApp)
    main_engine.add_app(STDataManagerApp)

    # 获取消息引擎
    message_engine = main_engine.get_engine("st_message")

    # 运行交互式测试
    run_interactive_test(message_engine)

if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "api":
            test_api()
        elif sys.argv[1] == "message":
            test_message()
        else:
            print(f"未知的测试类型: {sys.argv[1]}")
            print("可用的测试类型: api, message")
    else:
        print("请指定测试类型: api 或 message")
        print("示例: python scripts/test_datamanager.py api")
        print("示例: python scripts/test_datamanager.py message")
