# Docker 开发环境设置与使用指南

本文档提供了在 macOS 上使用 Docker 设置和使用 SimpleTrade 开发环境的完整指南，包括安装、配置和日常开发工作流程。

## 目录

1. [安装 Docker 环境](#1-安装-docker-环境)
   - [使用 Colima 安装轻量级 Docker 环境](#使用-colima-安装轻量级-docker-环境)
   - [验证安装](#验证安装)
   - [常用 Colima 命令](#常用-colima-命令)
2. [项目 Docker 文件说明](#2-项目-docker-文件说明)
   - [Dockerfile](#dockerfile)
   - [docker-compose.yml](#docker-composeyml)
   - [start_docker.sh](#start_dockersh)
3. [构建和启动开发环境](#3-构建和启动开发环境)
   - [启动步骤](#启动步骤)
   - [验证开发环境](#验证开发环境)
4. [开发工作流](#4-开发工作流)
   - [编辑代码](#编辑代码)
   - [查看日志](#查看日志)
   - [停止开发环境](#停止开发环境)
5. [常见问题解决](#5-常见问题解决)
6. [跨平台开发注意事项](#6-跨平台开发注意事项)
   - [在 M4 Mac 和 Intel Mac 之间切换](#在-m4-mac-和-intel-mac-之间切换)
   - [性能考虑](#性能考虑)
   - [数据持久化](#数据持久化)
7. [Docker 常用命令参考](#7-docker-常用命令参考)

## 部署验证任务进度（2024-04-15）

- [x] 阅读并理解本指南，梳理部署流程
- [x] 验证 Colima 虚拟机和 Docker 环境可用性
- [x] 验证 hello-world 容器运行，确认 Docker 基础功能正常
- [x] 按文档流程构建并启动 SimpleTrade 项目容器
- [x] 解决 TA-Lib 源码编译在 ARM 架构下的兼容性问题，改为 conda 安装
- [x] 解决依赖安装时的网络/DNS 问题，配置清华镜像并彻底移除官方源
- [x] 逐步补全 Python 依赖（requests、python-multipart、python-jose 等）
- [x] 容器服务最终启动成功，API 服务可用
- [x] 日志无关键报错，仅有无关紧要的警告

## 1. 安装 Docker 环境

### 使用 Colima 安装轻量级 Docker 环境

本项目使用 Colima 作为轻量级的容器运行时，用于在 macOS 上创建 Linux 虚拟机以运行 Docker 守护进程。这种方式避免了 Docker Desktop 的图形界面及其相关资源消耗。

#### 前提条件

- 已安装 Homebrew 包管理器。如果未安装，请先通过官网指令安装。

#### 安装步骤

1. **安装 Colima, Docker CLI, 和 Docker Compose:**

   打开终端 (Terminal)，执行以下 Homebrew 命令：
   ```bash
   brew install colima docker docker-compose
   ```

   - `colima`: 安装 Colima 核心程序。
   - `docker`: 安装 Docker 命令行客户端 (CLI)。**注意:** 这仅是客户端，Docker 引擎将在 Colima 管理的虚拟机中运行。
   - `docker-compose`: 安装 Docker Compose 工具。

2. **初始化并启动 Colima 虚拟机:**

   执行以下命令启动 Colima，并为其分配资源。该命令针对 Apple Silicon (aarch64) 架构进行了优化，并指定了内存和 CPU 核心数：
   ```bash
   colima start --arch aarch64 --memory 4 --cpu 2
   ```

   - `--arch aarch64`: 明确指定为 ARM64 架构，适用于 M 系列芯片。
   - `--memory 4`: 分配 4GB 内存给 Colima 虚拟机。
   - `--cpu 2`: 分配 2 个 CPU 核心给 Colima 虚拟机。
   - **注意:** 首次启动会下载所需的 Linux 基础镜像，可能需要一些时间。日志中会显示启动过程，包括创建虚拟机、配置网络、启动 Docker 服务等。

### 验证安装

在 Colima 启动成功后，执行以下命令验证 Docker 是否正确安装：

```bash
# 检查 Docker 守护进程连接
docker ps
```
预期输出：显示容器列表的表头（通常为空，因为还没有运行容器），并且命令不报错。

```bash
# 运行测试容器
docker run hello-world
```
预期输出：
- 如果本地没有镜像，会先显示从 Docker Hub 拉取 (Pull) 镜像的过程。
- 最后显示 "Hello from Docker!" 开头的欢迎信息，表明 Docker 客户端与守护进程通信正常，并且能够成功运行容器。

```bash
# 检查已下载的镜像
docker images
```
预期输出：列表中应包含 `hello-world` 镜像。

### 常用 Colima 命令

- 启动默认虚拟机: `colima start`
- 停止默认虚拟机: `colima stop`
- 查看虚拟机状态: `colima status`
- 删除虚拟机 (慎用): `colima delete`
- SSH 进入虚拟机: `colima ssh`
- 查看日志: `colima logs`

## 2. 项目 Docker 文件说明

SimpleTrade 项目包含以下 Docker 相关文件：

### Dockerfile

`Dockerfile` 定义了项目的开发环境，包括：

- 基础镜像：`python:3.9-slim`
- 国内镜像配置：使用清华、中科大和阿里云的镜像加速下载
- 系统依赖：build-essential, gcc, git 等
- TA-Lib 库的源码安装
- Python 工具和库的安装
- vnpy 及其相关模块的安装
- 项目依赖的安装

注意：我们使用了国内镜像来加速下载和安装，包括：

1. **apt镜像**：使用阿里云镜像加速系统包安装，完全替换所有源配置
2. **TA-Lib下载**：使用Gitee和多个SourceForge镜像加速下载
3. **pip镜像**：使用清华镜像加速 Python 包安装

文件内容：

```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 使用国内apt镜像
# 完全替换所有源为国内镜像
RUN echo "Configuring apt mirrors..." && \
    # 备份原始源配置
    if [ -f /etc/apt/sources.list ]; then \
        cp /etc/apt/sources.list /etc/apt/sources.list.bak; \
    fi && \
    # 清空所有源配置
    echo "" > /etc/apt/sources.list && \
    # 移除所有其他源配置
    rm -f /etc/apt/sources.list.d/*.list && \
    # 创建阿里云镜像源配置（速度更快）
    echo "deb https://mirrors.aliyun.com/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
    # 更新软件包列表
    apt-get clean && \
    apt-get update -y

# 安装系统依赖
RUN apt-get update && \
    echo "Installing system dependencies..." && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    libssl-dev \
    pkg-config \
    wget \
    curl \
    netcat-openbsd \
    vim \
    nano \
    htop \
    procps \
    iputils-ping \
    net-tools \
    telnet \
    dnsutils \
    lsof \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装TA-Lib
# 使用国内镜像下载TA-Lib
RUN cd /tmp && \
    echo "Downloading TA-Lib..." && \
    wget -q -O ta-lib-0.4.0-src.tar.gz https://gitee.com/mirrors/ta-lib/raw/master/ta-lib-0.4.0-src.tar.gz || \
    wget -q -O ta-lib-0.4.0-src.tar.gz https://jztkft.dl.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz || \
    wget -q -O ta-lib-0.4.0-src.tar.gz https://versaweb.dl.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz || \
    wget -q -O ta-lib-0.4.0-src.tar.gz http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    echo "Extracting TA-Lib..." && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    echo "Configuring TA-Lib..." && \
    ./configure --prefix=/usr && \
    echo "Building TA-Lib..." && \
    make && \
    echo "Installing TA-Lib..." && \
    make install && \
    cd /tmp && \
    rm -rf ta-lib-0.4.0-src.tar.gz ta-lib/

# 配置PIP国内镜像
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 安装常用Python工具
RUN pip install --no-cache-dir \
    ipython \
    jupyter \
    notebook \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scikit-learn \
    statsmodels \
    pytest \
    black \
    flake8 \
    isort \
    mypy \
    pylint

# 安装vnpy核心
RUN pip install --no-cache-dir \
    vnpy \
    vnpy_cta_strategy \
    vnpy_ctastrategy \
    vnpy_datamanager \
    vnpy_sqlite \
    vnpy_rest \
    vnpy_websocket \
    vnpy_csv \
    vnpy_mysql \
    vnpy_ctp \
    vnpy_ib \
    vnpy_tushare \
    vnpy_rqdata \
    vnpy_jotdx

# 复制启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 暴露端口
EXPOSE 8003

# 启动命令
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["conda", "run", "--no-capture-output", "-n", "simpletrade", "python", "-m", "uvicorn", "simpletrade.api.server:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
```

### docker-compose.yml

`docker-compose.yml` 定义了项目的服务配置，包括：

- 服务名称：api、mysql、frontend 和 jupyter
- 端口映射：8003:8003、3306:3306、8080:8080 和 8888:8888
- 卷挂载：将本地目录挂载到容器中，并使用数据卷持久化存储
- 环境变量：数据库连接参数等
- 启动命令
- 自动重启配置

文件内容：

```yaml
version: '3'

services:
  mysql:
    image: mysql:8.0
    container_name: simpletrade-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${SIMPLETRADE_DB_PASSWORD:-Cz159csa}
      MYSQL_DATABASE: ${SIMPLETRADE_DB_NAME:-simpletrade}
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
      - ./mysql-init:/docker-entrypoint-initdb.d
    networks:
      - simpletrade-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "${SIMPLETRADE_DB_USER:-root}", "-p${SIMPLETRADE_DB_PASSWORD:-Cz159csa}"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  api:
    build: .
    container_name: simpletrade-api
    depends_on:
      mysql:
        condition: service_healthy
    ports:
      - "8003:8003"
    volumes:
      - .:/app
      - data-volume:/app/data
      - logs-volume:/app/logs
      - configs-volume:/app/configs
    environment:
      - PYTHONPATH=/app
      - SIMPLETRADE_DB_HOST=mysql
      - SIMPLETRADE_DB_PORT=3306
      - SIMPLETRADE_DB_USER=${SIMPLETRADE_DB_USER:-root}
      - SIMPLETRADE_DB_PASSWORD=${SIMPLETRADE_DB_PASSWORD:-Cz159csa}
      - SIMPLETRADE_DB_NAME=${SIMPLETRADE_DB_NAME:-simpletrade}
      - SIMPLETRADE_API_PORT=8003
    networks:
      - simpletrade-network
    restart: unless-stopped

  frontend:
    image: node:16
    container_name: simpletrade-frontend
    working_dir: /app
    volumes:
      - ./web-frontend:/app
    ports:
      - "8080:8080"
    command: bash -c "npm install --legacy-peer-deps && npm run serve"
    depends_on:
      - api
    networks:
      - simpletrade-network
    restart: unless-stopped

  jupyter:
    build: .
    container_name: simpletrade-jupyter
    command: /app/docker_scripts/start_jupyter.sh
    ports:
      - "8888:8888"
    volumes:
      - .:/app
      - data-volume:/app/data
      - notebooks-volume:/app/notebooks
    environment:
      - PYTHONPATH=/app
      - SIMPLETRADE_DB_HOST=mysql
      - SIMPLETRADE_DB_PORT=3306
      - SIMPLETRADE_DB_USER=${SIMPLETRADE_DB_USER:-root}
      - SIMPLETRADE_DB_PASSWORD=${SIMPLETRADE_DB_PASSWORD:-Cz159csa}
      - SIMPLETRADE_DB_NAME=${SIMPLETRADE_DB_NAME:-simpletrade}
    networks:
      - simpletrade-network
    depends_on:
      - mysql
    restart: unless-stopped

networks:
  simpletrade-network:

volumes:
  mysql-data:
  data-volume:
  logs-volume:
  configs-volume:
  notebooks-volume:
```

### docker-entrypoint.sh

`docker-entrypoint.sh` 是容器的启动脚本，用于等待 MySQL 服务启动并初始化数据库：

```bash
#!/bin/bash

# 等待 MySQL 服务启动
echo "Waiting for MySQL to start..."
while ! nc -z $SIMPLETRADE_DB_HOST $SIMPLETRADE_DB_PORT; do
  sleep 1
done
echo "MySQL started"

# 初始化数据库
echo "Initializing database..."
conda run -n simpletrade python scripts/init_database.py

# 启动应用
echo "Starting application..."
exec "$@"
```

### .env.example

`.env.example` 是环境变量配置示例文件，用于配置数据库连接参数等：

```
# SimpleTrade 环境变量配置示例
# 复制此文件为 .env 并根据需要修改

# 数据库配置
SIMPLETRADE_DB_USER=root
SIMPLETRADE_DB_PASSWORD=Cz159csa
SIMPLETRADE_DB_HOST=mysql
SIMPLETRADE_DB_PORT=3306
SIMPLETRADE_DB_NAME=simpletrade
SIMPLETRADE_DB_POOL_SIZE=5
SIMPLETRADE_DB_MAX_OVERFLOW=10
SIMPLETRADE_DB_POOL_RECYCLE=3600
SIMPLETRADE_DB_ECHO=False

# API 配置
SIMPLETRADE_API_HOST=0.0.0.0
SIMPLETRADE_API_PORT=8003
SIMPLETRADE_API_DEBUG=True

# 日志配置
SIMPLETRADE_LOG_LEVEL=INFO
```

## 项目结构

SimpleTrade 项目的目录结构如下：

```
.
├── Dockerfile              # Docker 构建文件
├── README.md               # 项目说明
├── docker-compose.yml      # Docker 组合配置
├── docker-entrypoint.sh    # Docker 容器启动脚本
├── docker_scripts/         # Docker 容器内部脚本
│   ├── start_jupyter.sh    # 启动 Jupyter Notebook 服务
│   ├── check_system.sh     # 检查系统状态
│   ├── backup_data.sh      # 备份数据
│   └── run_backtest.sh     # 运行回测
├── docs/                   # 文档目录
├── mysql-init/             # MySQL 初始化脚本
├── notebooks/              # Jupyter 笔记本目录
│   ├── README.md           # Jupyter 使用指南
│   └── 数据分析示例.ipynb  # 示例笔记本
├── requirements.txt        # Python 依赖列表
├── simpletrade/            # 项目主代码
│   ├── __init__.py
│   ├── api/               # API 模块
│   ├── config/            # 配置模块
│   ├── core/              # 核心模块
│   │   └── analysis/       # 分析模块
│   │       └── visualization.py  # 数据可视化
│   ├── models/            # 数据模型
│   ├── services/          # 服务模块
│   │   ├── strategy_service.py  # 策略服务
│   │   ├── backtest_service.py  # 回测服务
│   │   └── monitor_service.py   # 监控服务
│   ├── strategies/        # 策略模块
│   │   └── moving_average_strategy.py  # 移动平均线策略
│   └── utils/             # 工具模块
├── start_docker.sh         # Docker 启动脚本
├── tests/                  # 测试目录
└── web-frontend/           # 前端代码
```

### docker_scripts 目录

`docker_scripts` 目录包含了一系列用于 Docker 容器内部的脚本，包括：

#### start_jupyter.sh

`start_jupyter.sh` 用于启动 Jupyter Notebook 服务：

```bash
#!/bin/bash

# 启动Jupyter Notebook服务
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
```

#### check_system.sh

`check_system.sh` 用于检查系统状态：

```bash
#!/bin/bash

# 检查系统状态
echo "=== 系统信息 ==="
uname -a
echo

echo "=== CPU信息 ==="
cat /proc/cpuinfo | grep "model name" | head -1
echo "CPU核心数: $(nproc)"
echo

echo "=== 内存信息 ==="
free -h
echo

echo "=== 磁盘信息 ==="
df -h
echo

echo "=== Python信息 ==="
python --version
pip --version
echo

echo "=== vnpy信息 ==="
python -c "import vnpy; print(f'vnpy版本: {vnpy.__version__}')"
echo

echo "=== 网络信息 ==="
ip addr | grep inet
echo

echo "=== 进程信息 ==="
ps aux | grep -E 'python|vnpy' | grep -v grep
echo

echo "=== 系统检查完成 ==="
```

#### backup_data.sh

`backup_data.sh` 用于备份数据：

```bash
#!/bin/bash

# 备份数据
BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 备份数据
echo "开始备份数据..."
tar -czf ${BACKUP_FILE} /app/data /app/configs /app/logs

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "备份成功: ${BACKUP_FILE}"
    echo "备份大小: $(du -h ${BACKUP_FILE} | cut -f1)"
else
    echo "备份失败!"
    exit 1
fi

# 清理旧备份（保留最近10个）
echo "清理旧备份..."
ls -t ${BACKUP_DIR}/backup_*.tar.gz | tail -n +11 | xargs -r rm

echo "备份完成!"
```

#### run_backtest.sh

`run_backtest.sh` 用于运行回测：

```bash
#!/bin/bash

# 运行回测脚本
# 用法: ./run_backtest.sh <策略名称> <开始日期> <结束日期> <交易品种> <交易所>

# 检查参数
if [ $# -lt 5 ]; then
    echo "用法: $0 <策略名称> <开始日期> <结束日期> <交易品种> <交易所>"
    echo "示例: $0 MovingAverageStrategy 20200101 20201231 BTCUSDT BINANCE"
    exit 1
fi

STRATEGY=$1
START_DATE=$2
END_DATE=$3
SYMBOL=$4
EXCHANGE=$5

echo "开始回测..."
echo "策略: $STRATEGY"
echo "时间范围: $START_DATE - $END_DATE"
echo "交易品种: $SYMBOL"
echo "交易所: $EXCHANGE"

# 运行回测
python -m simpletrade.backtest.run_backtest \
    --strategy $STRATEGY \
    --start_date $START_DATE \
    --end_date $END_DATE \
    --symbol $SYMBOL \
    --exchange $EXCHANGE

echo "回测完成!"
```

### start_docker.sh

`start_docker.sh` 是一个简单的启动脚本，用于启动 Docker 容器：

```bash
#!/bin/bash

# 确保脚本在项目根目录运行
cd "$(dirname "$0")"

# 如果 .env 文件不存在，复制 .env.example
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example"
  cp .env.example .env
fi

# 给脚本添加执行权限
chmod +x start_docker.sh

# 启动 Docker 容器
./start_docker.sh
```

## 3. 构建和启动开发环境

### 启动步骤

1. **确保 Colima 正在运行**

   在启动开发环境之前，确保 Colima 虚拟机已经启动。您可以使用以下命令检查 Colima 状态：

   ```bash
   colima status
   ```

   如果 Colima 未启动，请使用以下命令启动它：

   ```bash
   colima start
   ```

2. **打开终端**

   打开终端应用程序。

3. **导航到项目目录**

   ```bash
   cd /path/to/simpletrade
   ```

   或者使用您的项目实际路径。

4. **配置环境变量**

   复制环境变量配置示例文件，并根据需要修改：

   ```bash
   cp .env.example .env
   ```

   编辑 `.env` 文件，根据您的需要修改数据库连接参数、API 配置等。如果您使用默认配置，可以跳过这一步。

   > **注意：** 如果您使用 `start_docker.sh` 脚本启动，它会自动检查 `.env` 文件是否存在，如果不存在，会自动复制 `.env.example`。

5. **启动开发环境**

   有两种方式启动开发环境：

   **方式 1: 使用启动脚本（推荐）**

   ```bash
   # 给脚本添加执行权限
   chmod +x start_docker.sh

   # 运行启动脚本
   ./start_docker.sh
   ```

   这种方式会自动检查 `.env` 文件，并启动所有必要的服务，包括 MySQL 数据库、API 服务和前端服务。

   **方式 2: 直接使用 docker-compose 命令**

   ```bash
   docker-compose up --build
   ```

   第一次构建可能需要 10-15 分钟，因为它需要下载基础镜像、安装依赖等。后续启动会更快。

6. **等待服务启动**

   启动过程中，您将看到以下步骤：

   - MySQL 数据库服务启动
   - API 服务等待 MySQL 启动完成
   - 数据库初始化（创建表和添加示例数据）
   - API 服务启动
   - 前端服务启动

   整个过程是自动的，您只需要等待所有服务启动完成。

### 验证开发环境

构建完成并启动容器后，您应该能看到类似以下的输出：

```
mysql_1     | [Note] [Entrypoint]: MySQL init process done. Ready for start up.
mysql_1     | [Note] [Entrypoint]: Starting MySQL 8.0.x
...
api_1       | Waiting for MySQL to start...
api_1       | MySQL started
api_1       | Initializing database...
api_1       | 开始初始化数据库...
api_1       | 数据库 simpletrade 创建成功或已存在
api_1       | 数据库表创建成功
api_1       | 示例数据添加成功
api_1       | 数据库初始化完成
api_1       | Starting application...
api_1       | INFO:     Will watch for changes in these directories: ['/app']
api_1       | INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
api_1       | INFO:     Started reloader process [1] using WatchFiles
api_1       | Test API routes added successfully.
api_1       | Health check API route added.
api_1       | Analysis API routes added.
api_1       | Strategies API routes added.
...
frontend_1  | App running at:
frontend_1  | - Local:   http://localhost:8080/
```

现在，您可以进行以下验证：

1. **验证 API 服务**

   在浏览器中访问 `http://localhost:8003/docs` 查看 API 文档。

2. **验证前端服务**

   在浏览器中访问 `http://localhost:8080` 查看前端页面。

3. **验证数据库连接**

   您可以使用以下命令进入 MySQL 容器并验证数据库：

   ```bash
   # 进入 MySQL 容器
   docker exec -it simpletrade-mysql bash

   # 连接到 MySQL
   mysql -uroot -pCz159csa simpletrade

   # 查看数据库表
   SHOW TABLES;

   # 查询交易品种表
   SELECT * FROM symbols;

   # 查询策略表
   SELECT * FROM strategies;
   ```

4. **验证 API 端点**

   您可以使用 curl 命令测试 API 端点：

   ```bash
   # 测试健康检查端点
   curl -s http://localhost:8003/api/health/

   # 测试交易品种端点
   curl -s http://localhost:8003/api/data/symbols

   # 测试策略端点
   curl -s http://localhost:8003/api/strategies/
   ```

5. **验证 Jupyter Notebook**

   在浏览器中访问 `http://localhost:8888` 查看 Jupyter Notebook 界面。您可以创建新的笔记本或打开现有的笔记本。

   Jupyter Notebook 是一个交互式的开发环境，可用于数据分析、策略开发和回测结果分析。它允许您编写和执行代码，可视化数据，并以文档形式保存分析过程。

   在 `notebooks` 目录中提供了一些示例笔记本，包括数据分析示例、策略开发示例等。

### 关于首次构建时间

首次构建 Docker 镜像可能需要相当长的时间，特别是编译 TA-Lib 库的步骤。这是正常的，您可能需要等待 25-30 分钟才能完成首次构建。

具体来说，您可能会看到类似以下的输出，显示 TA-Lib 编译正在进行：

```
[+] Building 1602.2s (6/9)
 => [api 4/6] RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz &&     tar -xzf ta-lib-0.4.0-src.tar.gz &&     cd ta-lib/ &&     ./  1545.4s
```

#### 重要说明：跨机器缓存

需要注意的是，Docker 镜像缓存是与每台机器相关的，而不是跨机器共享的。这意味着：

1. **每台机器的首次构建**：在每台新机器上（如从公司的 M4 Mac 切换到家里的 Intel Mac），您都需要经历一次漫长的首次构建过程。

2. **同一台机器的后续启动**：一旦在特定机器上完成首次构建，后续在该机器上的启动将非常快速（通常只需要几秒钟）。

#### 跨机器共享 Docker 镜像的方法

为了避免在每台机器上都经历漫长的构建过程，您可以考虑以下方法：

1. **导出和导入 Docker 镜像**：
   ```bash
   # 在第一台机器上导出镜像
   docker save simpletrade_api > simpletrade_api.tar

   # 将 tar 文件复制到第二台机器
   # 然后在第二台机器上导入
   docker load < simpletrade_api.tar
   ```

2. **使用 Docker Registry**：
   - 设置一个私有的 Docker Registry
   - 将构建好的镜像推送到 Registry
   - 在其他机器上从 Registry 拉取镜像

3. **预构建基础镜像**：
   - 创建一个包含已编译 TA-Lib 的基础镜像
   - 将这个基础镜像发布到 Docker Hub
   - 在 Dockerfile 中使用这个基础镜像

## 4. 开发工作流

使用 Docker 进行开发的工作流程如下：

### 编辑代码

您可以使用您喜欢的编辑器（如 VS Code、PyCharm 等）在主机上编辑代码。由于我们使用了卷挂载，您在主机上对代码的修改会立即反映到容器中。

例如，您可以修改 `simpletrade/api/server.py` 文件中的 `/api/test/hello` 路由：

```python
@router.get("/hello")
async def hello():
    return {"message": "Hello from Docker Development Environment!"}
```

保存文件后，由于我们使用了 `--reload` 参数，服务器会自动重新加载，您可以立即在浏览器中看到更改的效果。

#### 卷挂载工作原理

很多开发者对"由于我们使用了卷挂载，您在主机上对代码的修改会立即反映到容器中"这句话的工作原理感到疑惑。以下是对这个机制的详细解释：

1. **文件系统映射**：当我们在 `docker-compose.yml` 文件中定义卷挂载（如 `.:/app`）时，Docker 创建了一个从主机目录（当前目录 `.`）到容器内目录（`/app`）的实时映射。

2. **实时同步**：这不是一个复制操作，而是一个实时的文件系统映射。容器内的 `/app` 目录实际上是直接访问主机上的目录，就像一个"窗口"，通过这个"窗口"可以看到和操作主机上的文件。

3. **双向访问**：这个映射是双向的，意味着：
   - 容器可以读取主机上的文件
   - 容器可以写入主机上的文件
   - 主机可以读取这些文件
   - 主机可以修改这些文件，修改会立即在容器中可见

4. **代码变化检测**：
   - Docker 本身不会主动监控文件变化
   - 实际上，是在容器内运行的 Uvicorn 服务器（使用 `--reload` 参数）在监控文件变化
   - Uvicorn 会定期检查文件的修改时间或使用操作系统的文件系统事件通知机制来检测文件变化
   - 当检测到文件变化时，Uvicorn 会重新加载 Python 模块，使得代码更改立即生效

5. **跨机器工作的原理**：
   - 在 `docker-compose.yml` 文件中，我们使用的是相对路径 `.:/app`，而不是绝对路径
   - 这意味着无论您在哪台机器上，Docker 都会挂载当前目录（即运行 `docker-compose up` 命令的目录）
   - 只要您在不同机器上保持相同的项目结构，卷挂载就会正常工作

这种机制使得您可以在主机上使用熟悉的编辑器编辑代码，而容器内的应用程序会立即反映这些更改，提供了非常流畅的开发体验。

### 查看日志

Docker 容器的日志会实时显示在终端中。如果您在另一个终端中启动了容器，可以使用以下命令查看日志：

```bash
docker-compose logs -f
```

### 停止开发环境

当您完成开发时，可以按 `Ctrl+C` 停止容器，或者在另一个终端中运行：

```bash
docker-compose down
```

## 5. 常见问题解决

### 问题 1: 端口冲突

如果端口 8002 已被占用，您会看到类似以下的错误：

```
Error response from daemon: Ports are not available: listen tcp 0.0.0.0:8002: bind: address already in use
```

解决方案：修改 `docker-compose.yml` 文件中的端口映射，例如将 `8002:8002` 改为 `8003:8002`，然后重新启动容器。

### 问题 2: 权限问题

如果遇到权限问题，可能会看到类似以下的错误：

```
permission denied while trying to connect to the Docker daemon socket
```

解决方案：确保您的用户属于 docker 组，或者使用 sudo 运行命令：

```bash
sudo docker-compose up --build
```

### 问题 3: 镜像构建失败

如果镜像构建失败，可能会看到各种错误信息。常见的解决方案包括：

1. 检查网络连接
2. 确保 Colima 正在运行
3. 尝试重新构建镜像：

```bash
docker-compose build --no-cache
```

### 问题 4: 卷挂载问题

如果代码更改没有反映到容器中，可能是卷挂载问题。解决方案：

1. 确保 `docker-compose.yml` 文件中的卷挂载配置正确
2. 重新启动容器
3. 检查 Colima 的文件共享设置

## 6. 跨平台开发注意事项

### 在 M4 Mac 和 Intel Mac 之间切换

Docker 的一个主要优势是能够在不同架构的机器上提供一致的开发环境。当您在 M4 Mac 和 Intel Mac 之间切换时，需要注意以下几点：

1. **安装 Colima**：在两台机器上都需要安装 Colima、Docker CLI 和 Docker Compose：
   ```bash
   brew install colima docker docker-compose
   ```

2. **启动 Colima**：在两台机器上都需要启动 Colima，但参数可能不同：
   - 在 M4 Mac 上：
     ```bash
     colima start --arch aarch64 --memory 4 --cpu 2
     ```
   - 在 Intel Mac 上：
     ```bash
     colima start --memory 4 --cpu 2
     ```
     注意在 Intel Mac 上不需要指定 `--arch` 参数。

3. **构建和启动容器**：在两台机器上使用相同的命令：
   ```bash
   docker-compose up --build
   ```

Docker 会自动处理架构差异，因为我们使用的是支持多架构的基础镜像。

### 性能考虑

在 M4 Mac 上，Docker 容器的性能通常很好，因为它使用原生虚拟化。在 Intel Mac 上，性能可能略低，但对于开发目的来说通常足够。

### 数据持久化

当您在不同机器之间切换时，需要注意数据持久化问题。如果您的应用程序在容器内存储数据，这些数据在不同机器之间不会自动同步。您可能需要使用外部存储或手动同步数据。

## 7. Jupyter Notebook 使用指南

Jupyter Notebook 是一个交互式的开发环境，可用于数据分析、策略开发和回测结果分析。在 SimpleTrade 项目中，我们已经集成了 Jupyter Notebook 服务，可以通过浏览器访问。

### 访问 Jupyter Notebook

1. 启动 SimpleTrade 容器后，在浏览器中访问：`http://localhost:8888`
2. 无需密码即可登录（在生产环境中应设置密码）

### Jupyter Notebook 的主要用途

1. **数据分析**：
   - 加载和探索历史行情数据
   - 计算和可视化技术指标
   - 分析交易品种的统计特性
   - 研究市场模式和相关性

2. **策略开发**：
   - 编写和测试交易策略
   - 可视化策略信号和交易结果
   - 优化策略参数
   - 分析策略性能指标

3. **回测结果分析**：
   - 加载和可视化回测结果
   - 分析策略的盈亏分布
   - 计算风险指标
   - 比较不同策略的性能

4. **实时监控**：
   - 连接到实时交易系统
   - 监控策略运行状态
   - 分析实时交易数据
   - 调整策略参数

### 示例笔记本

在 `notebooks` 目录中提供了一些示例笔记本，包括：

1. **数据分析示例.ipynb**：展示如何加载和分析历史数据

这些示例笔记本可以帮助您快速上手使用 Jupyter Notebook 进行数据分析和策略开发。

### 注意事项

1. Jupyter Notebook 服务运行在 Docker 容器中，数据保存在 notebooks 数据卷中
2. 重启容器不会丢失 Notebook 文件，但请定期备份重要的 Notebook
3. 在生产环境中，应设置 Jupyter Notebook 的访问密码
4. 避免在 Notebook 中运行耗时的计算，这可能会影响其他服务的性能

## 8. Docker 常用命令参考

以下是一些常用的 Docker 命令，可以帮助您管理开发环境：

### 构建和启动容器

```bash
# 构建并启动容器
docker-compose up --build

# 在后台启动容器
docker-compose up -d

# 只构建镜像，不启动容器
docker-compose build
```

### 管理容器

```bash
# 停止容器
docker-compose down

# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 查看容器日志
docker-compose logs -f

# 进入容器
docker-compose exec api bash
```

### 管理镜像

```bash
# 查看所有镜像
docker images

# 删除未使用的镜像
docker image prune

# 删除所有未使用的资源
docker system prune
```

### 卷和网络

```bash
# 查看卷
docker volume ls

# 查看网络
docker network ls
```

## 结论

使用 Docker 进行开发可以确保在不同机器上有一致的开发体验，避免"在我的机器上能运行"的问题。通过本指南中的步骤，您可以在 M4 Mac 和 Intel Mac 上设置相同的开发环境，并使用相同的工作流进行开发。

如果您遇到任何问题，请参考"常见问题解决"部分，或者查阅 [Docker 官方文档](https://docs.docker.com/)。
## 4. 常见问题和解决方法

### 问题 1: 前端依赖安装失败

如果您遇到前端依赖安装失败的问题，可能是因为 npm 依赖冲突。错误信息可能如下：

```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE could not resolve
...
npm ERR! Fix the upstream dependency conflict, or retry
npm ERR! this command with --force, or --legacy-peer-deps
```

解决方法：

1. 修改 `docker-compose.yml` 文件中的前端服务配置，添加 `--legacy-peer-deps` 选项：

```yaml
command: bash -c "npm install --legacy-peer-deps && npm run serve"
```

2. 或者手动进入容器安装依赖：

```bash
# 进入前端容器
docker exec -it simpletrade-frontend bash

# 安装依赖
npm install --legacy-peer-deps

# 启动前端服务
npm run serve
```

### 问题 2: API 服务缺少图形库依赖

如果您遇到类似下面的错误：

```
Failed to load global main_engine: libEGL.so.1: cannot open shared object file: No such file or directory
```

解决方法：

在 `Dockerfile` 中添加必要的图形库依赖：

```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    netcat-openbsd \
    libegl1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
```

### 问题 3: 权限问题

如果您遇到权限问题，可能是因为 Docker 容器内的用户与主机用户不同。尝试以下解决方法：

```bash
# 在主机上更改文件权限
chmod -R 777 /path/to/simpletrade
```

### 问题 4: 端口冲突

如果您遇到端口冲突问题，可能是因为端口已被其他应用程序占用。尝试以下解决方法：

```bash
# 查找占用端口的进程
lsof -i :8003

# 终止进程
kill -9 <PID>
```

或者修改 `docker-compose.yml` 文件中的端口映射：

```yaml
ports:
  - "8004:8003"  # 将主机端口从 8003 改为 8004
```

### 问题 5: 数据库初始化问题

如果您需要重置数据库并重新初始化，可以尝试以下方法：

```bash
# 停止容器
docker-compose down

# 删除卷
docker volume rm simpletrade_mysql-data

# 重新启动容器
docker-compose up
```

## 结论

使用 Docker 进行开发可以确保在不同机器上有一致的开发体验，避免"在我的机器上能运行"的问题。通过本指南中的步骤，您可以在 M4 Mac 和 Intel Mac 上设置相同的开发环境，并使用相同的工作流进行开发。

如果您遇到任何问题，请参考"常见问题和解决方法"部分，或者查阅 [Docker 官方文档](https://docs.docker.com/)。
