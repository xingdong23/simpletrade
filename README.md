# SimpleTrade

简单易用的个人量化交易平台，采用微信小程序/消息交互作为前端，支持策略交易、AI分析和实时监控等功能。

## 项目概述

SimpleTrade是一个为个人投资者设计的量化交易平台，旨在让普通个人用户也能轻松使用量化交易技术。项目直接使用vnpy源码作为基础，通过插件架构扩展功能。

## 主要特点

- 简单易用的交易界面
- 微信小程序和消息交互作为主要前端
- 策略管理与回测功能
- AI分析和决策支持
- 实时监控和通知
- 支持多种交易接口，包括IB和老虎证券

## 技术栈

- 后端: Python, vnpy框架(直接使用源码)
- API: FastAPI
- 数据库: SQLite
- 前端: 微信小程序, H5
- AI: Scikit-learn, PyTorch, OpenAI API

## 项目结构

```
simpletrade/
├── docs/                  # 项目文档
├── simpletrade/           # 主要代码包
│   ├── api/               # API接口
│   │   ├── data.py        # 数据管理API
│   │   ├── analysis.py    # 数据分析API
│   │   ├── server.py      # API服务器
│   │   └── wechat/        # 微信小程序API
│   ├── core/              # 核心功能
│   │   ├── data/          # 数据管理
│   │   ├── message/       # 消息处理
│   │   └── analysis/      # 数据分析
│   └── apps/              # 应用模块
│       └── st_datamanager/ # 数据管理应用
├── tests/                 # 测试代码
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   ├── scripts/           # 测试脚本
│   └── conftest.py        # 测试配置
├── examples/              # 示例代码
├── scripts/               # 脚本工具
├── vnpy/                  # vnpy子模块
├── vnpy_tiger/            # 老虎证券Gateway
├── web-frontend/          # Web前端
├── ai_context/            # AI协作上下文
├── setup.py               # 包安装配置
└── README.md              # 项目说明
```

## 安装与配置

### 1. 克隆仓库

```bash
git clone --recursive https://github.com/yourusername/simpletrade.git
cd simpletrade
```

注意`--recursive`参数，这是为了同时克隆vnpy子模块。

### 2. 创建Conda环境

```bash
conda create -n simpletrade python=3.8
conda activate simpletrade
```

### 3. 安装依赖

```bash
# 安装vnpy
cd vnpy
pip install -e .
cd ..

# 安装simpletrade
pip install -e .
```

### 4. 运行示例

```bash
# 运行数据管理示例
python examples/data_management_example.py

# 运行API服务示例
python examples/api_example.py
```

### 5. 运行测试

```bash
# 安装pytest
pip install pytest

# 运行单元测试
pytest tests/unit

# 运行集成测试
pytest tests/integration
```

## 运行项目 (开发模式)

确保您已按照"安装与配置"部分设置好环境。

### 1. 启动后端 API 服务

在项目根目录下的**系统终端**中执行以下命令：

```bash
# 激活 Conda 环境
conda activate simpletrade

# 启动 Uvicorn 服务器 (监听 0.0.0.0:8000，带自动重载)
# 注意：必须在激活的 simpletrade 环境中运行
uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8000 --reload
```

后端服务启动后，可以通过 `http://localhost:8000/docs` 访问 API 文档。

### 2. 启动前端开发服务器

在项目根目录下的**另一个系统终端**中执行以下命令：

```bash
# 激活 Conda 环境 (如果需要 Node/npm，确保它们在此环境或系统路径中)
conda activate simpletrade

# 进入前端目录
cd web-frontend

# 安装依赖 (如果尚未安装)
npm install

# 启动开发服务器 (通常监听 localhost:8080 或类似端口)
npm run serve
```

前端服务启动后，留意终端输出的确切访问地址，然后在浏览器中打开该地址。

**重要提示**: 
- 两个服务都需要保持运行状态。
- 所有后端相关的操作（包括启动 uvicorn）**必须**在激活的 `simpletrade` Conda 环境中进行。

## 开发指南

### 1. 环境设置

推荐使用Conda环境进行开发：

```bash
conda create -n simpletrade python=3.8
conda activate simpletrade

# 安装开发依赖
pip install pytest black isort
```

### 2. 代码规范

- 遵循PEP 8编码规范
- 使用类型注解
- 编写详细的文档字符串
- 编写单元测试

### 3. 提交规范

- 使用明确的提交信息
- 提交前运行测试
- 遵循分支管理策略

## 文档

详细文档请参阅`docs/`目录：

- [项目结构](docs/project_structure.md)
- [安装指南](docs/installation.md)
- [API参考](docs/api_reference.md)
- [功能需求文档](docs/functional_requirements.md)
- [技术规格文档](docs/technical_specification.md)
- [vnpy集成指南](docs/vnpy_integration_guide.md)
- [架构设计](docs/architecture_diagram.md)
- [老虎证券Gateway集成指南](docs/tiger_gateway_integration.md)
- [老虎证券Gateway使用指南](docs/tiger_gateway_usage.md)

## 许可证

[待定]
