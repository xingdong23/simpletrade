# SimpleTrade CentOS 8.5 部署指南

## 概述

本文档提供了在CentOS 8.5环境中部署SimpleTrade应用的完整指南，特别适用于网络受限的环境。通过使用本地Docker镜像，我们可以在无法正常访问Docker Hub的环境中优雅地部署应用。

## 目录结构

```
deploy/
├── CentOS_8.5_部署指南.md              # 本文档：完整的部署指南
├── Dockerfile.centos                  # 专为CentOS 8.5环境优化的Dockerfile
├── config/                            # 配置文件
│   └── nginx.conf                     # Nginx配置
├── panel/                             # 部署面板
│   ├── deploy.py                      # 部署API服务器
│   └── index.html                     # 部署面板Web界面
└── scripts/                           # 脚本
    ├── centos_setup.sh                # CentOS环境设置脚本
    ├── deploy_centos8_lowmem.sh       # 低内存环境优化部署脚本
    └── start.sh                       # 容器启动脚本
```

## 环境要求

- **操作系统**: CentOS 8.5 64位
- **最低配置**:
  - CPU: 2核
  - 内存: 2GB
  - 磁盘: 20GB
- **网络**: 开放80端口(HTTP)和22端口(SSH)
- **特殊情况**: 可能无法正常访问Docker Hub

## 快速开始

### 步骤1: 准备环境

首先，通过SSH连接到您的CentOS 8.5服务器：

```bash
ssh username@your-server-ip
```

创建工作目录并克隆代码仓库：

```bash
# 创建工作目录
sudo mkdir -p /opt/simpletrade

# 设置目录权限
sudo chown -R $(whoami):$(whoami) /opt/simpletrade

# 克隆代码仓库
git clone https://github.com/yourusername/simpletrade.git /opt/simpletrade

# 进入项目目录
cd /opt/simpletrade
```

### 步骤2: 设置CentOS环境

运行环境设置脚本，安装Docker和其他必要软件：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/centos_setup.sh

# 运行环境设置脚本
sudo ./deploy/scripts/centos_setup.sh --all
```

### 步骤3: 部署应用

使用优雅部署脚本构建和运行应用：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/deploy_centos8_lowmem.sh

# 构建和运行
./deploy/scripts/deploy_centos8_lowmem.sh --build --run
```

### 步骤4: 访问应用

部署完成后，您可以通过以下URL访问应用：

- **前端应用**: http://your-server-ip
- **部署面板**: http://your-server-ip/deploy/
  - 用户名: admin
  - 密码: admin123

## 详细说明

### 环境设置脚本 (centos_setup.sh)

此脚本用于在CentOS 8.5环境中设置必要的软件和配置：

```bash
# 安装Docker和其他必要软件
./deploy/scripts/centos_setup.sh --install

# 配置SELinux以允许Docker
./deploy/scripts/centos_setup.sh --selinux

# 配置防火墙以开放HTTP端口
./deploy/scripts/centos_setup.sh --firewall

# 执行所有操作
./deploy/scripts/centos_setup.sh --all
```

### 低内存环境优化部署脚本 (deploy_centos8_lowmem.sh)

此脚本专为低内存环境（2核2GB）优化，提供了构建、运行、停止和删除Docker容器的功能：

```bash
# 构建Docker镜像
./deploy/scripts/deploy_centos8_lowmem.sh --build

# 运行Docker容器
./deploy/scripts/deploy_centos8_lowmem.sh --run

# 停止Docker容器
./deploy/scripts/deploy_centos8_lowmem.sh --stop

# 删除Docker容器
./deploy/scripts/deploy_centos8_lowmem.sh --delete

# 查看容器日志
./deploy/scripts/deploy_centos8_lowmem.sh --logs

# 清理系统缓存和Docker缓存
./deploy/scripts/deploy_centos8_lowmem.sh --clean

# 创建交换文件（如果没有）
./deploy/scripts/deploy_centos8_lowmem.sh --swap
```

## 常见问题

### 1. Docker镜像构建失败

如果在构建Docker镜像时遇到问题，可能是由于以下原因：

- **内存不足**: 在低内存环境中，构建过程可能会失败。尝试清理系统缓存并创建交换文件：

  ```bash
  # 清理系统缓存
  ./deploy/scripts/deploy_centos8_lowmem.sh --clean

  # 创建交换文件
  ./deploy/scripts/deploy_centos8_lowmem.sh --swap

  # 重新构建
  ./deploy/scripts/deploy_centos8_lowmem.sh --build
  ```

- **网络问题**: 如果无法访问Docker Hub，构建可能会失败。确保已配置Docker镜像加速器：

  ```bash
  # 查看构建日志
  ./deploy/scripts/deploy_centos8_lowmem.sh --logs
  ```

### 2. 容器启动失败

如果容器无法正常启动，请检查日志：

```bash
# 查看容器日志
./deploy/scripts/deploy_centos8_lowmem.sh --logs
```

### 3. 无法访问应用

如果无法通过浏览器访问应用，请检查：

- **防火墙设置**: 确保80端口已开放
- **容器状态**: 确保容器正在运行
- **Nginx配置**: 检查Nginx配置是否正确

```bash
# 检查容器状态
docker ps

# 停止并重新启动容器
./deploy/scripts/deploy_centos8_lowmem.sh --stop
./deploy/scripts/deploy_centos8_lowmem.sh --run
```

## 更新应用

要更新应用，请按照以下步骤操作：

```bash
# 进入项目目录
cd /opt/simpletrade

# 拉取最新代码
git pull

# 重新构建并运行
./deploy/scripts/deploy_centos8_lowmem.sh --build --run
```

## 备份和恢复

### 备份数据

```bash
# 备份数据目录
tar -czvf simpletrade_data_backup.tar.gz /opt/simpletrade/data
```

### 恢复数据

```bash
# 恢复数据目录
tar -xzvf simpletrade_data_backup.tar.gz -C /
```

## 低内存环境优化

对于2核2GB内存的服务器，我们进行了以下优化：

1. **使用轻量级的Docker镜像**：基于CentOS 8的最小化镜像
2. **优化Node.js构建过程**：限制内存使用，避免OOM错误
3. **添加交换文件支持**：在内存不足时使用磁盘空间作为虚拟内存
4. **清理系统缓存**：定期清理系统缓存，释放内存

## 安全建议

1. **更改默认密码**：部署后立即更改部署面板的默认密码
2. **使用HTTPS**：在生产环境中，建议配置HTTPS
3. **限制SSH访问**：只允许特定IP地址通过SSH连接
4. **定期更新**：保持系统和应用的更新

## 故障排除

### 检查Docker状态

```bash
# 检查Docker服务状态
systemctl status docker

# 重启Docker服务
systemctl restart docker
```

### 检查容器状态

```bash
# 列出所有容器
docker ps -a

# 查看容器日志
docker logs simpletrade
```

### 检查磁盘空间

```bash
# 检查磁盘使用情况
df -h

# 清理Docker缓存
docker system prune -a
```

### 检查内存使用情况

```bash
# 检查内存使用情况
free -h

# 清理系统缓存
echo 3 > /proc/sys/vm/drop_caches
```

## 参考资料

- [Docker官方文档](https://docs.docker.com/)
- [CentOS 8.5文档](https://docs.centos.org/en-US/8-docs/)
