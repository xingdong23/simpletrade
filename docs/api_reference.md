# SimpleTrade API参考

本文档描述了SimpleTrade提供的API接口。

## 数据管理API

### 获取数据概览

```
GET /api/data/overview
```

返回所有可用的数据概览，包括K线数据和Tick数据。

### 获取K线数据

```
GET /api/data/bars?symbol={symbol}&exchange={exchange}&interval={interval}&start_date={start_date}&end_date={end_date}
```

参数：
- `symbol`: 代码，如 "AAPL"
- `exchange`: 交易所，如 "NASDAQ"
- `interval`: 周期，如 "1d"
- `start_date`: 开始日期，格式为 "YYYY-MM-DD"
- `end_date`: 结束日期，格式为 "YYYY-MM-DD"（可选）

### 获取Tick数据

```
GET /api/data/ticks?symbol={symbol}&exchange={exchange}&start_date={start_date}&end_date={end_date}
```

参数：
- `symbol`: 代码，如 "AAPL"
- `exchange`: 交易所，如 "NASDAQ"
- `start_date`: 开始日期，格式为 "YYYY-MM-DD"
- `end_date`: 结束日期，格式为 "YYYY-MM-DD"（可选）

### 导入数据

```
POST /api/data/import
```

请求体：
```json
{
  "file_path": "/path/to/data.csv",
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "interval": "1d",
  "datetime_format": "%Y-%m-%d",
  "datetime_column": "datetime",
  "open_column": "open",
  "high_column": "high",
  "low_column": "low",
  "close_column": "close",
  "volume_column": "volume",
  "open_interest_column": "open_interest"
}
```

### 导出数据

```
POST /api/data/export
```

请求体：
```json
{
  "file_path": "/path/to/export.csv",
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "interval": "1d",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```

### 删除数据

```
DELETE /api/data/bars?symbol={symbol}&exchange={exchange}&interval={interval}
```

参数：
- `symbol`: 代码，如 "AAPL"
- `exchange`: 交易所，如 "NASDAQ"
- `interval`: 周期，如 "1d"

## 数据分析API

### 计算技术指标

```
POST /api/analysis/indicators
```

请求体：
```json
{
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "interval": "1d",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "indicators": [
    {
      "name": "SMA",
      "params": {
        "period": 20
      }
    },
    {
      "name": "RSI",
      "params": {
        "period": 14
      }
    }
  ]
}
```

### 运行策略回测

```
POST /api/analysis/backtest
```

请求体：
```json
{
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "interval": "1d",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "strategy_name": "MovingAverageCrossover",
  "strategy_params": {
    "fast_period": 5,
    "slow_period": 20
  },
  "initial_capital": 100000.0
}
```

## 微信小程序API

### 用户登录

```
POST /api/wechat/auth/login
```

请求体：
```json
{
  "code": "wx_login_code"
}
```

### 获取数据概览

```
GET /api/wechat/data/overview
```

需要认证头：
```
Authorization: Bearer {access_token}
```
