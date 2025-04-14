#!/usr/bin/env python
"""
简单API测试

启动一个最简单的FastAPI服务器，用于测试。
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "API服务正常运行"}

if __name__ == "__main__":
    print("启动简单API测试服务器...")
    print("访问 http://localhost:8000/ 查看API")
    uvicorn.run(app, host="0.0.0.0", port=8000)
