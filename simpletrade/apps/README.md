# SimpleTrade 应用模块

SimpleTrade 应用模块包含了 SimpleTrade 交易平台的各种功能应用。这些应用基于 vnpy 的应用框架，但进行了扩展和增强，以提供更多功能和更好的用户体验。

## 应用概览

SimpleTrade 应用模块目前包含以下主要应用：

1. **st_datamanager** - 数据管理应用
2. **st_message** - 消息系统应用
3. **st_trader** - 交易增强应用

## 应用架构

所有 SimpleTrade 应用都继承自 `simpletrade.core.app.STBaseApp` 基类，该基类又继承自 vnpy 的 `BaseApp`。每个应用通常包含以下组件：

- **__init__.py** - 定义应用类和基本信息
- **engine.py** - 实现应用的核心功能引擎
- **widget.py** (可选) - 实现应用的图形界面
- **api/** (可选) - 提供 RESTful API 接口
- **commands/** (可选) - 提供消息指令处理功能

## 应用详情

### st_datamanager - 数据管理应用

数据管理应用提供数据下载、导入、导出、查看和管理功能，扩展了 vnpy_datamanager，并添加了 API 接口和消息指令处理功能。

**主要功能**：

- 获取 K 线数据和 Tick 数据
- 下载历史数据
- 从 CSV 文件导入数据
- 导出数据到 CSV 文件
- 删除数据

**API 接口**：

- `GET /api/data/overview` - 获取数据概览
- `GET /api/data/bars` - 获取 K 线数据
- `POST /api/data/download` - 下载历史数据
- `POST /api/data/import/csv` - 导入 CSV 数据
- `POST /api/data/export` - 导出数据
- `DELETE /api/data/bar/{exchange}/{symbol}/{interval}` - 删除 K 线数据

**消息指令**：

- `/data query [类型] [代码] [交易所] [周期] [开始日期] [结束日期(可选)]` - 查询数据
- `/data download [代码] [交易所] [周期] [开始日期] [结束日期(可选)]` - 下载数据
- `/data import [文件路径] [代码] [交易所] [周期] [时间列名] [开盘列名] [最高列名] [最低列名] [收盘列名] [成交量列名] [持仓量列名] [时间格式]` - 从 CSV 导入数据
- `/data export [代码] [交易所] [周期] [开始日期] [结束日期] [文件路径]` - 导出数据到 CSV
- `/data delete [类型] [代码] [交易所] [周期(仅 bar 类型需要)]` - 删除数据
- `/data help` - 显示帮助信息

### st_message - 消息系统应用

消息系统应用提供消息处理功能，支持通过消息指令控制系统。它是 SimpleTrade 的核心组件之一，使用户能够通过微信、飞书等消息平台与系统交互。

**主要功能**：

- 处理消息指令
- 将消息分发到相应的处理器
- 发送消息到用户或群组

**核心方法**：

- `register_processor(prefix, processor)` - 注册命令处理器
- `process_message(message_text)` - 处理消息
- `send_message(message, target)` - 发送消息

### st_trader - 交易增强应用

交易增强应用提供交易功能的增强，包括订单管理、持仓管理等。它扩展了 vnpy 的交易功能，提供更好的用户体验和更多的功能。

**主要功能**：

- 处理订单事件
- 处理成交事件
- 发送订单
- 撤销订单

**核心方法**：

- `send_order(symbol, exchange, direction, offset, price, volume, gateway_name)` - 发送订单
- `cancel_order(order_id, gateway_name)` - 撤销订单

**设计说明**：

st_trader 并非重复造轮子，而是对 vnpy 原有功能的轻量级封装和扩展：

1. **最小化的实现**：
   - `STTraderEngine` 的实现非常简洁，只有几个基本方法
   - 主要方法 `send_order` 和 `cancel_order` 只是对 vnpy 主引擎相应方法的简单封装
   - 没有重新实现订单管理、持仓管理等核心功能

2. **直接使用 vnpy 的事件系统**：
   - 注册了 vnpy 的标准事件 "eOrder" 和 "eTrade"
   - 事件处理函数目前只是简单的打印，为将来的扩展预留空间

3. **依赖 vnpy 的核心功能**：
   - 使用 vnpy 的 `OrderRequest` 和 `CancelRequest` 对象
   - 调用 `main_engine.send_order` 和 `main_engine.cancel_order` 方法
   - 没有自己实现订单路由、风控等功能

4. **扩展而非替代**：
   - 这是一个"交易增强引擎"，目的是增强而非替代 vnpy 的交易功能
   - 与 SimpleTrade 的其他组件（如消息系统、API 接口）集成
## 应用集成

应用通过 `simpletrade.core.initialization` 模块进行集成和初始化。在系统启动时，会自动加载和初始化所有注册的应用。

```python
# 初始化核心组件
event_engine = EventEngine()
main_engine = STMainEngine(event_engine)

# 添加应用
main_engine.add_app(STMessageApp)
main_engine.add_app(STTraderApp)
main_engine.add_app(STDataManagerApp)
```

## 开发新应用

要开发新的 SimpleTrade 应用，需要遵循以下步骤：

1. 创建一个新的应用目录，如 `simpletrade/apps/st_newapp`
2. 创建 `__init__.py` 文件，定义应用类
3. 创建 `engine.py` 文件，实现应用的核心功能引擎
4. 如果需要图形界面，创建 `widget.py` 文件
5. 如果需要 API 接口，创建 `api` 目录和相应的路由文件
6. 如果需要消息指令处理，创建 `commands` 目录和相应的处理器文件
7. 在 `simpletrade.core.initialization` 模块中注册新应用

## 测试应用

可以使用以下方法测试应用：

1. **API 测试**：启动 API 服务，通过 HTTP 请求测试 API 接口
2. **消息指令测试**：使用 `test_message` 函数测试消息指令处理
3. **交互式测试**：使用 `run_interactive_test` 函数进行交互式测试

```python
# 测试 API
from simpletrade.core.server import app, configure_server
configure_server(main_engine, event_engine)
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)

# 测试消息指令
message_engine = main_engine.get_engine("st_message")
run_interactive_test(message_engine)
```

## API 目录关系说明

在 SimpleTrade 项目中，存在两个主要的 API 相关目录：

1. **simpletrade/api/** - 整个平台的通用 API 目录
2. **simpletrade/apps/st_datamanager/api/** - 数据管理应用特定的 API 目录

这两个目录有明确的区别和关系：

### simpletrade/apps/st_datamanager/api/

- 特定于数据管理应用的 API 路由
- 定义了数据管理相关的所有 API 端点，如获取数据概览、获取 K 线数据、下载数据等
- 直接与 st_datamanager 引擎交互，通过依赖注入获取引擎实例
- 前缀为 `/api/data`，专注于数据管理功能

### simpletrade/api/

- 整个 SimpleTrade 平台的通用 API 路由
- 包含各种功能模块的 API 端点，如分析、策略管理、微信小程序等
- 可能会调用 st_datamanager 的功能，但不直接实现数据管理功能
- 各模块有不同的前缀，如 `/api/analysis`、`/api/strategies` 等

### 集成关系

在 `simpletrade/core/server.py` 中，会导入并注册 st_datamanager 的 API 路由：

```python
from simpletrade.apps.st_datamanager.api import router as data_router
app.include_router(data_router)
```

这意味着 st_datamanager 的 API 路由被集成到了整个 SimpleTrade 的 API 服务中，同时，其他模块的 API 路由也会被导入和注册。

这种设计使得各个应用可以独立开发和维护自己的 API，同时又能够集成到统一的 API 服务中，提供一致的用户体验。
