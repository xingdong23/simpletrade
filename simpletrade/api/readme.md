# SimpleTrade API 包

SimpleTrade API 包是 SimpleTrade 交易平台的 API 服务模块，提供 RESTful API 接口，用于访问 SimpleTrade 的各种功能。

## 主要文件和模块

1. **server.py** - API 服务的主要入口点
   - 创建和配置 FastAPI 应用实例
   - 添加中间件（如 CORS）
   - 注册各种路由器

2. **deps.py** - 依赖项注入模块
   - 提供数据库会话等依赖项

3. **routers/** - 路由器目录，包含各种 API 端点
   - **misc.py** - 包含测试和健康检查路由
   - **analysis.py** - 提供数据分析功能的 API
   - **strategies.py** - 策略管理相关的 API
   - **wechat/** - 微信小程序相关的 API

4. **wechat/** - 微信小程序接口
   - **auth.py** - 认证相关的 API
   - **data.py** - 数据相关的 API

## API 功能概览

1. **数据管理 API**
   - 获取数据概览
   - 获取 K 线数据
   - 获取 Tick 数据
   - 导入数据

2. **分析 API**
   - 计算技术指标
   - 回测策略

3. **策略 API**
   - 管理交易策略
   - 配置策略参数

4. **微信小程序 API**
   - 用户认证
   - 数据访问

5. **测试和健康检查 API**
   - `/api/test/hello` - 简单的测试端点
   - `/api/test/info` - 返回 API 版本信息
   - `/api/health/` - 健康检查端点

## 技术栈

- **Web 框架**: FastAPI
- **ASGI 服务器**: Uvicorn
- **数据验证**: Pydantic
- **数据库 ORM**: SQLAlchemy

## 使用方法

API 服务可以通过以下方式启动：

```bash
python -m uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8002 --reload
```

启动后，可以通过访问 `http://localhost:8002/docs` 查看 API 文档。