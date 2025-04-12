# 老虎证券Gateway集成指南

本文档详细介绍如何在SimpleTrade中集成和使用老虎证券Gateway，包括安装、配置、数据下载和实时数据订阅等功能。

## 1. 概述

老虎证券Gateway是SimpleTrade为对接老虎证券行情和交易服务而开发的交易接口。它基于老虎证券开放平台API，提供了历史数据下载、实时行情订阅和交易功能。

### 1.1 主要功能

- **历史数据下载**: 支持下载美股、港股等市场的历史K线数据
- **实时行情订阅**: 支持订阅实时行情数据
- **交易功能**: 支持下单、撤单等交易操作
- **账户管理**: 支持查询账户资金、持仓等信息

### 1.2 支持的市场

- 美国股票市场 (NYSE, NASDAQ, AMEX)
- 香港股票市场 (SEHK)
- 新加坡股票市场 (SGX)
- 澳大利亚股票市场 (ASX)

## 2. 安装与配置

### 2.1 获取并放置 vnpy_tiger 源码

`vnpy_tiger` 是 SimpleTrade 的自定义组件，并非通过 `pip` 安装。

1.  确保 `vnpy_tiger` 的源代码位于项目根目录下的 `vendors/vnpy_tiger` 目录中。
2.  `simpletrade/main.py` 文件会自动将 `vendors` 目录添加到 Python 搜索路径 (`sys.path`) 以便导入。

### 2.2 安装 vnpy_tiger 依赖

确保您已在激活的 Python 环境中安装了 `vnpy_tiger` 所需的依赖，主要是 `tigeropen`：

```bash
# 激活环境 (e.g., conda activate simpletrade)
pip install tigeropen
# 如果 vnpy_tiger 有 requirements.txt, 也安装它:
# pip install -r vendors/vnpy_tiger/requirements.txt
```

### 2.3 申请老虎证券开放平台账号

1. 访问[老虎开放平台](https://www.itigerup.com/openapi)
2. 注册并申请开发者账号
3. 创建应用并获取Tiger ID
4. 生成并下载私钥文件

### 2.4 配置老虎证券Gateway

在使用老虎证券Gateway之前，需要配置以下信息：

```python
TIGER_SETTING = {
    "tiger_id": "YOUR_TIGER_ID",  # 老虎证券开放平台ID
    "account": "YOUR_ACCOUNT",    # 老虎证券账户
    "private_key": "PATH_TO_PRIVATE_KEY",  # 私钥文件路径
    "server": "模拟",  # 可选: "标准", "环球", "模拟"
    "language": "中文"  # 可选: "中文", "英文"
}
```

## 3. 在SimpleTrade中使用老虎证券Gateway

### 3.1 注册老虎证券Gateway

`simpletrade/main.py` 文件中包含加载和注册 `vnpy_tiger` 的逻辑。由于 `vendors` 目录已加入 `sys.path`，`from vnpy_tiger import TigerGateway` 应该能正常工作。

```python
# (位于 main.py)
try:
    logger.info("Attempting to import vnpy_tiger...")
    from vnpy_tiger import TigerGateway # Should find it in vendors/
    logger.info("vnpy_tiger imported successfully.")
except ImportError as e:
    logger.error(f"Warning: vnpy_tiger not found. Error: {e}")
    logger.warning("Please install it first.") # Should say: Please check vendors/vnpy_tiger and dependencies.
    TigerGateway = None

# 在全局 App 和 Gateway 注册部分
if TigerGateway:
    main_engine.add_gateway(TigerGateway)
    logger.info("Global: Tiger Gateway registered.")
# ...
```

### 3.2 连接老虎证券Gateway

```python
# 连接老虎证券Gateway
setting = {
    "tiger_id": "YOUR_TIGER_ID",
    "account": "YOUR_ACCOUNT",
    "private_key": "PATH_TO_PRIVATE_KEY",
    "server": "模拟",
    "language": "中文"
}
main_engine.connect(setting, "TIGER")
```

### 3.3 订阅行情

```python
from vnpy.trader.object import SubscribeRequest
from vnpy.trader.constant import Exchange

# 创建订阅请求
req = SubscribeRequest(
    symbol="AAPL",  # 苹果股票
    exchange=Exchange.NASDAQ
)

# 订阅行情
main_engine.subscribe(req, "TIGER")
```

### 3.4 查询历史数据

```python
from datetime import datetime, timedelta
from vnpy.trader.object import HistoryRequest
from vnpy.trader.constant import Exchange, Interval

# 创建历史数据请求
req = HistoryRequest(
    symbol="AAPL",  # 苹果股票
    exchange=Exchange.NASDAQ,
    interval=Interval.DAILY,  # 日线数据
    start=datetime.now() - timedelta(days=10),  # 10天前
    end=datetime.now()  # 当前时间
)

# 查询历史数据
bars = main_engine.query_history(req, "TIGER")

# 打印历史数据
for bar in bars:
    print(f"日期: {bar.datetime}, 开盘: {bar.open_price}, 收盘: {bar.close_price}")
```

### 3.5 委托下单

```python
from vnpy.trader.object import OrderRequest
from vnpy.trader.constant import Direction, Offset, OrderType, Exchange

# 创建委托请求
req = OrderRequest(
    symbol="AAPL",  # 苹果股票
    exchange=Exchange.NASDAQ,
    direction=Direction.LONG,  # 买入
    offset=Offset.OPEN,  # 开仓
    type=OrderType.LIMIT,  # 限价单
    price=150.0,  # 价格
    volume=100  # 数量
)

# 发送委托
orderid = main_engine.send_order(req, "TIGER")
print(f"委托已发送，委托号: {orderid}")
```

## 4. 使用脚本工具

SimpleTrade提供了几个脚本工具，用于测试老虎证券Gateway的功能：

### 4.1 测试老虎证券Gateway

使用`scripts/test_tiger_gateway.py`脚本测试老虎证券Gateway的基本功能：

```bash
# 编辑脚本，填写老虎证券账户配置
vim scripts/test_tiger_gateway.py

# 运行脚本测试Gateway功能
python scripts/test_tiger_gateway.py
```

### 4.2 下载历史数据

使用`scripts/download_tiger_data.py`脚本下载历史数据：

```bash
# 编辑脚本，填写老虎证券账户配置
vim scripts/download_tiger_data.py

# 运行脚本下载历史数据
python scripts/download_tiger_data.py
```

### 4.3 订阅实时行情

使用`scripts/subscribe_tiger_data.py`脚本订阅实时行情：

```bash
# 编辑脚本，填写老虎证券账户配置
vim scripts/subscribe_tiger_data.py

# 运行脚本订阅实时行情
python scripts/subscribe_tiger_data.py
```

## 5. 数据流转

在SimpleTrade中，数据流转的过程如下：

### 5.1 历史数据下载

1. 通过老虎证券Gateway的query_history方法获取历史数据
2. 将历史数据保存到数据库中
3. 通过DataManager类提供的方法查询数据库中的历史数据

### 5.2 实时数据订阅

1. 通过老虎证券Gateway的subscribe方法订阅实时行情
2. Gateway接收到行情数据后，通过on_tick方法推送到事件引擎
3. 事件引擎将行情数据分发给注册的回调函数
4. 回调函数将行情数据保存到数据库中

### 5.3 API接口

1. API接口通过DataManager类查询数据库中的历史数据
2. API接口通过事件引擎接收实时行情数据

## 6. 常见问题

### 6.1 连接失败

如果连接老虎证券Gateway失败，请检查：

1. Tiger ID、账户和私钥是否正确
2. 网络连接是否正常
3. 老虎证券服务器是否可用

### 6.2 获取不到行情数据

如果获取不到行情数据，请检查：

1. 是否有对应的行情权限
2. 市场是否开盘
3. 股票代码是否正确

### 6.3 委托失败

如果委托失败，请检查：

1. 账户是否有足够的资金
2. 委托价格是否合理
3. 市场是否开盘

## 7. 参考资料

- [老虎开放平台官网](https://www.itigerup.com/openapi)
- [老虎开放平台API文档](https://quant.itigerup.com/openapi/)
- [老虎证券Gateway使用指南](./tiger_gateway_usage.md)
