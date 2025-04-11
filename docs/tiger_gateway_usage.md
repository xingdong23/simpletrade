# 老虎证券Gateway使用指南

本文档介绍如何在SimpleTrade中使用老虎证券Gateway获取行情数据和进行交易。

## 1. 准备工作

### 1.1 申请老虎证券开放平台账号

1. 访问[老虎开放平台](https://www.itigerup.com/openapi)
2. 注册并申请开发者账号
3. 创建应用并获取Tiger ID
4. 生成并下载私钥文件

### 1.2 安装老虎证券Gateway

```bash
# 安装老虎证券Gateway
cd vnpy_tiger
pip install -e .
```

## 2. 配置老虎证券Gateway

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

## 3. 下载历史数据

使用`scripts/download_tiger_data.py`脚本下载历史数据：

```bash
# 编辑脚本，填写老虎证券账户配置
vim scripts/download_tiger_data.py

# 运行脚本下载历史数据
python scripts/download_tiger_data.py
```

该脚本会下载指定股票的分钟、小时和日线数据，并保存到数据库中。

## 4. 订阅实时行情

使用`scripts/subscribe_tiger_data.py`脚本订阅实时行情：

```bash
# 编辑脚本，填写老虎证券账户配置
vim scripts/subscribe_tiger_data.py

# 运行脚本订阅实时行情
python scripts/subscribe_tiger_data.py
```

该脚本会订阅指定股票的实时行情，并将Tick数据保存到数据库中。

## 5. 在SimpleTrade中使用老虎证券Gateway

SimpleTrade已经集成了老虎证券Gateway，可以直接在SimpleTrade中使用：

```bash
# 启动SimpleTrade
python simpletrade/main.py
```

启动后，SimpleTrade会自动加载老虎证券Gateway，可以通过API接口访问老虎证券的行情和交易功能。

## 6. API接口使用示例

### 6.1 获取历史数据

```python
from datetime import datetime, timedelta
from vnpy.trader.object import HistoryRequest
from vnpy.trader.constant import Exchange, Interval

# 创建历史数据请求
req = HistoryRequest(
    symbol="AAPL",
    exchange=Exchange.NASDAQ,
    interval=Interval.DAILY,
    start=datetime.now() - timedelta(days=10),
    end=datetime.now()
)

# 查询历史数据
bars = main_engine.query_history(req, "TIGER")
```

### 6.2 订阅实时行情

```python
from vnpy.trader.object import SubscribeRequest
from vnpy.trader.constant import Exchange

# 创建订阅请求
req = SubscribeRequest(
    symbol="AAPL",
    exchange=Exchange.NASDAQ
)

# 订阅行情
main_engine.subscribe(req, "TIGER")
```

### 6.3 委托下单

```python
from vnpy.trader.object import OrderRequest
from vnpy.trader.constant import Direction, Offset, OrderType, Exchange

# 创建委托请求
req = OrderRequest(
    symbol="AAPL",
    exchange=Exchange.NASDAQ,
    direction=Direction.LONG,
    offset=Offset.OPEN,
    type=OrderType.LIMIT,
    price=150.0,
    volume=100
)

# 发送委托
main_engine.send_order(req, "TIGER")
```

## 7. 常见问题

### 7.1 连接失败

如果连接老虎证券Gateway失败，请检查：

1. Tiger ID、账户和私钥是否正确
2. 网络连接是否正常
3. 老虎证券服务器是否可用

### 7.2 获取不到行情数据

如果获取不到行情数据，请检查：

1. 是否有对应的行情权限
2. 市场是否开盘
3. 股票代码是否正确

### 7.3 委托失败

如果委托失败，请检查：

1. 账户是否有足够的资金
2. 委托价格是否合理
3. 市场是否开盘
