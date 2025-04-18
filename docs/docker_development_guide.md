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

### 启动脚本

项目提供了多个启动脚本，适用于不同的架构和基础镜像：

#### start_docker.sh

`start_docker.sh` 是原始的启动脚本，使用默认的 Dockerfile 和 docker-compose.yml：

```bash
#!/bin/bash

# 确保脚本在项目根目录运行
cd "$(dirname "$0")"

# 如果 .env 文件不存在，复制 .env.example
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example"
  cp .env.example .env
fi

# 启动 Docker 容器
docker-compose up --build
```

#### start_docker_arm64.sh

`start_docker_arm64.sh` 是为 ARM64 架构（如 Apple Silicon Mac）优化的启动脚本，使用 Dockerfile.arm64 和 docker-compose.arm64.yml：

```bash
#!/bin/bash

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
  echo -e "${BLUE}[SimpleTrade]${NC} $1"
}

# 检查是否需要强制重新构建
if [ "$1" = "--rebuild" ]; then
  REBUILD="--no-cache"
  print_message "强制重新构建所有镜像..."
else
  REBUILD=""
  print_message "使用缓存构建镜像（如需强制重新构建，请使用 --rebuild 选项）..."
fi

# 构建并启动API服务
print_message "构建并启动API服务..."
docker-compose -f docker-compose.arm64.yml build $REBUILD api
```

这个脚本有以下特点：

1. **支持缓存控制**：通过 `--rebuild` 选项可以选择是否使用缓存
2. **错误处理**：如果构建失败，会尝试使用现有镜像启动
3. **状态检查**：启动后会检查各个服务的运行状态

#### start_docker_debian11.sh 和 start_docker_ubuntu.sh

这两个脚本分别使用 Debian 11 和 Ubuntu 20.04 作为基础镜像，结构与 `start_docker_arm64.sh` 类似。

### 如何选择正确的启动脚本

根据您的系统架构和偏好选择适合的启动脚本：

1. **Apple Silicon Mac (M1/M2/M3/M4)**：**必须**使用 `./start_docker_arm64.sh`。这个脚本是为了确保使用 ARM64 兼容的配置 (`docker-compose.arm64.yml` 和 `Dockerfile.arm64`)。**切勿**直接运行 `docker-compose up` 或使用非 arm64 的脚本，否则可能导致运行时错误、性能问题或构建失败。
2. **Intel Mac 或其他 x86_64 系统**：可以使用 `./start_docker_debian11.sh` 或 `./start_docker_ubuntu.sh`。
3. **如果遇到问题**：尝试使用 `--rebuild` 选项强制重新构建（例如 `./start_docker_arm64.sh --rebuild`）。

## 3. 构建和启动开发环境

### 启动步骤

1.  **确保 Docker 环境运行:** 确保 Colima (或其他 Docker 环境) 已经启动。

2.  **导航到项目根目录:** 在终端中，`cd` 到 SimpleTrade 项目的根目录。

3.  **执行启动脚本 (推荐):**
    *   对于 **ARM64 (M系列芯片)**: 运行 `./start_docker_arm64.sh`
    *   对于 **Intel (x86_64)**: 运行 `./start_docker_intel.sh`

    该脚本会自动处理环境检查、构建必要的 Docker 镜像、启动所有必需的服务（MySQL, API, 前端, Jupyter）。首次运行或代码有重大更改时，构建过程可能需要一些时间。后续启动会利用缓存，速度更快。

4.  **直接使用 Docker Compose (可选):**
    如果您只想启动部分服务或更精细地控制，可以直接使用 `docker-compose` 命令：

    *   **启动所有服务:**
      ```bash
      # ARM64
      docker-compose -f docker-compose.arm64.yml up
      # Intel
      docker-compose -f docker-compose.yml up
      ```
    *   **仅启动 API 和 数据库:**
      ```bash
      # ARM64
      docker-compose -f docker-compose.arm64.yml up api
      # Intel (假设依赖正确设置)
      docker-compose -f docker-compose.yml up api
      ```
    *   **在后台运行:** 在 `up` 命令后添加 `-d` 参数，例如 `docker-compose -f docker-compose.arm64.yml up -d`。

5.  **等待服务就绪:** 脚本或 `docker-compose up` 命令会显示各个服务的启动日志。等待所有服务启动完成，特别是 MySQL 和 API 服务。

### 验证开发环境

启动成功后，您可以通过以下方式验证：

- **API 服务:** 访问 `http://localhost:8003` 或 API 文档 `http://localhost:8003/docs`。
- **前端界面:** 访问 `http://localhost:8080`。
- **Jupyter Notebook:** 访问 `http://localhost:8888`。
- **检查容器状态:** 运行 `docker ps` 或 `docker-compose -f <your_compose_file>.yml ps` 查看正在运行的容器。

## 4. 开发工作流

### 编辑代码

- **直接编辑:** 由于项目目录通过 Docker 卷挂载到了容器内部的 `/app` 目录，您可以直接在本地 IDE（如 PyCharm, VS Code）中编辑项目文件。
- **后端热重载:** API 服务 (`simpletrade-api`) 配置了 Uvicorn 的 `--reload` 模式。当您修改并保存后端 Python 代码 (`.py` 文件) 时，API 服务会自动重启加载更改，无需手动重启容器。您可以在 API 服务的日志中看到重载信息。
- **前端热重载:** 前端开发服务器 (`simpletrade-frontend`) 也通常配置了热重载。修改前端代码 (`.vue`, `.js`, `.css` 等) 会自动更新浏览器中的页面或需要手动刷新。

### 连接到容器内数据库 (MySQL)

您可以使用 IDE（如 PyCharm）或独立的数据库客户端连接到运行在 Docker 容器内的 MySQL 数据库进行查看和调试。

**连接参数:**

- **主机 (Host):** `localhost` 或 `127.0.0.1`
- **端口 (Port):** `3307` (注意：我们已将宿主机端口从默认的 3306 修改为 3307，以避免与本机可能运行的 MySQL 冲突)
- **用户名 (User):** `root` (或在 `.env` 文件中配置的值)
- **密码 (Password):** `Cz159csa` (或在 `.env` 文件中配置的值)
- **数据库 (Database):** `simpletrade` (或在 `.env` 文件中配置的值)

**在 PyCharm 中设置:**

1.  打开 **Database** 工具窗口 (`View -> Tool Windows -> Database`)。
2.  点击 **+** -> **Data Source** -> **MySQL**。
3.  在配置窗口中填写上述 **连接参数**。
4.  如果提示下载驱动，请点击 **Download missing driver files**。
5.  点击 **Test Connection** 验证连接是否成功。
6.  点击 **OK** 或 **Apply** 保存。
7.  现在您可以在 Database 工具窗口中浏览 `simpletrade` 数据库的表结构和数据了。

### 进入容器内部 (Shell)

有时您可能需要进入容器内部执行命令、检查文件或进行调试。

使用 `docker exec` 命令：

```bash
docker exec -it <container_name_or_id> bash
```

- `-i`: 保持标准输入打开 (interactive)。
- `-t`: 分配一个伪终端 (pseudo-TTY)。
- `<container_name_or_id>`: 要进入的容器的名称或 ID。您可以通过 `docker ps` 查看。
- `bash`: 在容器内启动 `bash` shell。

**常用容器名称:**

- **API 服务:** `simpletrade-api`
- **前端服务:** `simpletrade-frontend`
- **MySQL 服务:** `simpletrade-mysql`
- **Jupyter 服务:** `simpletrade-jupyter`

**示例：进入 API 服务容器:**

```bash
docker exec -it simpletrade-api bash
```

进入后，您就像在容器的 Linux 环境中一样，可以执行 `ls`, `cd`, `pip list`, `python` 等命令。
输入 `exit` 或按 `Ctrl+D` 可以退出容器 shell。

### 查看日志

查看运行中服务的日志对于调试至关重要。

**使用 Docker Compose 查看 (推荐):**

此方法按服务名称查看，更方便。

```bash
docker-compose -f <your_compose_file>.yml logs <service_name>
```

- `<your_compose_file>.yml`: 指向您使用的 compose 文件 (`docker-compose.arm64.yml` 或 `docker-compose.yml`)。
- `<service_name>`: 要查看日志的服务名称 (例如: `api`, `frontend`, `mysql`, `jupyter`)。

**常用选项:**

- `-f` 或 `--follow`: 持续跟踪日志输出 (按 `Ctrl+C` 停止)。
- `-t` 或 `--timestamps`: 显示时间戳。
- `--tail <number>`: 只显示最后 N 行日志 (例如 `--tail 100`)。

**示例：持续跟踪 API 服务日志并显示时间戳:**

```bash
docker-compose -f docker-compose.arm64.yml logs -ft api
```

**使用 Docker CLI 查看 (按容器名称):**

```bash
docker logs <container_name_or_id>
```

选项与 `docker-compose logs` 类似 (`-f`, `-t`, `--tail`)。

**示例：查看 MySQL 容器的最后 50 行日志:**

```bash
docker logs --tail 50 simpletrade-mysql
```

### 停止开发环境

完成开发工作后，停止并移除容器以释放资源。

**使用 Docker Compose:**

```bash
docker-compose -f <your_compose_file>.yml down
```

这将停止并移除由该 compose 文件定义的所有服务相关的容器、网络。

**注意:** 默认情况下，`down` 命令**不会**删除 Docker 卷 (Volumes)，这意味着您的数据库数据 (`mysql-data`) 和其他持久化数据会保留。如果需要彻底清除卷，可以添加 `-v` 参数: `docker-compose -f <your_compose_file>.yml down -v` (请谨慎使用)。

## 5. 常见问题解决

*   **端口冲突 (`Bind for 0.0.0.0:XXXX failed: port is already allocated`):**
    *   **原因:** 您宿主机上的另一个应用程序正在使用 Docker 想要映射的端口 (如 3306, 8080, 8003, 8888)。
    *   **解决:**
        1.  找到并停止占用端口的本机应用程序 (例如，停止本机的 MySQL 服务以释放 3306)。
        2.  或者，修改 `docker-compose.*.yml` 文件中的 `ports` 映射，将**冒号左侧**的宿主机端口改为一个未被占用的端口 (就像我们将 MySQL 改为 `3307:3306` 一样)。修改后需要 `down` 和 `up` 重启服务。
*   **后端代码修改后 API 未更新:**
    *   **原因:** Uvicorn 热重载可能因文件系统事件问题未触发。
    *   **解决:** 确认 `api` 服务的 `command` 中包含 `--reload` 和 `--reload-dir /app` 参数。如果问题仍然存在，尝试重启 Docker 服务 (`down` 和 `up`)。
*   **依赖安装失败:**
    *   **原因:** 网络问题、镜像源问题、依赖冲突。
    *   **解决:** 检查 Dockerfile 和 `docker-compose.*.yml` 中的镜像源配置是否正确且可用。尝试清理 Docker 缓存 (`docker system prune -a`) 并重新构建 (`<start_script>.sh --rebuild` 或 `docker-compose build --no-cache`)。
*   **容器启动失败/日志无输出:**
    *   **原因:** 启动命令错误、脚本内部错误、资源不足。
    *   **解决:** 使用 `docker logs <container_name>` 查看具体错误。尝试进入容器 (`docker exec -it <container_name> bash`) 手动执行启动命令排查。

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

3. **构建和启动容器**：
   - 在 M4 Mac 上：**必须**使用 `./start_docker_arm64.sh` 或 `docker-compose -f docker-compose.arm64.yml up --build ...`
   - 在 Intel Mac 上：可以使用 `./start_docker.sh` 或 `docker-compose up --build ...`

Docker 会根据使用的 Dockerfile (如 `Dockerfile.arm64` vs `Dockerfile`) 处理架构差异。

### 性能考虑

在 M4 Mac 上，Docker 容器的性能通常很好，因为它使用原生虚拟化。在 Intel Mac 上，性能可能略低，但对于开发目的来说通常足够。

### 数据持久化

当您在不同机器之间切换时，需要注意数据持久化问题。如果您的应用程序在容器内存储数据，这些数据在不同机器之间不会自动同步。您可能需要使用外部存储或手动同步数据。

## 7. Docker 常用命令参考

以下是一些常用的 Docker 命令，可以帮助您管理开发环境。

**注意:** 如果您在 **ARM64 Mac** 上操作，并且项目使用了特定的 `arm64` 配置文件，记得在 `docker-compose` 命令后添加 `-f docker-compose.arm64.yml` 参数，例如：`docker-compose -f docker-compose.arm64.yml ps`。

### 构建和启动容器

```bash
# 构建并启动容器 (使用默认 compose 文件)
docker-compose up --build

# 构建并启动容器 (使用特定 compose 文件, e.g., for ARM64)
docker-compose -f docker-compose.arm64.yml up --build

# 在后台启动容器 (根据需要添加 -f)
docker-compose up -d

# 只构建镜像，不启动容器 (根据需要添加 -f)
docker-compose build
```

### 管理容器

```bash
# 停止容器 (根据需要添加 -f)
docker-compose down

# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 查看容器日志 (根据需要添加 -f)
docker-compose logs -f <service_name>
# 例如: docker-compose -f docker-compose.arm64.yml logs -f api

# 进入容器 (根据需要添加 -f)
docker-compose exec <service_name> bash
# 例如: docker-compose -f docker-compose.arm64.yml exec api bash
```

### 管理镜像

```