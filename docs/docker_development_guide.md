# Docker 开发环境设置指南

本文档提供了使用 Docker 设置 SimpleTrade 开发环境的详细步骤。使用 Docker 可以确保在不同机器（如公司的 M4 Mac 和家里的 Intel Mac）上有一致的开发体验。

## 目录

1. [安装 Docker Desktop](#1-安装-docker-desktop)
2. [项目 Docker 文件说明](#2-项目-docker-文件说明)
3. [构建和启动开发环境](#3-构建和启动开发环境)
4. [开发工作流](#4-开发工作流)
5. [常见问题解决](#5-常见问题解决)
6. [跨平台开发注意事项](#6-跨平台开发注意事项)
7. [Docker 常用命令参考](#7-docker-常用命令参考)

## 1. 安装 Docker Desktop

### macOS (Apple Silicon/M1/M2/M3/M4)

1. 访问 [Docker Desktop 下载页面](https://www.docker.com/products/docker-desktop)
2. 下载 "Mac with Apple Silicon" 版本
3. 打开下载的 `.dmg` 文件，将 Docker 图标拖到 Applications 文件夹
4. 从 Applications 文件夹启动 Docker Desktop
5. 首次启动时，可能需要输入管理员密码
6. 等待 Docker Desktop 完成初始化（状态栏图标变为稳定状态）

### macOS (Intel)

1. 访问 [Docker Desktop 下载页面](https://www.docker.com/products/docker-desktop)
2. 下载 "Mac with Intel Chip" 版本
3. 打开下载的 `.dmg` 文件，将 Docker 图标拖到 Applications 文件夹
4. 从 Applications 文件夹启动 Docker Desktop
5. 首次启动时，可能需要输入管理员密码
6. 等待 Docker Desktop 完成初始化（状态栏图标变为稳定状态）

### 验证安装

打开终端，运行以下命令验证 Docker 是否正确安装：

```bash
docker --version
docker compose version
```

如果命令返回版本信息，则表示安装成功。

## 2. 项目 Docker 文件说明

SimpleTrade 项目包含以下 Docker 相关文件：

### Dockerfile

`Dockerfile` 定义了项目的开发环境，包括：

- 基础镜像：`continuumio/miniconda3`
- 系统依赖：build-essential, wget 等
- TA-Lib 库的安装
- Conda 环境的创建和配置
- 项目依赖的安装

文件内容：

```dockerfile
FROM continuumio/miniconda3

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安装 TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib-0.4.0-src.tar.gz ta-lib/

# 创建 conda 环境
RUN conda create -n simpletrade python=3.12 -y

# 安装依赖
RUN conda install -n simpletrade -c conda-forge ta-lib -y && \
    conda run -n simpletrade pip install vnpy vnpy_sqlite fastapi uvicorn[standard] pydantic[email] tigeropen

# 设置工作目录
WORKDIR /app

# 暴露端口
EXPOSE 8002

# 启动命令
CMD ["conda", "run", "--no-capture-output", "-n", "simpletrade", "python", "-m", "uvicorn", "simpletrade.api.server:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
```

### docker-compose.yml

`docker-compose.yml` 定义了项目的服务配置，包括：

- 服务名称：api
- 端口映射：8002:8002
- 卷挂载：将本地目录挂载到容器中
- 环境变量：PYTHONPATH
- 启动命令

文件内容：

```yaml
version: '3'

services:
  api:
    build: .
    ports:
      - "8002:8002"
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
    command: conda run --no-capture-output -n simpletrade python -m uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8002 --reload

  # 前端服务暂时注释掉，专注于后端开发
  # frontend:
  #   image: node:14
  #   working_dir: /app
  #   volumes:
  #     - ./web-frontend:/app
  #   ports:
  #     - "8080:8080"
  #   command: bash -c "npm install && npm run serve"
  #   depends_on:
  #     - api
```

### start_docker.sh

`start_docker.sh` 是一个简单的启动脚本，用于启动 Docker 容器：

```bash
#!/bin/bash

# 确保脚本在项目根目录运行
cd "$(dirname "$0")"

# 启动 Docker 容器
docker compose up --build
```

## 3. 构建和启动开发环境

### 步骤 1: 确保 Docker Desktop 正在运行

在启动开发环境之前，确保 Docker Desktop 应用程序已经启动。您可以在状态栏中查看 Docker 图标，或者打开 Applications 文件夹并启动 Docker Desktop。

### 步骤 2: 打开终端

打开终端应用程序。

### 步骤 3: 导航到项目目录

```bash
cd /Users/chengzheng/workspace/trade/simpletrade
```

或者使用您的项目实际路径。

### 步骤 4: 启动开发环境

有两种方式启动开发环境：

#### 方式 1: 使用启动脚本

```bash
./start_docker.sh
```

#### 方式 2: 直接使用 docker compose 命令

```bash
docker compose up --build
```

第一次构建可能需要 10-15 分钟，因为它需要下载基础镜像、安装依赖等。后续启动会更快。

### 步骤 5: 验证开发环境

构建完成并启动容器后，您应该能看到类似以下的输出：

```
api_1  | INFO:     Will watch for changes in these directories: ['/app']
api_1  | INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
api_1  | INFO:     Started reloader process [1] using WatchFiles
api_1  | Test API routes added successfully.
api_1  | Health check API route added.
...
```

现在，您可以在浏览器中访问 `http://localhost:8002/docs` 查看 API 文档。

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

### 查看日志

Docker 容器的日志会实时显示在终端中。如果您在另一个终端中启动了容器，可以使用以下命令查看日志：

```bash
docker compose logs -f
```

### 停止开发环境

当您完成开发时，可以按 `Ctrl+C` 停止容器，或者在另一个终端中运行：

```bash
docker compose down
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
sudo docker compose up --build
```

### 问题 3: 镜像构建失败

如果镜像构建失败，可能会看到各种错误信息。常见的解决方案包括：

1. 检查网络连接
2. 确保 Docker Desktop 正在运行
3. 尝试重新构建镜像：

```bash
docker compose build --no-cache
```

### 问题 4: 卷挂载问题

如果代码更改没有反映到容器中，可能是卷挂载问题。解决方案：

1. 确保 `docker-compose.yml` 文件中的卷挂载配置正确
2. 重新启动容器
3. 检查 Docker Desktop 的文件共享设置

## 6. 跨平台开发注意事项

### 在 M4 Mac 和 Intel Mac 之间切换

Docker 的一个主要优势是能够在不同架构的机器上提供一致的开发环境。当您在 M4 Mac 和 Intel Mac 之间切换时，只需要执行相同的步骤：

1. 确保 Docker Desktop 已安装并运行
2. 导航到项目目录
3. 运行 `docker compose up --build`

Docker 会自动处理架构差异，因为我们使用的是支持多架构的基础镜像。

### 性能考虑

在 M4 Mac 上，Docker 容器的性能通常很好，因为它使用原生虚拟化。在 Intel Mac 上，性能可能略低，但对于开发目的来说通常足够。

## 7. Docker 常用命令参考

以下是一些常用的 Docker 命令，可以帮助您管理开发环境：

### 构建和启动容器

```bash
# 构建并启动容器
docker compose up --build

# 在后台启动容器
docker compose up -d

# 只构建镜像，不启动容器
docker compose build
```

### 管理容器

```bash
# 停止容器
docker compose down

# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 查看容器日志
docker compose logs -f

# 进入容器
docker compose exec api bash
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
