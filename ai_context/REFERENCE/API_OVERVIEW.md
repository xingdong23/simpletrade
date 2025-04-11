# SimpleTrade API概览

**最后更新**: 2023-10-15

## 1. API架构

SimpleTrade采用RESTful API架构，提供标准化的接口用于交易操作、数据查询和系统管理。同时，提供WebSocket接口用于实时数据推送。

### 1.1 基本架构

```
客户端 <---> API网关 <---> 服务层 <---> 核心引擎
```

- **客户端**: 微信小程序、Web界面、消息系统
- **API网关**: 处理认证、路由和请求限流
- **服务层**: 实现业务逻辑和数据处理
- **核心引擎**: 基于vnpy的交易和策略引擎

### 1.2 技术栈

- **Web框架**: FastAPI
- **认证**: JWT (JSON Web Token)
- **实时通信**: WebSocket
- **文档**: Swagger/OpenAPI
- **序列化**: JSON

## 2. API端点概览

### 2.1 认证与用户管理

| 端点 | 方法 | 描述 | 权限 |
|-----|------|------|------|
| `/api/auth/login` | POST | 用户登录 | 公开 |
| `/api/auth/logout` | POST | 用户登出 | 用户 |
| `/api/auth/refresh` | POST | 刷新令牌 | 用户 |
| `/api/users/me` | GET | 获取当前用户信息 | 用户 |
| `/api/users/me` | PUT | 更新用户信息 | 用户 |

### 2.2 交易接口管理

| 端点 | 方法 | 描述 | 权限 |
|-----|------|------|------|
| `/api/gateways` | GET | 获取所有交易接口 | 用户 |
| `/api/gateways/{id}` | GET | 获取特定交易接口信息 | 用户 |
| `/api/gateways` | POST | 添加交易接口 | 用户 |
| `/api/gateways/{id}` | PUT | 更新交易接口 | 用户 |
| `/api/gateways/{id}` | DELETE | 删除交易接口 | 用户 |
| `/api/gateways/{id}/connect` | POST | 连接交易接口 | 用户 |
| `/api/gateways/{id}/disconnect` | POST | 断开交易接口 | 用户 |

### 2.3 订单管理

| 端点 | 方法 | 描述 | 权限 |
|-----|------|------|------|
| `/api/orders` | GET | 获取订单列表 | 用户 |
| `/api/orders/{id}` | GET | 获取特定订单 | 用户 |
| `/api/orders` | POST | 创建新订单 | 用户 |
| `/api/orders/{id}` | DELETE | 撤销订单 | 用户 |
| `/api/orders/batch-cancel` | POST | 批量撤销订单 | 用户 |
| `/api/trades` | GET | 获取成交记录 | 用户 |

### 2.4 持仓管理

| 端点 | 方法 | 描述 | 权限 |
|-----|------|------|------|
| `/api/positions` | GET | 获取持仓列表 | 用户 |
| `/api/positions/{symbol}` | GET | 获取特定品种持仓 | 用户 |
| `/api/positions/close` | POST | 平仓操作 | 用户 |
| `/api/positions/close-all` | POST | 全部平仓 | 用户 |

### 2.5 策略管理

| 端点 | 方法 | 描述 | 权限 |
|-----|------|------|------|
| `/api/strategies` | GET | 获取策略列表 | 用户 |
| `/api/strategies/{id}` | GET | 获取特定策略 | 用户 |
| `/api/strategies` | POST | 创建新策略 | 用户 |
| `/api/strategies/{id}` | PUT | 更新策略 | 用户 |
| `/api/strategies/{id}` | DELETE | 删除策略 | 用户 |
| `/api/strategies/{id}/start` | POST | 启动策略 | 用户 |
| `/api/strategies/{id}/stop` | POST | 停止策略 | 用户 |
| `/api/strategies/{id}/performance` | GET | 获取策略绩效 | 用户 |
| `/api/strategies/templates` | GET | 获取策略模板列表 | 用户 |

### 2.6 数据管理

| 端点 | 方法 | 描述 | 权限 |
|-----|------|------|------|
| `/api/market/bars` | GET | 获取K线数据 | 用户 |
| `/api/market/ticks` | GET | 获取Tick数据 | 用户 |
| `/api/market/instruments` | GET | 获取合约信息 | 用户 |
| `/api/market/subscribe` | POST | 订阅行情数据 | 用户 |
| `/api/market/unsubscribe` | POST | 取消订阅行情数据 | 用户 |

### 2.7 AI分析

| 端点 | 方法 | 描述 | 权限 |
|-----|------|------|------|
| `/api/ai/analyze` | POST | 请求AI分析 | 用户 |
| `/api/ai/analysis/{id}` | GET | 获取分析结果 | 用户 |
| `/api/ai/predict` | POST | 请求预测 | 用户 |
| `/api/ai/models` | GET | 获取可用模型 | 用户 |
| `/api/ai/train` | POST | 训练自定义模型 | 高级用户 |

### 2.8 系统管理

| 端点 | 方法 | 描述 | 权限 |
|-----|------|------|------|
| `/api/system/status` | GET | 获取系统状态 | 用户 |
| `/api/system/logs` | GET | 获取系统日志 | 管理员 |
| `/api/system/settings` | GET | 获取系统设置 | 用户 |
| `/api/system/settings` | PUT | 更新系统设置 | 管理员 |

## 3. 请求/响应格式

### 3.1 通用响应格式

所有API响应都遵循以下格式：

```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功",
  "code": 200,
  "timestamp": "2023-10-15T08:30:00Z"
}
```

或者在出错时：

```json
{
  "success": false,
  "data": null,
  "message": "错误详情",
  "code": 400,
  "timestamp": "2023-10-15T08:30:00Z"
}
```

### 3.2 分页响应格式

对于返回列表的端点，支持分页：

```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "message": "操作成功",
  "code": 200,
  "timestamp": "2023-10-15T08:30:00Z"
}
```

### 3.3 请求示例

#### 创建订单

```
POST /api/orders

{
  "symbol": "AAPL",
  "direction": "LONG",
  "offset": "OPEN",
  "type": "LIMIT",
  "price": 150.5,
  "volume": 100,
  "gateway_name": "IB"
}
```

#### 获取K线数据

```
GET /api/market/bars?symbol=AAPL&interval=1d&start=2023-01-01&end=2023-10-01
```

## 4. WebSocket API

### 4.1 连接

WebSocket连接URL：`wss://api.simpletrade.com/ws`

连接时需要提供认证令牌：`wss://api.simpletrade.com/ws?token=<JWT_TOKEN>`

### 4.2 消息格式

#### 客户端消息

```json
{
  "action": "subscribe",
  "channel": "tick",
  "data": {
    "symbols": ["AAPL", "MSFT"]
  }
}
```

#### 服务器消息

```json
{
  "channel": "tick",
  "data": {
    "symbol": "AAPL",
    "last_price": 150.5,
    "volume": 1000,
    "open_interest": 0,
    "last_volume": 10,
    "limit_up": 165.0,
    "limit_down": 135.0,
    "open_price": 149.0,
    "high_price": 151.2,
    "low_price": 148.5,
    "pre_close": 149.0,
    "bid_price_1": 150.4,
    "bid_volume_1": 200,
    "ask_price_1": 150.6,
    "ask_volume_1": 300,
    "gateway_name": "IB",
    "datetime": "2023-10-15T08:30:00Z"
  },
  "timestamp": "2023-10-15T08:30:00Z"
}
```

### 4.3 频道类型

| 频道 | 描述 | 数据内容 |
|-----|------|---------|
| `tick` | Tick数据更新 | 最新市场行情数据 |
| `bar` | K线数据更新 | 最新K线数据 |
| `order` | 订单状态更新 | 订单状态变化 |
| `trade` | 成交更新 | 新成交信息 |
| `position` | 持仓更新 | 持仓变化 |
| `account` | 账户更新 | 账户资金变化 |
| `log` | 日志更新 | 系统日志 |
| `strategy` | 策略状态更新 | 策略运行状态变化 |

### 4.4 操作类型

| 操作 | 描述 | 参数 |
|-----|------|------|
| `subscribe` | 订阅频道 | channel, symbols |
| `unsubscribe` | 取消订阅 | channel, symbols |
| `ping` | 心跳检测 | 无 |
| `authenticate` | 认证(可选) | token |

## 5. 认证与安全

### 5.1 JWT认证

SimpleTrade API使用JWT (JSON Web Token) 进行认证：

1. 客户端通过`/api/auth/login`获取JWT令牌
2. 客户端在后续请求的Header中包含令牌：`Authorization: Bearer <token>`
3. 令牌有效期为2小时，可通过`/api/auth/refresh`刷新

### 5.2 权限级别

| 级别 | 描述 | 权限范围 |
|-----|------|---------|
| 公开 | 无需认证 | 登录、注册、公开数据访问 |
| 用户 | 普通用户权限 | 交易操作、数据查询、策略管理 |
| 高级用户 | 扩展权限 | 高级功能、模型训练 |
| 管理员 | 管理权限 | 系统管理、用户管理 |

### 5.3 安全措施

1. **HTTPS**: 所有API通信使用HTTPS加密
2. **请求限流**: 防止API滥用
3. **IP白名单**: 可配置IP访问限制
4. **敏感操作确认**: 重要操作需要二次确认
5. **日志审计**: 记录所有API访问和操作

## 6. 错误处理

### 6.1 错误码

| 错误码 | 描述 | 处理建议 |
|-------|------|---------|
| 400 | 请求参数错误 | 检查请求参数 |
| 401 | 未认证 | 重新登录获取令牌 |
| 403 | 权限不足 | 检查用户权限 |
| 404 | 资源不存在 | 检查请求的资源ID |
| 409 | 资源冲突 | 检查资源状态 |
| 429 | 请求过于频繁 | 降低请求频率 |
| 500 | 服务器内部错误 | 联系系统管理员 |

### 6.2 错误响应示例

```json
{
  "success": false,
  "data": null,
  "message": "订单参数无效：价格必须大于0",
  "code": 400,
  "timestamp": "2023-10-15T08:30:00Z",
  "details": {
    "field": "price",
    "reason": "must_be_positive"
  }
}
```

## 7. API客户端

### 7.1 Python客户端

SimpleTrade提供官方Python客户端库：

```python
from simpletrade.client import SimpleTradeClient

# 初始化客户端
client = SimpleTradeClient(api_url="https://api.simpletrade.com")

# 登录
client.login(username="user", password="password")

# 获取账户信息
account = client.get_account()

# 下单
order = client.create_order(
    symbol="AAPL",
    direction="LONG",
    offset="OPEN",
    type="LIMIT",
    price=150.5,
    volume=100
)

# 订阅WebSocket数据
client.subscribe_ticks(["AAPL", "MSFT"], callback=on_tick)
```

### 7.2 微信小程序集成

微信小程序可以通过以下方式集成API：

```javascript
// 登录
wx.request({
  url: 'https://api.simpletrade.com/api/auth/login',
  method: 'POST',
  data: {
    username: 'user',
    password: 'password'
  },
  success(res) {
    const token = res.data.data.token;
    wx.setStorageSync('token', token);
  }
});

// 获取账户信息
wx.request({
  url: 'https://api.simpletrade.com/api/users/me',
  method: 'GET',
  header: {
    'Authorization': `Bearer ${wx.getStorageSync('token')}`
  },
  success(res) {
    const userInfo = res.data.data;
    // 处理用户信息
  }
});

// WebSocket连接
const ws = wx.connectSocket({
  url: `wss://api.simpletrade.com/ws?token=${wx.getStorageSync('token')}`,
  success() {
    console.log('WebSocket连接成功');
  }
});

ws.onMessage(function(res) {
  const data = JSON.parse(res.data);
  // 处理WebSocket消息
});
```

## 8. API版本控制

SimpleTrade API采用版本控制策略，确保向后兼容性：

1. **URL版本控制**: `/api/v1/...`, `/api/v2/...`
2. **默认使用最新版本**: 不指定版本时使用最新版本
3. **版本淘汰策略**: 旧版本API会有至少6个月的淘汰期
4. **版本兼容性文档**: 提供版本间变更的详细文档

## 9. API使用最佳实践

1. **使用官方客户端库**: 减少集成错误，自动处理认证和重试
2. **实现指数退避重试**: 遇到临时错误时使用指数退避策略重试
3. **缓存不常变化的数据**: 减少API调用，提高应用性能
4. **使用WebSocket获取实时更新**: 避免频繁轮询API
5. **处理所有错误情况**: 确保应用在API错误时能够优雅降级
6. **遵循请求限流规则**: 避免触发限流机制
7. **定期刷新令牌**: 在令牌过期前刷新，避免认证失败

通过遵循这些最佳实践，开发者可以构建稳定、高效的应用，充分利用SimpleTrade API的功能。
