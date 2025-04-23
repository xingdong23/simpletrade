# SimpleTrade 开发进度与任务追踪

## 今日工作 (2025-04-23)

1.  **项目理解:** 阅读了 `simpletrade` 项目中 `core`, `apps`, `services`, `api`, `config` 等核心包的 `README.md` 文件，初步了解了项目结构和各模块功能。
2.  **启动错误排查与修复:**
    *   解决了 `main.py` 启动时因 `STBaseApp` 初始化参数不匹配导致的 `TypeError`。 (修改了 `core/app.py`)
    *   解决了因 `vnpy` 内部 `add_engine` 方法调用签名与 `STBaseEngine` 定义不匹配导致的 `TypeError`。 (覆盖了 `core/engine.py` 中的 `add_app` 方法)
    *   解决了覆盖 `add_app` 后导致 `CtaEngine` 初始化参数数量错误的 `TypeError`。 (在 `add_app` 中添加了基于 `inspect` 的智能参数判断)
    *   解决了添加 `CtaStrategyApp` 时因传递字符串而非类导致的 `TypeError`。 (修改了 `core/initialization.py`)
    *   修复了多处因 `get_db` 函数导入路径错误 (`config.database` 应为 `api.deps`) 导致的 `ImportError`，涉及文件：`api/routers/strategies.py`, `services/strategy_service.py`, `services/monitor_service.py`。
    *   修复了因尝试导入不存在的 `BaseStrategy` 导致的 `ImportError`，改为导入正确的 `vnpy_ctastrategy.template.CtaTemplate`。 (修改了 `services/strategy_service.py`)
    *   修复了因尝试导入不存在的 `StrategyRun` 和 `TradeRecord` 模型导致的 `ImportError`。 (修改了 `services/monitor_service.py`)
    *   修复了因尝试导入不存在的 `User` 模型导致的 `ModuleNotFoundError`。 (注释了 `api/routers/strategies.py` 中的导入)
3.  **功能增强:**
    *   修改了 `main.py`，使其能够在启动核心引擎的同时，在后台线程中启动 FastAPI/Uvicorn API 服务器。
    *   对比 `docker_scripts/run_api.py`，为 `main.py` 添加了 API 服务器配置步骤 (`configure_server` 调用) 和后台数据同步任务的启动逻辑（尽管同步任务因 `get_db` 导入问题暂时禁用）。

## 任务进度

*   **主要目标达成:** `simpletrade/main.py` 脚本现在可以成功运行，不再因初始化过程中的 `TypeError` 或 `ImportError` 而崩溃。
*   **核心引擎与 API 服务同时启动:** 实现了通过运行 `main.py` 同时启动 SimpleTrade 核心引擎和 FastAPI API 服务器的功能。
*   **API 路由加载:** 大部分 API 路由（Data, WeChat(placeholder), Analysis, Strategies）现在可以成功加载（除 Strategies 外，其他路由的实际功能性待验证）。

## 遗留问题与后续任务

- [ ] **修复后台数据同步导入:**
    - **文件:** `simpletrade/services/data_sync_service.py`
    - **任务:** 将 `get_db` 的导入路径从 `simpletrade.config.database` 改为 `simpletrade.api.deps`。
- [ ] **配置数据源 (Datafeed):**
    - **位置:** VnPy 全局 `SETTINGS`
    - **任务:** 根据实际数据源配置 `SETTINGS["datafeed.name"]` 及相关参数。
- [ ] **处理缺失模型:**
    - **User:** 创建 `User` 模型并取消 `strategies.py` 中的注释（如果需要用户功能）。
    - **StrategyRun, TradeRecord:** 创建这两个模型并更新 `monitor_service.py` 等处的逻辑（如果需要策略运行持久化和交易记录功能）。
- [ ] **可选依赖安装:**
    - **包:** `vnpy_datamanager`, `vnpy_ib`, `vnpy_tiger`
    - **任务:** 如果需要，使用 `pip install` 安装。
- [ ] **API 功能验证:**
    - **范围:** 策略、监控等相关 API 端点。
    - **任务:** 测试 API 功能是否符合预期，特别注意因模型缺失或代码注释可能导致的问题。
- [ ] **完善 API 路由:**
    - **路由:** WeChat, Test, Health
    - **任务:** 实现或完善这些路由的功能。 