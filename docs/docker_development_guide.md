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

# 直接用 conda 安装 TA-Lib，无需源码编译
# 创建 conda 环境
RUN conda create -n simpletrade python=3.12 -y

# 移除 conda 官方源，仅用清华镜像
RUN conda config --remove-key channels || true
RUN conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/ \
    && conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ \
    && conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ \
    && conda config --set show_channel_urls yes

# 安装依赖
RUN conda install -n simpletrade ta-lib -y && \
    conda run -n simpletrade pip install vnpy vnpy_sqlite fastapi uvicorn[standard] pydantic[email] tigeropen requests python-multipart python-jose

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
docker-compose up --build
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

4. **启动开发环境**

   有两种方式启动开发环境：

   **方式 1: 使用启动脚本**

   ```bash
   ./start_docker.sh
   ```

   **方式 2: 直接使用 docker-compose 命令**

   ```bash
   docker-compose up --build
   ```

   第一次构建可能需要 10-15 分钟，因为它需要下载基础镜像、安装依赖等。后续启动会更快。

### 验证开发环境

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

## 7. Docker 常用命令参考

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
