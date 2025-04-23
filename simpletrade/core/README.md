# SimpleTrade Core 包

SimpleTrade 的 core 包是整个项目的核心，包含了基础组件和核心功能。它扩展了 vnpy 的核心功能，并提供了 SimpleTrade 特有的功能。

## 主要模块

### engine.py - 主引擎模块

`engine.py` 定义了 `STMainEngine` 类，继承自 vnpy 的 `MainEngine`，是整个系统的核心。

**主要功能**：

- 管理所有功能模块，包括交易接口和应用模块
- 添加了 SimpleTrade 特有的功能，如 `st_engines` 字典
- 处理日志事件
- 提供获取引擎实例的方法

**核心方法**：

```python
class STMainEngine(MainEngine):
    def __init__(self, event_engine=None):
        # 初始化
        
    def register_event(self):
        # 注册事件处理函数
        
    def process_log_event(self, event):
        # 处理日志事件
        
    def add_st_engine(self, engine_name, engine):
        # 添加SimpleTrade引擎
        
    def get_st_engine(self, engine_name):
        # 获取SimpleTrade引擎
        
    def connect(self, setting, gateway_name):
        # 连接交易接口
        
    def get_cta_engine(self):
        # 获取CTA策略引擎
```

### app.py - 应用基类模块

`app.py` 定义了 `STBaseApp` 和 `STBaseEngine` 类，是所有 SimpleTrade 应用和引擎的基类。

**主要功能**：

- 提供应用和引擎的基本结构和接口
- 定义应用和引擎的通用属性和方法
- 与 vnpy 的应用框架集成

**核心类**：

```python
class STBaseApp(BaseApp):
    app_type = "st"  # SimpleTrade应用类型
    app_name = ""    # 应用名称
    app_module = ""  # 应用模块
    app_path = ""    # 应用路径
    display_name = ""  # 显示名称
    engine_class = None  # 引擎类
    widget_class = None  # 界面类
    
    def __init__(self, main_engine, event_engine):
        # 初始化

class STBaseEngine(BaseEngine):
    def __init__(self, main_engine, event_engine, app_name):
        # 初始化
```

### initialization.py - 初始化模块

`initialization.py` 提供了系统初始化的功能，包括初始化事件引擎、主引擎、网关和应用。

**主要功能**：

- 初始化核心组件
- 加载网关和应用
- 配置系统参数

**核心函数**：

```python
def initialize_core_components():
    """初始化核心组件"""
    # 创建事件引擎和主引擎
    event_engine = EventEngine()
    main_engine = STMainEngine(event_engine)
    
    # 添加网关
    # ...
    
    # 添加应用
    main_engine.add_app(STMessageApp)
    main_engine.add_app(STTraderApp)
    main_engine.add_app(STDataManagerApp)
    main_engine.add_app(STAnalysisApp)
    
    # 添加vnpy原生应用
    if DataManagerApp:
        main_engine.add_app(DataManagerApp)
    # ...
    
    return main_engine, event_engine
```

## 与 vnpy 的关系

SimpleTrade 的 core 包主要是对 vnpy 的扩展和增强：

1. **继承关系**：
   - `STMainEngine` 继承自 vnpy 的 `MainEngine`
   - `STBaseApp` 继承自 vnpy 的 `BaseApp`
   - `STBaseEngine` 继承自 vnpy 的 `BaseEngine`

2. **功能复用**：
   - 直接使用 vnpy 的数据模型（如 `BarData`、`TickData`）
   - 直接使用 vnpy 的常量（如 `Exchange`、`Interval`）
   - 直接使用 vnpy 的数据库功能

3. **功能扩展**：
   - 添加了消息处理功能
   - 添加了 API 接口
   - 添加了更多的数据分析功能

## 设计说明

SimpleTrade 的 core 包采用了模块化设计，主要特点包括：

1. **分层架构**：
   - 核心层：提供基础功能和接口
   - 应用层：提供具体功能实现
   - 接口层：提供与外部系统的交互

2. **插件机制**：
   - 通过 `add_app` 方法加载应用
   - 应用可以独立开发和维护
   - 应用之间通过事件和引擎实例交互

3. **事件驱动**：
   - 使用 vnpy 的事件引擎
   - 通过事件实现模块间的松耦合
   - 支持异步处理

4. **配置灵活**：
   - 支持通过环境变量配置
   - 支持通过配置文件配置
   - 支持运行时动态配置

5. **职责分离**：
   - core 包只提供核心功能和基础接口
   - 具体功能实现在 apps 包中
   - 避免功能重复和职责不清

## 架构改进说明

为了使架构更加清晰和合理，我们进行了以下改进：

1. **移除了 core/data 目录**：
   - 数据管理功能完全由 `apps/st_datamanager` 提供
   - 避免了功能重复和职责不清

2. **移除了 core/message 目录**：
   - 消息处理功能完全由 `apps/st_message` 提供
   - 基础接口和具体实现都在同一个应用中

3. **移除了 core/analysis 目录**：
   - 分析功能完全由 `apps/st_analysis` 提供
   - 提供了完整的分析功能，包括技术指标计算、策略回测和可视化分析

4. **创建了 apps/st_analysis 应用**：
   - 将分析功能从 core 包移动到 apps 包中
   - 添加了 API 接口和消息指令处理功能

## 使用示例

```python
# 初始化核心组件
from simpletrade.core.initialization import initialize_core_components
main_engine, event_engine = initialize_core_components()

# 获取应用引擎
data_engine = main_engine.get_engine("st_datamanager")
message_engine = main_engine.get_engine("st_message")
trader_engine = main_engine.get_engine("st_trader")
analysis_engine = main_engine.get_engine("st_analysis")

# 使用数据管理功能
bars = data_engine.get_bar_data(
    symbol="AAPL",
    exchange=Exchange.SMART,
    interval=Interval.DAILY,
    start=datetime(2023, 1, 1),
    end=datetime(2023, 12, 31)
)

# 使用分析功能
df = analysis_engine.calculate_indicators(bars, ["ma", "macd", "rsi"])
results = analysis_engine.backtest_strategy(bars, {"ma_cross": {"fast": 5, "slow": 20}})

# 使用消息处理功能
message_engine.process_message("/data query bar AAPL SMART 1d 2023-01-01")
message_engine.process_message("/analysis indicator AAPL SMART 1d 2023-01-01 2023-12-31 ma macd")

# 使用交易功能
trader_engine.send_order(
    symbol="AAPL",
    exchange=Exchange.SMART,
    direction=Direction.LONG,
    offset=Offset.OPEN,
    price=150.0,
    volume=100,
    gateway_name="TIGER"
)
```

## 依赖关系

- 依赖 vnpy 及其相关包
- 依赖 pandas、numpy 等数据处理库
- 依赖 FastAPI、uvicorn 等 Web 框架
