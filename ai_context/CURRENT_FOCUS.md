# SimpleTrade 当前工作重点

**最后更新**: 2024-04-12 15:30

## 当前Sprint目标
完善Web前端开发，增强用户界面和交互体验，**开始进行前后端联调**。 (**阻塞：核心数据下载功能因 Tiger Gateway 加载问题受阻**)

## 活跃任务

1. **AI协作方式优化**
   - 优先级: 高
   - 状态: 已完成
   - 描述: 设计并实施更高效的AI协作方式，减少重复说明上下文的需求
   - 相关文件: `ai_context/PROJECT_STATUS.md`, `ai_context/CURRENT_FOCUS.md`, `ai_context/DECISIONS_LOG.md`, `ai_context/AI_COLLABORATION_GUIDE.md`
   - 成果: 创建了AI上下文管理结构和初始文件
   - 完成时间: 2023-10-15 13:30

2. **项目架构设计**
   - 优先级: 高
   - 状态: 已完成
   - 描述: 设计项目的整体架构，包括组件关系、数据流和部署架构
   - 相关文件: `docs/architecture_diagram.md`
   - 成果: 完成了详细的架构设计文档，包括轻量级数据存储方案
   - 完成时间: 2023-10-15 14:20

3. **项目结构创建**
   - 优先级: 高
   - 状态: 已完成
   - 描述: 创建独立的SimpleTrade项目结构，不再依赖于vnpy源码环境
   - 相关文件: 项目根目录下的所有基础文件和目录
   - 成果: 创建了标准的Python项目结构，包括核心包、文档和测试目录
   - 完成时间: 2023-10-15 14:45

4. **项目环境搭建方案**
   - 优先级: 高
   - 状态: 已完成
   - 描述: 设计项目开发环境和基础架构，包括vnpy源码集成、数据库配置等
   - 相关文件: `docs/vnpy_integration_plan.md`, `scripts/setup_vnpy.py`, `scripts/update_vnpy.py`
   - 成果: 详细的环境搭建文档和脚本，并在conda环境中成功安装，规定所有应用安装必须使用conda，并始终使用同一个simpletrade环境
   - 进度: 100%
   - 完成时间: 2024-04-11 17:50

5. **vnpy源码集成方案设计**
   - 优先级: 高
   - 状态: 已完成
   - 描述: 设计vnpy源码集成方案，包括目录结构、依赖管理、源码引用和版本控制策略
   - 相关文件: `docs/vnpy_integration_plan.md`, `.gitmodules`
   - 进度: 100%
   - 完成时间: 2024-04-11 17:50
   - 注意: 更新了方案，使用vnpy的最新版本（4.0.0+）而非原计划的2.3.0版本

6. **核心引擎代码框架设计**
   - 优先级: 高
   - 状态: 进行中
   - 描述: 设计扩展vnpy的核心引擎的代码框架
   - 相关文件: `simpletrade/core/engine.py`, `simpletrade/core/app.py`
   - 进度: 80%
   - 最后更新: 2024-04-11 17:50
   - 注意: 代码框架已设计，并已在conda环境中测试

7. **vnpy源码实际集成**
   - 优先级: 高
   - 状态: 已完成
   - 描述: 执行实际的vnpy源码集成操作，包括初始化Git仓库、添加子模块、安装依赖等
   - 相关文件: `.gitmodules`, `vnpy/`
   - 成果: 成功集成vnpy源码并在conda环境中安装
   - 完成时间: 2024-04-11 17:50

8. **数据管理功能开发**
   - 优先级: 高
   - 状态: 已完成
   - 描述: 开发数据管理功能，包括数据查询、导入、导出、删除等，并集成vnpy的数据模型和管理功能
   - 相关文件: `simpletrade/core/data/manager.py`, `simpletrade/core/data/__init__.py`, `simpletrade/api/data.py`
   - 成果: 成功实现数据管理功能，包括API接口和消息处理器
   - 完成时间: 2024-04-12 14:00

9. **API服务框架开发**
   - 优先级: 高
   - 状态: 已完成
   - 描述: 设计并实现API服务框架，提供RESTful API和WebSocket接口
   - 相关文件: `simpletrade/api/data.py`, `simpletrade/api/analysis.py`, `simpletrade/api/wechat/data.py`
   - 成果: 成功实现数据管理和数据分析的API接口
   - 完成时间: 2024-04-12 14:00

10. **数据分析功能开发**
    - 优先级: 高
    - 状态: 已完成
    - 描述: 开发数据分析功能，包括技术指标计算和策略回测
    - 相关文件: `simpletrade/core/analysis/indicators.py`, `simpletrade/core/analysis/backtest.py`, `simpletrade/api/analysis.py`
    - 成果: 成功实现技术指标计算和策略回测功能，并提供API接口
    - 完成时间: 2024-04-12 14:00

11. **Web前端开发**
    - 优先级: 高
    - 状态: 已完成
    - 描述: 开发简单的Web前端，包括数据管理和数据分析功能
    - 相关文件: `web-frontend/`
    - 成果: 成功实现数据管理和数据分析的Web前端界面
    - 完成时间: 2024-04-12 16:30

12. **项目结构重组**
    - 优先级: 高
    - 状态: 已完成
    - 描述: 重组项目结构，使其更加清晰和有组织
    - 相关文件: `tests/`, `examples/`, `docs/`
    - 成果: 成功重组项目结构，创建了测试、示例和文档目录
    - 完成时间: 2024-04-12 16:30

13. **Web前端启动问题解决**
    - 优先级: 高
    - 状态: 已完成
    - 描述: 解决Web前端启动问题，包括API服务器启动错误和npm安装依赖错误
    - 相关文件: `simpletrade/api/server.py`, `scripts/start_web_frontend.py`, `scripts/start_simple_web.py`, `web-frontend/public/simple.html`
    - 成果: 成功解决Web前端启动问题，创建了简单版HTML前端，并修复API跨域问题和缺失的API端点
    - 完成时间: 2024-04-13 15:30

14. **老虎证券Gateway实现**
    - 优先级: 高
    - 状态: 已完成
    - 描述: 实现老虎证券Gateway，支持历史数据下载和实时数据订阅
    - 相关文件: `vnpy_tiger/vnpy_tiger/tiger_gateway.py`, `scripts/download_tiger_data.py`, `scripts/subscribe_tiger_data.py`, `scripts/test_tiger_gateway.py`
    - 成果: 成功实现老虎证券Gateway，并集成到SimpleTrade项目中，支持历史数据下载和实时数据订阅
    - 完成时间: 2024-04-13 17:30

15. **老虎证券Gateway文档编写**
    - 优先级: 高
    - 状态: 已完成
    - 描述: 编写老虎证券Gateway相关文档，包括集成指南和使用指南
    - 相关文件: `docs/tiger_gateway_integration.md`, `docs/tiger_gateway_usage.md`
    - 成果: 成功编写了详细的老虎证券Gateway文档，包括安装、配置、数据下载和实时数据订阅等功能的说明
    - 完成时间: 2024-04-13 18:00

16. **[更新] Web前端开发与完善**
    - 状态: 进行中
    - 进度: 80%
    - 描述: 基本UI框架完成，**后端阻塞 API `/api/data/overview` 已修复**，准备进行数据相关功能的联调。
    - 相关文件: `web-frontend/`
    - 计划完成时间: 待定

17. **[更新] 修复 `/api/data/overview` 返回调试数据的问题**
    - 优先级: 紧急
    - 状态: **已解决**
    - 描述: 通过定位正确的 API 文件 (`routes.py`)、修复引擎初始化、依赖注入和方法调用链中的多个问题，最终解决了此问题。旧 API 文件已被移除。
    - 相关文件: `simpletrade/apps/st_datamanager/api/routes.py`, `simpletrade/apps/st_datamanager/engine.py`
    - 完成时间: [当前日期 时间]

18. **[更新] 实现数据下载功能 (方案A)**
    - 优先级: 高
    - 状态: **进行中 (阻碍: Tiger Gateway 加载问题)**
    - 进度: 40%
    - 描述: 已移除对 `vnpy_datamanager` 的依赖，在 `STDataManagerEngine` 中实现了 `download_bar_data` 的框架逻辑（含按需连接）。调试过程中遇到 `vnpy_tiger` 加载失败问题，已确认模块可在 Python 解释器中导入，但应用启动时可能仍存在问题。
    - 相关文件: `simpletrade/apps/st_datamanager/engine.py`, `simpletrade/apps/st_datamanager/api/routes.py`, `simpletrade/main.py`, `vnpy_tiger/`

19. **[新增] 实现数据导入功能 (方案A)**
    - 优先级: 高
    - 状态: **已完成 (代码实现，待测试)**
    - 描述: 在 `STDataManagerEngine` 中使用 pandas 实现了 `import_data_from_csv` 方法，不依赖 `vnpy_datamanager`。
    - 相关文件: `simpletrade/apps/st_datamanager/engine.py`, `simpletrade/apps/st_datamanager/api/routes.py`

20. **测试计划文档编写**
    - 优先级: 高
    - 状态: 待开始
    - 描述: 编写详细的测试策略、测试用例和测试环境规范
    - 相关文件: `docs/test_plan.md`
    - 预期成果: 完整的测试计划文档，包括单元测试、集成测试和性能测试策略

22. **[新增] 启动指南文档编写**
    - 优先级: 中
    - 状态: **已完成**
    - 描述: 创建详细的启动指南文档，记录了正确的后端和前端启动方式，以及如何验证 vnpy_tiger 的加载状态。
    - 相关文件: `docs/startup_guide.md`
    - 完成时间: 2024-04-12 15:30

21. **部署和运维文档编写**
    - 优先级: 中
    - 状态: 待开始
    - 描述: 编写系统部署流程、环境要求和监控方案
    - 相关文件: `docs/deployment_operations.md`
    - 预期成果: 详细的部署指南和运维手册

## 阻碍/问题
- ~~[移除] API服务器运行时加载旧代码/调试代码~~
- 需要确定具体的测试框架和工具
- 需要决定是否使用Docker进行部署
- 需要确定微信小程序与后端的具体交互方式
- **[新增] `vnpy_tiger` 加载失败**: 尽管执行了 `pip install -e .` 并且依赖 `tigeropen` 已确认安装，应用启动时仍报告 `vnpy_tiger not found`。需要干净重启应用后再次验证。
- **[新增] 环境依赖管理冲突风险**: 项目指南要求优先 `conda`，但调试中使用了 `pip` 安装本地包 (`-e .`) 和依赖 (`tigeropen`)，需关注潜在冲突。
- **数据库无数据**: 需要通过下载或导入添加数据。
- **Pydantic V2 警告**

## 本周目标
1. ✅ 完成vnpy源码集成方案设计
2. ✅ 执行实际的vnpy源码集成操作
3. ✅ 测试运行主程序，验证集成是否成功
4. ✅ 开发数据管理功能，包括数据查询、导入、导出、删除等
5. ✅ 实现数据管理API接口
6. ✅ 完成数据分析功能开发
7. ✅ 完成API接口开发
8. ✅ 开发简单的Web前端，包括数据管理和数据分析功能
9. ✅ 重组项目结构，使其更加清晰和有组织
10. ✅ 解决Web前端启动问题，包括API服务器启动错误和npm安装依赖错误
11. ✅ 实现老虎证券Gateway，支持历史数据下载和实时数据订阅
12. ✅ 编写老虎证券Gateway相关文档，包括集成指南和使用指南
13. ✅ 完善Web前端，增强用户界面和交互体验 (基本框架完成)
14. ✅ 开发交易中心、回测系统和AI分析等功能模块 (基本框架完成)
15. ✅ 定位并**解决**前后端联调中的系列问题 (API 可用)。
16. ~~⏳ 修复自定义 App 初始化 TypeError。~~ (已包含在 15 中)
17. ✅ **解决 `/api/data/overview` 返回调试数据的问题。**
18. ⏳ **继续排查 `vnpy_tiger` 加载问题** (进度: 50%)
19. ✅ **实现数据导入功能 (方案A)** (代码完成)。
20. ✅ **创建启动指南文档** (已完成)

## 下一步具体行动
1.  **[最优先] 继续排查 `vnpy_tiger` 在应用启动时的加载问题**:
   - 添加更详细的日志输出
   - 考虑在代码中显式添加 vnpy_tiger 到 sys.path
   - 测试其他 Gateway 是否可以正常工作
2.  **测试数据下载**: (前提：`vnpy_tiger` 加载成功) 调用 `/api/data/download` (interval="d") 尝试下载少量数据。
3.  **验证数据下载**: 确认数据是否成功入库 (检查日志和 `/api/data/overview`)。
4.  **测试数据导入**: 准备CSV文件，调用 `/api/data/import` 测试 `import_data_from_csv` 功能。
5.  (数据可用后) 联调数据管理: 连接前端与后端API (概览、下载状态、导入、导出、删除、查看)。
6.  连接仪表盘的市场概览与后端API或WebSocket。
7.  实现交易中心等其他模块与后端API的对接。
8.  编写测试计划文档和单元测试。
9.  添加数据可视化组件。
10. 测试老虎证券Gateway (连接和交易功能)。
11. 编写用户文档。
12. 处理 Pydantic V2 警告。
