# SimpleTrade CentOS 8.5 部署指南

## 概述

本文档提供了在CentOS 8.5环境中部署SimpleTrade应用的方法，特别适用于网络受限的环境。通过使用本地Docker镜像，我们可以在无法正常访问Docker Hub的环境中优雅地部署应用。

## 目录结构

```
deploy/
├── CentOS_8.5_部署指南_网络受限环境.md  # 详细的部署指南
├── Dockerfile.centos                  # 专为CentOS 8.5环境优化的Dockerfile
├── config/                            # 配置文件
│   └── nginx.conf                     # Nginx配置
├── panel/                             # 部署面板
│   ├── deploy.py                      # 部署API服务器
│   └── index.html                     # 部署面板Web界面
└── scripts/                           # 脚本
    ├── centos_deploy.sh               # 旧版部署脚本（已弃用）
    ├── centos_setup.sh                # CentOS环境设置脚本
    ├── deploy_centos8.sh              # 新版优雅部署脚本
    └── start.sh                       # 容器启动脚本
```

## 快速开始

### 步骤1: 准备环境

首先，确保已安装Docker并配置好环境：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/centos_setup.sh

# 运行环境设置脚本
sudo ./deploy/scripts/centos_setup.sh --all
```

### 步骤2: 部署应用

使用优雅部署脚本构建和运行应用：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/deploy_centos8.sh

# 构建和运行
./deploy/scripts/deploy_centos8.sh --build --run
```

### 步骤3: 访问应用

部署完成后，您可以通过服务器IP地址访问应用：

- **前端应用**: http://your-server-ip/
- **部署面板**: http://your-server-ip/deploy/
  - 用户名: admin
  - 密码: admin123

## 详细说明

### 环境设置脚本 (centos_setup.sh)

此脚本用于设置CentOS 8.5环境，包括：

- 安装Docker和必要的依赖
- 配置SELinux以允许Docker容器运行
- 配置防火墙开放HTTP端口

使用方法：

```bash
./deploy/scripts/centos_setup.sh --all
```

### 优雅部署脚本 (deploy_centos8.sh)

此脚本用于构建和运行Docker容器，特别优化用于网络受限的环境：

- 使用本地CentOS 8镜像作为基础镜像
- 在单个阶段中完成所有构建步骤
- 添加SELinux兼容参数
- 创建必要的数据和日志目录

使用方法：

```bash
# 构建Docker镜像
./deploy/scripts/deploy_centos8.sh --build

# 运行Docker容器
./deploy/scripts/deploy_centos8.sh --run

# 停止Docker容器
./deploy/scripts/deploy_centos8.sh --stop

# 删除Docker容器
./deploy/scripts/deploy_centos8.sh --delete

# 查看容器日志
./deploy/scripts/deploy_centos8.sh --logs
```

### Dockerfile.centos

此Dockerfile专为CentOS 8.5环境优化，使用CentOS 8作为基础镜像，避免从Docker Hub拉取外部镜像。它在单个阶段中完成所有构建步骤，包括：

- 配置CentOS 8的存储库（因为CentOS 8已经EOL）
- 安装Node.js、Python和其他必要的软件
- 构建前端和后端
- 配置Nginx和启动脚本

## 故障排除

### 问题1: Docker安装失败

**症状**：运行`centos_setup.sh`脚本时，Docker安装失败。

**解决方案**：
```bash
# 手动安装Docker
sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y --nobest docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

### 问题2: 构建失败

**症状**：运行`deploy_centos8.sh --build`时，构建失败。

**解决方案**：
- 检查构建日志：`cat /opt/simpletrade/deploy/logs/build_*.log`
- 确保CentOS 8镜像可用：`docker images | grep centos`
- 如果CentOS 8镜像不可用，可以尝试手动拉取：`docker pull centos:8`

### 问题3: 容器无法启动

**症状**：运行`deploy_centos8.sh --run`时，容器无法启动。

**解决方案**：
- 查看Docker错误日志：`docker logs simpletrade`
- 检查SELinux状态：`getenforce`
- 如果SELinux是问题，可以临时禁用：`sudo setenforce 0`

## 更多信息

有关更详细的部署指南，请参阅[CentOS_8.5_部署指南_网络受限环境.md](./CentOS_8.5_部署指南_网络受限环境.md)。

---

**文档版本**: 1.0  
**最后更新**: 2023年11月15日  
**适用环境**: CentOS 8.5 64位  
**文档作者**: SimpleTrade团队
