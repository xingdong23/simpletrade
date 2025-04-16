# SimpleTrade 策略管理系统

## 简介

SimpleTrade 策略管理系统是一个基于vnpy的量化交易策略管理平台，提供策略的创建、配置、回测、监控和可视化功能。系统充分利用vnpy的策略执行框架，同时提供更好的管理和用户体验。

## 主要功能

### 策略管理

- **策略发现**：自动发现和注册策略类
- **策略创建**：创建新的策略配置
- **策略配置**：配置策略参数
- **策略执行**：初始化、启动和停止策略

### 策略监控

- **实时状态**：监控策略的运行状态
- **性能指标**：跟踪策略的性能指标，如盈亏、胜率等
- **交易记录**：记录策略的交易历史
- **持仓信息**：显示策略的当前持仓

### 回测分析

- **策略回测**：使用历史数据回测策略
- **回测报告**：生成详细的回测报告
- **数据可视化**：提供资金曲线、回撤曲线、交易分布等可视化图表
- **回测记录**：保存和查询历史回测记录

### API接口

- **RESTful API**：提供完整的RESTful API接口
- **策略管理API**：管理策略的创建、配置、执行等
- **回测API**：执行回测和查询回测结果
- **监控API**：获取策略的实时监控数据

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/simpletrade.git
cd simpletrade

# 安装依赖
pip install -r requirements.txt
```

### 创建策略

1. 在`simpletrade/strategies`目录下创建新的策略文件，例如`my_strategy.py`
2. 实现策略类，继承自`CtaTemplate`
3. 系统会自动发现并注册新的策略类

示例策略：

```python
from vnpy.app.cta_strategy.template import CtaTemplate
from vnpy.trader.object import BarData
from vnpy.trader.utility import ArrayManager

class MyStrategy(CtaTemplate):
    """
    我的自定义策略
    """
    
    # 策略参数
    param1 = 10
    param2 = 20
    
    # 策略变量
    var1 = 0
    var2 = 0
    
    # 参数列表，用于UI显示
    parameters = ["param1", "param2"]
    
    # 变量列表，用于UI显示
    variables = ["var1", "var2"]
    
    def __init__(self, cta_engine, strategy_name, setting):
        """初始化"""
        super().__init__(cta_engine, strategy_name, setting)
        self.am = ArrayManager()
    
    def on_init(self):
        """策略初始化"""
        self.write_log("策略初始化")
        self.load_bar(10)
    
    def on_start(self):
        """策略启动"""
        self.write_log("策略启动")
    
    def on_stop(self):
        """策略停止"""
        self.write_log("策略停止")
    
    def on_bar(self, bar):
        """K线更新"""
        self.am.update_bar(bar)
        
        # 策略逻辑
        # ...
```

### 使用API

#### 获取策略列表

```bash
curl -X GET "http://localhost:8000/api/strategies/"
```

#### 创建策略

```bash
curl -X POST "http://localhost:8000/api/strategies/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的策略",
    "description": "这是我的自定义策略",
    "type": "MyStrategy",
    "category": "自定义",
    "parameters": {
      "param1": 15,
      "param2": 25
    }
  }'
```

#### 创建用户策略

```bash
curl -X POST "http://localhost:8000/api/strategies/user/create" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "strategy_id": 1,
    "name": "我的交易策略",
    "parameters": {
      "param1": 15,
      "param2": 25
    }
  }'
```

#### 初始化策略

```bash
curl -X POST "http://localhost:8000/api/strategies/user/1/init"
```

#### 启动策略

```bash
curl -X POST "http://localhost:8000/api/strategies/user/1/start"
```

#### 停止策略

```bash
curl -X POST "http://localhost:8000/api/strategies/user/1/stop"
```

#### 获取策略监控信息

```bash
curl -X GET "http://localhost:8000/api/strategies/monitor/1"
```

#### 运行回测

```bash
curl -X POST "http://localhost:8000/api/strategies/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": 1,
    "symbol": "AAPL",
    "exchange": "NASDAQ",
    "interval": "1d",
    "start_date": "2020-01-01",
    "end_date": "2020-12-31",
    "initial_capital": 100000
  }'
```

#### 获取回测记录

```bash
curl -X GET "http://localhost:8000/api/strategies/backtest/records"
```

## 架构设计

### 组件

- **数据库模型**：`Strategy`, `UserStrategy`, `BacktestRecord`
- **服务**：`StrategyService`, `BacktestService`, `MonitorService`
- **API**：RESTful API接口
- **可视化**：数据可视化模块

### 数据流

1. 用户通过API创建策略配置，存储在数据库中
2. 策略服务从数据库加载配置，转换为vnpy可用的格式
3. vnpy的CTA引擎执行策略，生成交易信号和执行交易
4. 监控服务实时监控策略状态和性能
5. 回测服务执行策略回测，生成回测结果
6. 数据可视化模块将回测结果转换为图表
7. API接口将数据返回给前端展示

## 贡献

欢迎贡献代码、报告问题或提出建议。请遵循以下步骤：

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
