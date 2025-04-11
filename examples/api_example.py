#!/usr/bin/env python
"""
API服务示例

展示如何启动和使用SimpleTrade的API服务。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI
import uvicorn

from simpletrade.api.data import router as data_router
from simpletrade.api.analysis import router as analysis_router

def main():
    """主函数"""
    print("SimpleTrade API服务示例")
    
    # 创建FastAPI应用
    app = FastAPI(title="SimpleTrade API")
    
    # 添加路由
    app.include_router(data_router)
    app.include_router(analysis_router)
    
    # 启动服务
    print("API服务已启动，访问 http://localhost:8000/docs 查看API文档")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
