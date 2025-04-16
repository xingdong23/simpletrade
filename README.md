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

- 后端: Python, vnpy框架 (标准库安装), FastAPI
- API: FastAPI
- 数据库: MySQL (主数据库), SQLite (本地测试)
- 前端: Vue 2.x, Element UI, ECharts, 微信小程序
- AI: Scikit-learn, PyTorch, OpenAI API
- **特殊组件**: 自定义 `vnpy_tiger` (存放于 `vendors/` 目录)

## 项目结构

```
simpletrade/
├── ai_context/            # AI协作上下文
├── docs/                  # 项目文档
├── examples/              # 示例代码
├── scripts/               # 脚本工具
├── simpletrade/           # 主要代码包
│   ├── api/               # API接口
│   │   ├── server.py      # API服务器
│   │   └── wechat/        # 微信小程序API
│   ├── apps/              # 应用模块
│   │   └── st_datamanager/ # 数据管理应用
│   ├── core/              # 核心功能
│   │   ├── data/          # 数据管理
│   │   ├── message/       # 消息处理
│   │   └── analysis/      # 数据分析
│   └── main.py            # 主程序入口
├── test_data/             # 测试数据目录
├── tests/                 # 测试代码
├── ui/                    # UI设计文件
├── vendors/               # 自定义/非pip安装的组件
│   └── vnpy_tiger/        # 自定义的老虎证券Gateway
├── web-frontend/          # Web前端
├── setup.py               # 包安装配置
└── README.md              # 项目说明
```

## 安装与配置

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/simpletrade.git
cd simpletrade
```

### 2. 创建Conda环境

```bash
conda create -n simpletrade python=3.10
conda activate simpletrade
```

### 3. 安装依赖

**重要**: 本项目采用混合依赖管理：
- vnpy 核心及官方插件通过 `pip` 安装。
- 自定义的 `vnpy_tiger` 网关位于 `vendors/vnpy_tiger` 目录，需要单独安装其依赖。

```bash
# 激活环境
conda activate simpletrade

# 推荐使用 pip 安装 vnpy 及其插件
# pip install vnpy vnpy_ctp vnpy_ib vnpy_tiger vnpy_datamanager vnpy_sqlite
# 安装 vnpy 核心及常用官方插件
pip install vnpy vnpy_ctp vnpy_ib vnpy_datamanager vnpy_sqlite # 注意：移除了 vnpy_tiger

# 安装 simpletrade 自身 (如果需要，或者在开发中使用)
# pip install -e .

# 安装其他项目依赖 (例如 FastAPI, Uvicorn)
pip install fastapi uvicorn[standard] pydantic[email]

# 安装 vnpy_tiger 的依赖 (主要是 tigeropen)
# 确保 tigeropen 已安装
pip install tigeropen
# 如果 vnpy_tiger 有 requirements.txt, 也可以安装它:
# pip install -r vendors/vnpy_tiger/requirements.txt

# 安装可能需要的额外依赖 (例如 TA-Lib)
# conda install -c conda-forge ta-lib # (示例，根据需要安装)

# 安装数据库相关依赖
pip install sqlalchemy pymysql
```

### 4. 设置数据库

#### MySQL 数据库设置

```bash
# 确保已安装 MySQL 并启动服务

# 运行数据库初始化脚本
bash scripts/setup_mysql.sh

# 或者手动创建数据库并初始化
# 1. 创建数据库
mysql -uroot -pCz159csa -e "CREATE DATABASE IF NOT EXISTS simpletrade DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. 初始化数据库表和示例数据
python scripts/init_database.py
```

数据库配置参数可以在 `simpletrade/config/settings.py` 文件中修改，或者通过环境变量设置。

#### 环境变量配置

项目提供了一个环境变量配置示例文件 `.env.example`，可以复制为 `.env` 并根据需要修改：

```bash
# 复制环境变量配置示例文件
cp .env.example .env

# 编辑环境变量配置文件
vim .env  # 或使用其他编辑器
```

#### 数据库配置参数

- `SIMPLETRADE_DB_USER`: 数据库用户名（默认："root"）
- `SIMPLETRADE_DB_PASSWORD`: 数据库密码（默认："Cz159csa"）
- `SIMPLETRADE_DB_HOST`: 数据库主机（默认："localhost"）
- `SIMPLETRADE_DB_PORT`: 数据库端口（默认："3306"）
- `SIMPLETRADE_DB_NAME`: 数据库名称（默认："simpletrade"）
- `SIMPLETRADE_DB_POOL_SIZE`: 连接池大小（默认：5）
- `SIMPLETRADE_DB_MAX_OVERFLOW`: 最大溢出连接数（默认：10）
- `SIMPLETRADE_DB_POOL_RECYCLE`: 连接回收时间（默认：3600秒）
- `SIMPLETRADE_DB_ECHO`: 是否显示SQL语句（默认：False）

#### API配置参数

- `SIMPLETRADE_API_HOST`: API服务器主机（默认："0.0.0.0"）
- `SIMPLETRADE_API_PORT`: API服务器端口（默认：8003）
- `SIMPLETRADE_API_DEBUG`: 是否启用调试模式（默认：True）

### 5. 运行示例

```bash
# 运行数据管理示例
python examples/data_management_example.py

# 运行API服务示例
python examples/api_example.py
```

### 6. 运行测试

```bash
# 安装pytest
pip install pytest

# 运行单元测试
pytest tests/unit

# 运行集成测试
pytest tests/integration
```

## 运行项目

确保您已按照"安装与配置"部分设置好环境。SimpleTrade 提供两种运行方式：使用 Docker 运行和本地开发模式运行。

### 方式一：使用 Docker 运行（推荐）

使用 Docker 运行是最简单的方式，可以一键启动所有服务，包括 MySQL 数据库、API 服务和前端服务。

#### 1. 启动所有服务

```bash
# 确保已安装 Docker 和 Docker Compose

# 运行启动脚本
./start_docker.sh
```

这个脚本会：
- 检查并创建 `.env` 文件（如果不存在）
- 构建并启动所有 Docker 容器
- 初始化 MySQL 数据库并添加示例数据

启动后，可以访问：
- API 文档：`http://localhost:8003/docs`
- 前端页面：`http://localhost:8080`
- MySQL 数据库：`localhost:3306`（用户名：root，密码：Cz159csa）

#### 2. 查看服务日志

```bash
# 查看所有服务的日志
docker-compose logs

# 查看特定服务的日志
docker-compose logs mysql  # MySQL 数据库日志
docker-compose logs api    # API 服务日志
docker-compose logs frontend  # 前端服务日志
```

#### 3. 停止服务

```bash
# 停止所有服务
docker-compose down
```

#### 4. 重置数据库

如果需要重置数据库，可以删除数据库卷：

```bash
# 停止所有服务
docker-compose down

# 删除数据库卷
docker volume rm simpletrade_mysql-data

# 重新启动服务
./start_docker.sh
```

更多关于 Docker 的信息，请参考 [Docker 开发指南](docs/docker_development_guide.md) 和 [MySQL 与 Docker 集成指南](docs/mysql_docker_guide.md)。

### 方式二：本地开发模式

如果您希望在本地进行开发，可以分别启动后端和前端服务。

#### 1. 启动后端 API 服务

在项目根目录下的**系统终端**中执行以下命令：

```bash
# 激活 Conda 环境
conda activate simpletrade

# 启动 Uvicorn 服务器 (监听 0.0.0.0:8003，带自动重载)
# 注意：必须在激活的 simpletrade 环境中运行
python -m uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8003 --reload
```

后端服务启动后，可以通过 `http://localhost:8003/docs` 访问 API 文档。

#### 2. 启动前端开发服务器

在项目根目录下的**另一个系统终端**中执行以下命令：

```bash
# 激活 Conda 环境 (如果需要 Node/npm，确保它们在此环境或系统路径中)
conda activate simpletrade

# 进入前端目录
cd web-frontend

# 安装依赖 (如果尚未安装)
npm install --legacy-peer-deps

# 启动开发服务器 (通常监听 localhost:8080 或类似端口)
npm run serve
```

前端服务启动后，可以通过 `http://localhost:8080` 访问前端页面。

**重要提示**:
- 两个服务都需要保持运行状态。
- 所有后端相关的操作（包括启动 uvicorn）**必须**在激活的 `simpletrade` Conda 环境中进行。
- 确保 MySQL 数据库已经启动并初始化。

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
- [Docker 开发指南](docs/docker_development_guide.md)
- [MySQL 与 Docker 集成指南](docs/mysql_docker_guide.md)

## 许可证

[待定]
