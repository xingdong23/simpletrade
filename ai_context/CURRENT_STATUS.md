# SimpleTrade 当前状态

**最后更新**: 2024-04-19 15:30

## 项目阶段
规划与设计 -> [当前] **需求重定义与前端原型设计** -> 核心功能开发 -> 扩展功能开发 -> 测试与优化 -> 部署上线

## 项目概述
SimpleTrade是一个为个人投资者设计的、易于上手的量化与实盘交易平台，采用Web界面交互，提供精选策略、便捷的回测与实盘对接，并通过内置数据服务和特色策略简化用户操作。

**核心特色**：策略参数调整、回测和实盘交易一体化设计，用户可以在同一界面中无缝切换不同阶段，大幅提高策略优化和实盘执行的效率。

## 技术栈
- 后端: Python, FastAPI
- 核心引擎/交易: 利用 vnpy 库 (标准安装，除了 `vnpy_tiger`)
- 数据库: PostgreSQL + TimescaleDB (或其他时序数据库)
- 数据处理: Pandas, NumPy
- AI: Qlib, Scikit-learn, PyTorch/TensorFlow
- 前端: Vue.js + Element UI
- 环境管理: Conda (`simpletrade` 环境)
- **特殊组件**: 自定义 `vnpy_tiger` (存放于 `vendors/` 目录)

## 已完成工作
- ✅ 项目整体初步规划与架构设计
- ✅ 项目名称确定为 "SimpleTrade"
- ✅ 创建独立项目结构
- ✅ 初始化Git仓库
- ✅ Conda 环境 (`simpletrade`) 配置基础
- ✅ 老虎证券 Gateway (`vnpy_tiger`) 的初步集成与测试 (代码位于 `vendors/`)
- ✅ 基础 Web 前端框架 (Vue.js) 搭建
- ✅ **前端原型设计与开发:**
    - 清理旧前端代码
    - 搭建应用导航与主布局
    - 开发策略中心页面 (策略库、策略构建器、我的策略)
      - **实现策略参数调整、回测和实盘交易一体化的界面设计**
      - **设计参数优化和策略比较功能界面**
      - **重构策略中心，实现新的层次化结构，包括基础策略、高级策略和组件库**
      - **增强策略卡片，添加复杂度和资源需求指示器**
      - **将策略详情从弹出框改为独立完整页面，以便更详细地展示复杂策略内容**
    - 开发交易中心页面 (账户概览、持仓、订单)
      - **与策略中心无缝集成，支持策略交易的实时监控和管理**
    - 开发 AI 分析中心页面 (市场分析、股票预测、模型训练)
    - 开发用户中心页面 (个人资料、账户设置、订阅管理)
    - **采用Element UI框架实现专业、美观的量化交易界面**
- ✅ 修复StrategyCenterView.vue文件中的标签嵌套问题
- ✅ 实现策略详情独立页面
- ✅ 修复 talib 与 vnpy 兼容性问题，解决 `symbol not found in flat namespace '_TA_ACCBANDS'` 错误
- ✅ 修复 WeChat Mini Program API 路由中的 `ApiResponseModel` 命名错误
- ✅ 更新项目文档，包括项目结构、安装指南和启动指南
- ✅ 添加缺失的 `/api/data/symbols` 接口，提供测试数据
- ✅ 修改前端 API 基地址，从 8000 改为 8003（因为 8002 端口已被占用）
- ✅ 成功启动了后端服务器，运行在 8003 端口
- ✅ 成功启动了前端服务器
- ✅ 修复了 `/api/data/symbols` 端点的 500 内部服务器错误
- ✅ **设计并实现了 MySQL 数据库结构**，包括交易品种、策略、用户策略和回测记录表
- ✅ **实现了数据库连接和 ORM 模型**，使用 SQLAlchemy
- ✅ **修改了 API 端点，从数据库获取数据**，而不是返回硬编码的测试数据
- ✅ **添加了策略相关的 API 端点**，包括获取策略列表、策略详情和用户策略
- ✅ **创建了数据库初始化脚本**，用于创建数据库表和添加示例数据
- ✅ **更新了 README 文件**，添加数据库设置说明
- ✅ **完善了策略管理系统**：
  - 增强了策略注册机制，添加了动态发现和注册策略的功能
  - 添加了策略分类和描述信息，使策略管理更加结构化
  - 创建了策略监控服务，提供对运行中策略的实时监控
  - 扩展了策略API接口，添加了策略创建、初始化、启动和停止的功能
  - 添加了数据可视化功能，提供回测结果的可视化展示
  - 编写了详细的策略管理系统文档

## 进行中工作
- 🔄 **前端与后端集成测试** (优先级: 高)
    - 启动前端服务，测试策略中心重构后的功能
    - 启动后端服务，测试API接口
    - 测试前端页面与后端 API 的交互
    - 进度: 50%
- 🔄 **MySQL 数据库集成测试** (优先级: 高)
    - 运行数据库初始化脚本，创建数据库表和添加示例数据
    - 测试 `/api/data/symbols` 端点，确保它能够从数据库获取交易品种
    - 测试策略相关的 API 端点，确保它们能够正确地从数据库获取数据
    - 进度: 0%
- 🔄 **前端界面优化** (优先级: 中)
    - 移除主布局中的API状态显示区域 [已完成]
    - 将策略详情从弹出框改为独立完整页面 [已完成]
    - 重构策略中心，实现新的层次化结构 [已完成]
    - 增强策略卡片，添加复杂度和资源需求指示器 [已完成]
    - 进度: 90%
- 🔄 **项目文档更新** (优先级: 中)
    - 更新核心 AI 协作文档 [进行中]
    - 创建长期规划路线图文档 [已完成]
    - 进度: 70%

## 待开始工作
- ⏳ **数据中心 (Data Hub) 开发 (后端):**
    - 设计并实现 PostgreSQL + TimescaleDB 数据库模型用于存储规范化行情数据
    - 实现数据导入器，支持从 CSV 和本地 Qlib 数据集导入历史数据
    - 实现数据转换层，将数据库数据按需转换为 Qlib 格式
    - 实现数据更新和管理逻辑
    - 提供内部数据访问 API (FastAPI)
- ⏳ **策略中心 (Strategy Center) 开发 (后端):**
    - 完善策略管理系统的前端集成
    - 实现策略监控页面，实时展示策略运行状态和性能指标
    - 实现回测结果的可视化展示
    - 优化监控服务的性能，减少对策略执行的影响
    - 添加更多策略类型，如机器学习策略、因子策略等
- ⏳ **交易中心 (Trading Center) 开发 (后端):**
    - 对接 Tiger Gateway 实现模拟交易和实盘交易执行
    - 实现账户信息管理（资产、持仓、订单）
- ⏳ **AI 分析中心 (后端):**
    - 集成 Qlib，实现基于平台数据的模型训练和分析功能

## 遇到的问题

### [前端标签嵌套问题] - 已解决
- **问题描述**: 在重构策略中心过程中发现StrategyCenterView.vue文件中的标签嵌套问题，导致页面无法正常编译和显示。
- **解决方案**: 重新组织标签页的结构，确保标签正确闭合。修复复杂度评分组件中的v-model语法错误。
- **状态**: **已解决**

### [需求与设计]
- **问题描述**: 项目需求发生重大调整，需根据新设计重新规划开发任务和技术细节。
- **状态**: **进行中 (前端原型设计已完成，正在进行前端优化)**

### [核心问题] Tiger Gateway 配置问题 - 已解决
- **问题描述**: 使用 Tiger Gateway 下载数据时遇到私钥格式或账户权限问题（如美国市场无权限）。
- **解决方案**: 已解决配置问题，可以正常使用Tiger Gateway。
- **状态**: **已解决**

### [环境依赖管理冲突风险] - 已解决
- **问题描述**: 项目混合使用 `conda` 管理环境，`pip` 可能用于安装 `conda` 源缺失的依赖 (如 `tigeropen`)，并手动管理 `vendors/vnpy_tiger`。
- **解决方案**: 已解决环境依赖管理问题，环境配置稳定。
- **状态**: **已解决**

### [已解决] talib与vnpy兼容性问题
- **问题描述**: 在启动后端服务时，遇到talib库相关的符号加载错误：`symbol not found in flat namespace '_TA_ACCBANDS'`。这个错误导致API路由无法正确注册，影响了后端服务的正常运行。问题可能是由于系统TA-Lib库（0.4.0）与Python ta-lib包（0.6.3）版本不匹配导致的。
- **解决方案**:
  1. 卸载旧版本的 ta-lib Python 包：`conda run -n simpletrade pip uninstall -y ta-lib`
  2. 重新安装 ta-lib 0.6.3 版本：`conda run -n simpletrade pip install ta-lib`
  3. 以开发模式安装 simpletrade 包：`conda run -n simpletrade pip install -e .`
     - 开发模式安装（`pip install -e .`）不会复制代码，而是在 Python 的 site-packages 目录中创建一个指向原始代码位置的链接
     - 这解决了 Python 路径和模块导入问题，使 Python 可以正确找到 `simpletrade.api` 模块
     - 开发者仍然可以直接在源码目录中开发，所有的修改都会立即生效
  4. 使用新的启动命令启动服务器：`conda run -n simpletrade python -m uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8002 --reload`
     - 注意端口从原来的 8000 改为 8002，以避免端口冲突
- **状态**: **已解决**

### [已解决] WeChat Mini Program API 路由错误
- **问题描述**: 在启动后端服务时，遇到 `name 'ApiResponseModel' is not defined` 错误。这是因为在 `simpletrade/api/wechat/data.py` 文件中使用了未定义的 `ApiResponseModel`。
- **解决方案**: 将 `simpletrade/api/wechat/data.py` 文件中的 `ApiResponseModel` 改为 `ApiResponse`。
- **状态**: **已解决**

### [已解决] 项目文档更新
- **问题描述**: 项目文档与当前代码不同步，导致开发者可能使用过时的信息。
- **解决方案**: 更新了项目结构、安装指南和启动指南文档，使其与当前代码保持一致。特别是添加了关于开发模式安装和启动命令的详细说明。
- **状态**: **已解决**

### [已解决] 数据 API 错误
- **问题描述**: `/api/data/symbols` 端点返回 500 内部服务器错误，可能是依赖注入问题
- **解决方案**: 修改了 `/api/data/symbols` 端点，移除了对 `engine` 参数的依赖，因为这个端点只返回静态数据，不需要访问数据管理引擎
- **状态**: **已解决**

### [已解决] 端口占用
- **问题描述**: 原计划使用的 8002 端口已被占用，改用 8003 端口
- **解决方案**: 修改了所有前端 API 调用的基地址，从 8002 改为 8003
- **状态**: **已解决**

### [已解决] 健康检查端点问题
- **问题描述**: 健康检查端点 `/api/health` 没有返回任何内容
- **解决方案**: 发现需要在 URL 末尾添加斜杠，正确的 URL 是 `/api/health/`
- **状态**: **已解决**

### [新问题] 数据库集成测试
- **问题描述**: 需要测试 MySQL 数据库集成，确保 API 端点能够正确地从数据库获取数据
- **状态**: **待测试**

### [待评估] Qlib 集成复杂度
- **问题描述**: 将 Qlib 集成到现有平台，需要适配数据格式、协调训练/回测流程，具体复杂度待评估。Qlib主要用于机器学习策略部分。
- **状态**: **待评估**

## 下一步计划
1. **[当前最优先]** **测试 MySQL 数据库集成:**
   - 运行数据库初始化脚本，创建数据库表和添加示例数据
   - 测试 `/api/data/symbols` 端点，确保它能够从数据库获取交易品种
   - 测试策略相关的 API 端点，确保它们能够正确地从数据库获取数据

2. **完成前后端集成测试:**
   - 使用已启动的后端服务器（端口 8003）测试前后端数据交互
   - 测试策略中心重构后的功能
   - 测试分析 API 功能，包括技术指标计算和策略回测

3. **与用户分享前端原型，收集反馈:**
   - 展示策略中心重构后的功能
   - 展示策略详情页面
   - 收集用户对基础策略和高级策略分类的反馈

4. **基于前端原型，与用户确认最终需求细节。**

5. **实现数据中心(Data Hub)后端:**
   - 基于 MySQL 数据库，实现数据导入和管理功能
   - 实现数据转换层，将数据库数据按需转换为 Qlib 格式

## 最近更新
- [2024-04-19 15:30]: 完善了策略管理系统，增强了策略注册机制，添加了策略监控和数据可视化功能
- [2024-04-19 14:00]: 创建了详细的策略管理系统文档，包括实施方案、使用指南和API规范
- [2024-04-19 10:30]: 实现了策略监控服务，提供对运行中策略的实时监控
- [2024-04-19 09:00]: 添加了数据可视化功能，提供回测结果的可视化展示
- [2024-04-18 16:30]: 增强了策略注册机制，添加了动态发现和注册策略的功能
- [2024-04-18 13:30]: 设计并实现了 MySQL 数据库结构，修改 API 端点从数据库获取数据
- [2024-04-18 12:45]: 修复了 `/api/data/symbols` 端点的 500 内部服务器错误
- [2024-04-18 12:30]: 成功启动了前端和后端服务器，开始前后端集成测试
- [2024-04-18 12:15]: 修改了前端 API 基地址，从 8000 改为 8003
- [2024-04-18 01:30]: 修复 WeChat Mini Program API 路由错误，更新项目文档，完善启动指南
