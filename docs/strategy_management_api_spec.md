# SimpleTrade 策略管理系统 API 规范

## 概述

本文档描述了SimpleTrade策略管理系统的API接口规范，包括请求和响应格式、数据模型和错误处理。

## 基本信息

- **基础URL**: `http://localhost:8000/api`
- **内容类型**: `application/json`
- **认证**: 暂未实现，计划使用JWT认证

## 通用响应格式

所有API响应都遵循以下格式：

```json
{
  "success": true|false,
  "message": "响应消息",
  "data": null|object|array
}
```

- `success`: 表示请求是否成功
- `message`: 响应消息，成功或错误信息
- `data`: 响应数据，可以是null、对象或数组

## 错误处理

当请求失败时，API会返回以下格式的响应：

```json
{
  "success": false,
  "message": "错误消息",
  "data": null
}
```

常见的错误消息包括：

- `"未找到资源"`: 请求的资源不存在
- `"参数错误"`: 请求参数不正确
- `"服务器错误"`: 服务器内部错误

## API端点

### 策略管理

#### 获取策略列表

获取所有可用的策略。

- **URL**: `/strategies/`
- **方法**: `GET`
- **查询参数**:
  - `type` (可选): 策略类型
  - `category` (可选): 策略分类
- **响应**:

```json
{
  "success": true,
  "message": "获取策略成功，共 X 个",
  "data": [
    {
      "id": 1,
      "name": "策略名称",
      "description": "策略描述",
      "category": "策略分类",
      "type": "策略类型",
      "complexity": 1,
      "resource_requirement": 1,
      "parameters": {
        "param1": {
          "type": "number",
          "default": 10,
          "min": 1,
          "max": 100,
          "description": "参数1描述"
        },
        "param2": {
          "type": "string",
          "default": "value",
          "options": ["value1", "value2"],
          "description": "参数2描述"
        }
      }
    }
  ]
}
```

#### 获取策略详情

获取特定策略的详细信息。

- **URL**: `/strategies/{strategy_id}`
- **方法**: `GET`
- **路径参数**:
  - `strategy_id`: 策略ID
- **响应**:

```json
{
  "success": true,
  "message": "获取策略详情成功",
  "data": {
    "id": 1,
    "name": "策略名称",
    "description": "策略描述",
    "category": "策略分类",
    "type": "策略类型",
    "complexity": 1,
    "resource_requirement": 1,
    "parameters": {
      "param1": {
        "type": "number",
        "default": 10,
        "min": 1,
        "max": 100,
        "description": "参数1描述"
      },
      "param2": {
        "type": "string",
        "default": "value",
        "options": ["value1", "value2"],
        "description": "参数2描述"
      }
    },
    "code": "策略代码",
    "class_details": {
      "class_name": "策略类名",
      "category": "策略分类",
      "description": "策略描述",
      "parameters": ["param1", "param2"],
      "variables": ["var1", "var2"],
      "default_values": {
        "param1": 10,
        "param2": "value"
      },
      "param_types": {
        "param1": "number",
        "param2": "string"
      },
      "param_descriptions": {
        "param1": "参数1描述",
        "param2": "参数2描述"
      }
    }
  }
}
```

#### 获取用户策略列表

获取特定用户的策略列表。

- **URL**: `/strategies/user/{user_id}`
- **方法**: `GET`
- **路径参数**:
  - `user_id`: 用户ID
- **响应**:

```json
{
  "success": true,
  "message": "获取用户策略成功，共 X 个",
  "data": [
    {
      "id": 1,
      "name": "用户策略名称",
      "strategy_id": 1,
      "strategy_name": "策略名称",
      "category": "策略分类",
      "type": "策略类型",
      "complexity": 1,
      "resource_requirement": 1,
      "parameters": {
        "param1": 15,
        "param2": "value"
      }
    }
  ]
}
```

#### 创建策略

创建新的策略。

- **URL**: `/strategies/create`
- **方法**: `POST`
- **请求体**:

```json
{
  "name": "策略名称",
  "description": "策略描述",
  "type": "策略类型",
  "category": "策略分类",
  "parameters": {
    "param1": 15,
    "param2": "value"
  }
}
```

- **响应**:

```json
{
  "success": true,
  "message": "创建策略成功",
  "data": {
    "id": 1,
    "name": "策略名称",
    "type": "策略类型"
  }
}
```

#### 创建用户策略

创建新的用户策略。

- **URL**: `/strategies/user/create`
- **方法**: `POST`
- **请求体**:

```json
{
  "user_id": 1,
  "strategy_id": 1,
  "name": "用户策略名称",
  "parameters": {
    "param1": 15,
    "param2": "value"
  }
}
```

- **响应**:

```json
{
  "success": true,
  "message": "创建用户策略成功",
  "data": {
    "id": 1,
    "name": "用户策略名称",
    "strategy_id": 1
  }
}
```

#### 初始化策略

初始化用户策略。

- **URL**: `/strategies/user/{user_strategy_id}/init`
- **方法**: `POST`
- **路径参数**:
  - `user_strategy_id`: 用户策略ID
- **响应**:

```json
{
  "success": true,
  "message": "初始化策略成功"
}
```

#### 启动策略

启动用户策略。

- **URL**: `/strategies/user/{user_strategy_id}/start`
- **方法**: `POST`
- **路径参数**:
  - `user_strategy_id`: 用户策略ID
- **响应**:

```json
{
  "success": true,
  "message": "启动策略成功"
}
```

#### 停止策略

停止用户策略。

- **URL**: `/strategies/user/{user_strategy_id}/stop`
- **方法**: `POST`
- **路径参数**:
  - `user_strategy_id`: 用户策略ID
- **响应**:

```json
{
  "success": true,
  "message": "停止策略成功"
}
```

### 策略监控

#### 获取所有策略监控信息

获取所有正在监控的策略信息。

- **URL**: `/strategies/monitor`
- **方法**: `GET`
- **响应**:

```json
{
  "success": true,
  "message": "获取策略监控信息成功，共 X 个",
  "data": [
    {
      "strategy_name": "策略名称",
      "user_strategy_id": 1,
      "start_time": "2023-01-01 00:00:00",
      "last_update_time": "2023-01-01 00:01:00",
      "status": "running",
      "error_message": "",
      "performance": {
        "total_profit": 1000.0,
        "total_trades": 10,
        "win_trades": 7,
        "loss_trades": 3,
        "win_rate": 0.7,
        "max_drawdown": 200.0,
        "current_drawdown": 50.0
      },
      "positions": [
        {
          "symbol": "AAPL",
          "direction": "多",
          "volume": 100
        }
      ],
      "trades": [
        {
          "time": "2023-01-01 00:00:30",
          "symbol": "AAPL",
          "direction": "多",
          "offset": "开仓",
          "price": 150.0,
          "volume": 100
        }
      ],
      "logs": [
        {
          "time": "2023-01-01 00:00:00",
          "message": "策略启动"
        }
      ]
    }
  ]
}
```

#### 获取特定策略监控信息

获取特定策略的监控信息。

- **URL**: `/strategies/monitor/{user_strategy_id}`
- **方法**: `GET`
- **路径参数**:
  - `user_strategy_id`: 用户策略ID
- **响应**:

```json
{
  "success": true,
  "message": "获取策略监控信息成功",
  "data": {
    "strategy_name": "策略名称",
    "user_strategy_id": 1,
    "start_time": "2023-01-01 00:00:00",
    "last_update_time": "2023-01-01 00:01:00",
    "status": "running",
    "error_message": "",
    "performance": {
      "total_profit": 1000.0,
      "total_trades": 10,
      "win_trades": 7,
      "loss_trades": 3,
      "win_rate": 0.7,
      "max_drawdown": 200.0,
      "current_drawdown": 50.0
    },
    "positions": [
      {
        "symbol": "AAPL",
        "direction": "多",
        "volume": 100
      }
    ],
    "trades": [
      {
        "time": "2023-01-01 00:00:30",
        "symbol": "AAPL",
        "direction": "多",
        "offset": "开仓",
        "price": 150.0,
        "volume": 100
      }
    ],
    "logs": [
      {
        "time": "2023-01-01 00:00:00",
        "message": "策略启动"
      }
    ]
  }
}
```

### 回测管理

#### 运行回测

运行策略回测。

- **URL**: `/strategies/backtest`
- **方法**: `POST`
- **请求体**:

```json
{
  "strategy_id": 1,
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "interval": "1d",
  "start_date": "2020-01-01",
  "end_date": "2020-12-31",
  "initial_capital": 100000.0,
  "rate": 0.0003,
  "slippage": 0.2,
  "size": 1.0,
  "pricetick": 0.2,
  "user_id": 1
}
```

- **响应**:

```json
{
  "success": true,
  "message": "回测成功",
  "data": {
    "statistics": {
      "start_date": "2020-01-01",
      "end_date": "2020-12-31",
      "total_days": 365,
      "profit_days": 200,
      "loss_days": 165,
      "start_balance": 100000.0,
      "end_balance": 120000.0,
      "total_return": 0.2,
      "annual_return": 0.2,
      "max_drawdown": 0.1,
      "max_drawdown_duration": 30,
      "total_trades": 50,
      "win_trades": 30,
      "loss_trades": 20,
      "win_rate": 0.6,
      "sharpe_ratio": 1.5
    },
    "trades": [
      {
        "time": "2020-01-15 00:00:00",
        "symbol": "AAPL",
        "direction": "多",
        "offset": "开仓",
        "price": 150.0,
        "volume": 100,
        "profit": 0.0
      }
    ]
  }
}
```

#### 获取回测记录列表

获取回测记录列表。

- **URL**: `/strategies/backtest/records`
- **方法**: `GET`
- **查询参数**:
  - `user_id` (可选): 用户ID
  - `strategy_id` (可选): 策略ID
- **响应**:

```json
{
  "success": true,
  "message": "获取回测记录成功，共 X 个",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "strategy_id": 1,
      "symbol": "AAPL",
      "exchange": "NASDAQ",
      "interval": "1d",
      "start_date": "2020-01-01",
      "end_date": "2020-12-31",
      "initial_capital": 100000.0,
      "final_capital": 120000.0,
      "total_return": 0.2,
      "annual_return": 0.2,
      "max_drawdown": 0.1,
      "sharpe_ratio": 1.5,
      "created_at": "2023-01-01 00:00:00"
    }
  ]
}
```

#### 获取回测记录详情

获取特定回测记录的详细信息。

- **URL**: `/strategies/backtest/records/{record_id}`
- **方法**: `GET`
- **路径参数**:
  - `record_id`: 回测记录ID
- **响应**:

```json
{
  "success": true,
  "message": "获取回测记录详情成功",
  "data": {
    "id": 1,
    "user_id": 1,
    "strategy_id": 1,
    "symbol": "AAPL",
    "exchange": "NASDAQ",
    "interval": "1d",
    "start_date": "2020-01-01",
    "end_date": "2020-12-31",
    "initial_capital": 100000.0,
    "final_capital": 120000.0,
    "total_return": 0.2,
    "annual_return": 0.2,
    "max_drawdown": 0.1,
    "sharpe_ratio": 1.5,
    "created_at": "2023-01-01 00:00:00",
    "results": {
      "statistics": {
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
        "total_days": 365,
        "profit_days": 200,
        "loss_days": 165,
        "start_balance": 100000.0,
        "end_balance": 120000.0,
        "total_return": 0.2,
        "annual_return": 0.2,
        "max_drawdown": 0.1,
        "max_drawdown_duration": 30,
        "total_trades": 50,
        "win_trades": 30,
        "loss_trades": 20,
        "win_rate": 0.6,
        "sharpe_ratio": 1.5
      },
      "trades": [
        {
          "time": "2020-01-15 00:00:00",
          "symbol": "AAPL",
          "direction": "多",
          "offset": "开仓",
          "price": 150.0,
          "volume": 100,
          "profit": 0.0
        }
      ],
      "equity_curve": [
        {
          "datetime": "2020-01-01 00:00:00",
          "capital": 100000.0,
          "drawdown": 0.0,
          "drawdown_pct": 0.0
        }
      ]
    }
  }
}
```

## 数据模型

### Strategy

策略模型，存储策略的基本信息和参数。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | Integer | 策略ID |
| name | String | 策略名称 |
| description | Text | 策略描述 |
| category | String | 策略分类 |
| type | String | 策略类型 |
| complexity | Integer | 复杂度评分 (1-5) |
| resource_requirement | Integer | 资源需求评分 (1-5) |
| code | Text | 策略代码 |
| parameters | JSON | 策略参数 |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### UserStrategy

用户策略模型，存储用户的策略配置。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | Integer | 用户策略ID |
| user_id | Integer | 用户ID |
| strategy_id | Integer | 策略ID |
| name | String | 用户策略名称 |
| parameters | JSON | 用户策略参数 |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### BacktestRecord

回测记录模型，存储回测结果。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| id | Integer | 回测记录ID |
| user_id | Integer | 用户ID |
| strategy_id | Integer | 策略ID |
| symbol | String | 交易品种 |
| exchange | String | 交易所 |
| interval | String | K线周期 |
| start_date | Date | 开始日期 |
| end_date | Date | 结束日期 |
| initial_capital | Numeric | 初始资金 |
| final_capital | Numeric | 最终资金 |
| total_return | Numeric | 总收益率 |
| annual_return | Numeric | 年化收益率 |
| max_drawdown | Numeric | 最大回撤 |
| sharpe_ratio | Numeric | 夏普比率 |
| results | JSON | 回测结果 |
| created_at | DateTime | 创建时间 |

## 错误码

| 错误码 | 描述 |
| --- | --- |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 版本历史

| 版本 | 日期 | 描述 |
| --- | --- | --- |
| 1.0.0 | 2023-01-01 | 初始版本 |
