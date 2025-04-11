# SimpleTrade 技术规格文档

**版本**: 0.1  
**日期**: 2023-10-15  
**状态**: 初稿  

## 1. 文档目的

本文档详细描述 SimpleTrade 交易平台的技术规格，包括系统架构、API设计、数据模型、组件接口等技术细节，为开发团队和AI辅助开发提供明确的技术实现指导。

## 2. 系统架构

### 2.1 整体架构

SimpleTrade采用基于vnpy插件架构的设计，直接使用vnpy源码并通过自定义插件扩展功能。系统采用前后端分离架构，后端基于Python，前端采用微信小程序/H5。

```
simpletrade/
├── vnpy/                      # vnpy源码（直接复制）
├── simpletrade_apps/          # SimpleTrade自定义应用/插件
├── simpletrade_core/          # SimpleTrade核心扩展
├── frontend/                  # 前端代码
├── config/                    # 配置文件
├── scripts/                   # 脚本工具
├── tests/                     # 测试代码
├── docs/                      # 文档
├── requirements.txt           # 项目依赖
└── main.py                    # 主程序入口
```

### 2.2 后端架构

后端采用模块化设计，基于vnpy的事件驱动架构，通过自定义插件扩展功能。

#### 2.2.1 核心组件

1. **STMainEngine**: 扩展vnpy的MainEngine，提供核心功能管理
2. **EventEngine**: 事件驱动引擎，处理系统内部事件通信
3. **Gateway**: 交易接口网关，连接不同的交易平台
4. **Database**: 数据存储组件，管理系统数据

#### 2.2.2 自定义插件

1. **st_trader**: 交易增强插件，扩展订单管理功能
2. **st_data**: 数据管理插件，提供数据获取和处理功能
3. **st_risk**: 风险管理插件，提供风控规则和监控
4. **st_ml**: 机器学习插件，提供AI分析和预测功能
5. **st_wechat**: 微信接口插件，提供微信小程序API
6. **st_web**: Web接口插件，提供Web API和WebSocket服务

### 2.3 前端架构

前端采用微信小程序作为主要界面，同时提供H5版本作为备选。

#### 2.3.1 微信小程序

1. **页面结构**:
   - 首页: 账户概览、快捷操作
   - 交易页: 下单、持仓管理
   - 策略页: 策略列表、参数配置
   - 分析页: K线图表、AI分析结果
   - 我的: 个人设置、账户管理

2. **技术栈**:
   - WXML/WXSS/JS: 微信小程序原生开发
   - WeUI: UI组件库
   - ECharts Mini: 图表库

#### 2.3.2 H5版本

1. **页面结构**: 与微信小程序保持一致
2. **技术栈**:
   - Vue.js: 前端框架
   - Vant: UI组件库
   - ECharts: 图表库

### 2.4 通信架构

#### 2.4.1 API通信

1. **RESTful API**: 处理非实时请求
2. **WebSocket**: 处理实时数据推送
3. **消息队列**: 处理异步任务

#### 2.4.2 数据流

1. **市场数据流**: 行情数据从交易所→网关→引擎→前端
2. **交易数据流**: 交易指令从前端→API→引擎→网关→交易所
3. **事件流**: 系统内部通过事件引擎进行通信

## 3. API规范

### 3.1 RESTful API

#### 3.1.1 基本规范

- **基础URL**: `https://api.simpletrade.com/v1`
- **认证方式**: JWT (JSON Web Token)
- **数据格式**: JSON
- **HTTP方法**:
  - GET: 获取资源
  - POST: 创建资源
  - PUT: 更新资源
  - DELETE: 删除资源
- **状态码**:
  - 200: 成功
  - 201: 创建成功
  - 400: 请求错误
  - 401: 未授权
  - 403: 禁止访问
  - 404: 资源不存在
  - 500: 服务器错误

#### 3.1.2 API端点

##### 用户管理

```
GET    /users/me              # 获取当前用户信息
PUT    /users/me              # 更新用户信息
POST   /auth/login            # 用户登录
POST   /auth/logout           # 用户登出
POST   /auth/refresh          # 刷新令牌
```

##### 交易接口管理

```
GET    /gateways              # 获取所有交易接口
GET    /gateways/{id}         # 获取特定交易接口信息
POST   /gateways              # 添加交易接口
PUT    /gateways/{id}         # 更新交易接口
DELETE /gateways/{id}         # 删除交易接口
POST   /gateways/{id}/connect # 连接交易接口
POST   /gateways/{id}/disconnect # 断开交易接口
```

##### 订单管理

```
GET    /orders                # 获取订单列表
GET    /orders/{id}           # 获取特定订单
POST   /orders                # 创建新订单
DELETE /orders/{id}           # 撤销订单
GET    /trades                # 获取成交记录
```

##### 持仓管理

```
GET    /positions             # 获取持仓列表
GET    /positions/{symbol}    # 获取特定品种持仓
POST   /positions/close       # 平仓操作
```

##### 策略管理

```
GET    /strategies            # 获取策略列表
GET    /strategies/{id}       # 获取特定策略
POST   /strategies            # 创建新策略
PUT    /strategies/{id}       # 更新策略
DELETE /strategies/{id}       # 删除策略
POST   /strategies/{id}/start # 启动策略
POST   /strategies/{id}/stop  # 停止策略
GET    /strategies/{id}/performance # 获取策略绩效
```

##### 数据管理

```
GET    /market/bars           # 获取K线数据
GET    /market/ticks          # 获取Tick数据
GET    /market/instruments    # 获取合约信息
```

##### AI分析

```
POST   /ai/analyze            # 请求AI分析
GET    /ai/analysis/{id}      # 获取分析结果
POST   /ai/predict            # 请求预测
GET    /ai/models             # 获取可用模型
```

#### 3.1.3 请求/响应示例

##### 创建订单请求

```json
POST /orders

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

##### 创建订单响应

```json
{
  "id": "ord123456",
  "symbol": "AAPL",
  "direction": "LONG",
  "offset": "OPEN",
  "type": "LIMIT",
  "price": 150.5,
  "volume": 100,
  "traded": 0,
  "status": "SUBMITTING",
  "gateway_name": "IB",
  "created_at": "2023-10-15T08:30:00Z"
}
```

### 3.2 WebSocket API

#### 3.2.1 基本规范

- **WebSocket URL**: `wss://api.simpletrade.com/ws`
- **认证方式**: 通过URL参数传递token
- **数据格式**: JSON
- **心跳机制**: 每30秒发送一次心跳包

#### 3.2.2 消息类型

##### 订阅/取消订阅

```json
// 订阅
{
  "action": "subscribe",
  "channel": "tick",
  "symbols": ["AAPL", "MSFT"]
}

// 取消订阅
{
  "action": "unsubscribe",
  "channel": "tick",
  "symbols": ["AAPL"]
}
```

##### 市场数据推送

```json
// Tick数据
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
  }
}
```

##### 交易数据推送

```json
// 订单状态更新
{
  "channel": "order",
  "data": {
    "id": "ord123456",
    "symbol": "AAPL",
    "direction": "LONG",
    "offset": "OPEN",
    "type": "LIMIT",
    "price": 150.5,
    "volume": 100,
    "traded": 50,
    "status": "PARTTRADED",
    "gateway_name": "IB",
    "updated_at": "2023-10-15T08:31:00Z"
  }
}

// 成交推送
{
  "channel": "trade",
  "data": {
    "id": "trd123456",
    "order_id": "ord123456",
    "symbol": "AAPL",
    "direction": "LONG",
    "offset": "OPEN",
    "price": 150.5,
    "volume": 50,
    "gateway_name": "IB",
    "datetime": "2023-10-15T08:31:00Z"
  }
}
```

## 4. 数据模型

### 4.1 核心数据模型

#### 4.1.1 用户模型

```python
class User:
    id: str                # 用户ID
    username: str          # 用户名
    email: str             # 邮箱
    phone: str             # 手机号
    is_active: bool        # 是否激活
    is_admin: bool         # 是否管理员
    created_at: datetime   # 创建时间
    last_login: datetime   # 最后登录时间
```

#### 4.1.2 交易接口模型

```python
class Gateway:
    id: str                # 接口ID
    name: str              # 接口名称
    type: str              # 接口类型 (CTP, IB, etc.)
    settings: dict         # 接口设置
    status: str            # 连接状态
    user_id: str           # 所属用户ID
```

#### 4.1.3 订单模型

```python
class Order:
    id: str                # 订单ID
    symbol: str            # 交易品种
    exchange: str          # 交易所
    direction: str         # 方向 (LONG, SHORT)
    offset: str            # 开平 (OPEN, CLOSE)
    type: str              # 订单类型 (LIMIT, MARKET)
    price: float           # 价格
    volume: float          # 数量
    traded: float          # 已成交数量
    status: str            # 状态
    gateway_name: str      # 接口名称
    created_at: datetime   # 创建时间
    updated_at: datetime   # 更新时间
    user_id: str           # 所属用户ID
```

#### 4.1.4 成交模型

```python
class Trade:
    id: str                # 成交ID
    order_id: str          # 订单ID
    symbol: str            # 交易品种
    exchange: str          # 交易所
    direction: str         # 方向
    offset: str            # 开平
    price: float           # 价格
    volume: float          # 数量
    gateway_name: str      # 接口名称
    datetime: datetime     # 成交时间
    user_id: str           # 所属用户ID
```

#### 4.1.5 持仓模型

```python
class Position:
    symbol: str            # 交易品种
    exchange: str          # 交易所
    direction: str         # 方向
    volume: float          # 数量
    frozen: float          # 冻结数量
    price: float           # 均价
    pnl: float             # 盈亏
    yd_volume: float       # 昨仓数量 (期货特有)
    gateway_name: str      # 接口名称
    user_id: str           # 所属用户ID
```

#### 4.1.6 策略模型

```python
class Strategy:
    id: str                # 策略ID
    name: str              # 策略名称
    class_name: str        # 策略类名
    parameters: dict       # 策略参数
    variables: dict        # 策略变量
    status: str            # 运行状态
    created_at: datetime   # 创建时间
    updated_at: datetime   # 更新时间
    user_id: str           # 所属用户ID
```

### 4.2 数据库模式

#### 4.2.1 MongoDB集合

1. **users**: 用户信息
2. **gateways**: 交易接口配置
3. **orders**: 订单记录
4. **trades**: 成交记录
5. **positions**: 持仓记录
6. **strategies**: 策略配置
7. **bars**: K线数据
8. **ticks**: Tick数据
9. **logs**: 系统日志

#### 4.2.2 索引设计

```javascript
// users集合索引
db.users.createIndex({ "username": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })

// orders集合索引
db.orders.createIndex({ "user_id": 1 })
db.orders.createIndex({ "symbol": 1 })
db.orders.createIndex({ "created_at": 1 })

// trades集合索引
db.trades.createIndex({ "user_id": 1 })
db.trades.createIndex({ "order_id": 1 })
db.trades.createIndex({ "datetime": 1 })

// bars集合索引
db.bars.createIndex({ "symbol": 1, "interval": 1, "datetime": 1 }, { unique: true })
```

## 5. 组件接口

### 5.1 核心引擎接口

#### 5.1.1 主引擎接口

```python
class STMainEngine:
    """SimpleTrade主引擎"""
    
    def __init__(self, event_engine=None):
        """初始化"""
        
    def add_gateway(self, gateway_class):
        """添加接口"""
        
    def add_app(self, app_class):
        """添加应用"""
        
    def connect(self, setting, gateway_name):
        """连接接口"""
        
    def subscribe(self, symbols, gateway_name):
        """订阅行情"""
        
    def send_order(self, symbol, direction, offset, price, volume, gateway_name):
        """发送订单"""
        
    def cancel_order(self, order_id, gateway_name):
        """撤销订单"""
        
    def get_engine(self, engine_name):
        """获取引擎"""
        
    def get_gateway(self, gateway_name):
        """获取接口"""
        
    def get_all_gateways(self):
        """获取所有接口"""
        
    def get_all_apps(self):
        """获取所有应用"""
```

#### 5.1.2 事件引擎接口

```python
class EventEngine:
    """事件引擎"""
    
    def __init__(self):
        """初始化"""
        
    def start(self):
        """启动"""
        
    def stop(self):
        """停止"""
        
    def register(self, event_type, handler):
        """注册事件处理函数"""
        
    def unregister(self, event_type, handler):
        """注销事件处理函数"""
        
    def put(self, event):
        """推送事件"""
```

### 5.2 插件接口

#### 5.2.1 交易增强插件接口

```python
class STTraderEngine:
    """交易增强引擎"""
    
    def __init__(self, main_engine, event_engine):
        """初始化"""
        
    def place_advanced_order(self, symbol, direction, offset, price, volume, gateway_name, **kwargs):
        """下高级订单"""
        
    def place_conditional_order(self, symbol, direction, offset, price, volume, gateway_name, condition):
        """下条件单"""
        
    def close_position(self, position, price=0, gateway_name=None):
        """平仓"""
        
    def close_all_positions(self, gateway_name=None):
        """全部平仓"""
```

#### 5.2.2 数据管理插件接口

```python
class STDataEngine:
    """数据管理引擎"""
    
    def __init__(self, main_engine, event_engine):
        """初始化"""
        
    def load_bar_data(self, symbol, exchange, interval, start, end):
        """加载K线数据"""
        
    def load_tick_data(self, symbol, exchange, start, end):
        """加载Tick数据"""
        
    def download_bar_data(self, symbol, exchange, interval, start, end):
        """下载K线数据"""
        
    def save_bar_data(self, bars):
        """保存K线数据"""
        
    def save_tick_data(self, ticks):
        """保存Tick数据"""
```

#### 5.2.3 机器学习插件接口

```python
class STMLEngine:
    """机器学习引擎"""
    
    def __init__(self, main_engine, event_engine):
        """初始化"""
        
    def load_data(self, symbol, start_date, end_date, interval="1d"):
        """加载数据"""
        
    def calculate_features(self, df):
        """计算特征"""
        
    def train_model(self, symbol, model_name, **kwargs):
        """训练模型"""
        
    def predict(self, symbol, model_name):
        """预测"""
        
    def analyze(self, symbol, **kwargs):
        """分析"""
```

#### 5.2.4 微信接口插件接口

```python
class STWechatEngine:
    """微信接口引擎"""
    
    def __init__(self, main_engine, event_engine):
        """初始化"""
        
    def start(self):
        """启动服务"""
        
    def stop(self):
        """停止服务"""
        
    def get_account_info(self, user_id):
        """获取账户信息"""
        
    def place_order(self, user_id, symbol, direction, offset, price, volume):
        """下单"""
        
    def send_notification(self, user_id, message):
        """发送通知"""
```

## 6. 安全规范

### 6.1 认证与授权

1. **JWT认证**:
   - 使用JWT进行API认证
   - Token有效期为2小时
   - 支持刷新Token机制

2. **权限控制**:
   - 基于角色的访问控制 (RBAC)
   - 用户角色: 普通用户、高级用户、管理员
   - 资源级权限控制

### 6.2 数据安全

1. **数据加密**:
   - 传输加密: 使用HTTPS/WSS
   - 存储加密: 敏感数据加密存储
   - 密码哈希: 使用bcrypt算法

2. **安全措施**:
   - API请求限流
   - 防SQL注入
   - 防XSS攻击
   - CSRF保护

## 7. 性能规范

### 7.1 响应时间

1. **API响应时间**:
   - 90%的API请求响应时间<200ms
   - 99%的API请求响应时间<500ms

2. **WebSocket延迟**:
   - 行情数据推送延迟<100ms
   - 订单状态更新延迟<200ms

### 7.2 吞吐量

1. **API吞吐量**:
   - 支持每秒至少100个API请求
   - 高峰期可扩展至每秒500个请求

2. **WebSocket连接**:
   - 支持至少1000个并发WebSocket连接
   - 每个连接支持多个订阅主题

### 7.3 资源使用

1. **CPU使用率**:
   - 正常负载下<30%
   - 峰值负载下<70%

2. **内存使用**:
   - 基础内存占用<1GB
   - 峰值内存占用<4GB

3. **存储需求**:
   - 系统基础存储<10GB
   - 每用户数据存储<1GB

## 8. 依赖关系

### 8.1 外部依赖

1. **vnpy框架**: v2.2.0或更高版本
2. **Python**: 3.7或更高版本
3. **MongoDB**: 4.4或更高版本
4. **Redis**: 6.0或更高版本

### 8.2 第三方库

1. **Web框架**: FastAPI 0.68.0+
2. **WebSocket**: websockets 10.0+
3. **数据处理**: pandas 1.3.0+, numpy 1.20.0+
4. **机器学习**: scikit-learn 1.0.0+, PyTorch 1.9.0+
5. **图表库**: matplotlib 3.4.0+
6. **技术指标**: ta-lib 0.4.0+

## 9. 部署规范

### 9.1 环境配置

1. **开发环境**:
   - 本地开发环境
   - 测试数据库
   - 模拟交易接口

2. **测试环境**:
   - 独立测试服务器
   - 测试数据库
   - 模拟交易接口

3. **生产环境**:
   - 高可用服务器集群
   - 生产数据库集群
   - 实盘交易接口

### 9.2 部署流程

1. **容器化部署**:
   - 使用Docker容器
   - 使用docker-compose管理服务
   - 支持Kubernetes部署

2. **CI/CD流程**:
   - 代码提交触发自动测试
   - 测试通过后自动构建
   - 手动触发部署

### 9.3 监控与日志

1. **系统监控**:
   - 服务器资源监控
   - 应用性能监控
   - 接口连接状态监控

2. **日志管理**:
   - 集中式日志收集
   - 日志分级存储
   - 日志分析和告警

## 10. 测试规范

### 10.1 单元测试

1. **测试框架**: pytest
2. **测试覆盖率**: 核心功能>80%
3. **测试类型**:
   - 功能测试
   - 边界测试
   - 异常测试

### 10.2 集成测试

1. **测试范围**:
   - API接口测试
   - 组件交互测试
   - 数据流测试

2. **测试环境**:
   - 独立测试环境
   - 模拟交易接口
   - 测试数据集

### 10.3 性能测试

1. **测试工具**: Locust
2. **测试指标**:
   - 响应时间
   - 吞吐量
   - 错误率
   - 资源使用率

3. **测试场景**:
   - 正常负载测试
   - 峰值负载测试
   - 长时间稳定性测试

## 11. 修订历史

| 版本 | 日期 | 描述 | 作者 |
|-----|------|------|------|
| 0.1 | 2023-10-15 | 初稿 | AI助手 |
