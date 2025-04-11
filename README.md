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

## 技术栈

- 后端: Python, vnpy框架(直接使用源码)
- API: FastAPI
- 数据库: SQLite
- 前端: 微信小程序, H5
- AI: Scikit-learn, PyTorch, OpenAI API

## 项目结构

```
simpletrade/
├── simpletrade/        # 核心代码包
│   ├── core/           # 核心引擎和功能
│   ├── apps/           # 自定义应用
│   ├── api/            # API服务
│   ├── models/         # 数据模型
│   └── utils/          # 工具函数
├── vnpy/               # vnpy源码(Git子模块)
├── docs/               # 项目文档
├── tests/              # 测试代码
├── scripts/            # 脚本工具
├── ui/                 # UI设计和原型
└── ai_context/         # AI协作上下文
```

## 安装与配置

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/simpletrade.git
cd simpletrade
```

### 2. 初始化vnpy子模块

```bash
git submodule update --init
```

### 3. 安装依赖

```bash
# 安装项目依赖
pip install -e .

# 安装vnpy依赖
python scripts/setup_vnpy.py
```

### 4. 运行

```bash
python -m simpletrade.main
```

## 开发指南

### 1. 环境设置

推荐使用虚拟环境进行开发：

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
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

- [功能需求文档](docs/functional_requirements.md)
- [技术规格文档](docs/technical_specification.md)
- [vnpy集成指南](docs/vnpy_integration_guide.md)
- [vnpy集成方案](docs/vnpy_integration_plan.md)
- [架构设计](docs/architecture_diagram.md)

## 许可证

[待定]
