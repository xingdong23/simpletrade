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
    ├── deploy_centos8.sh              # 优雅部署脚本
    └── start.sh                       # 容器启动脚本
```

## 环境要求

- **操作系统**: CentOS 8.5 64位
- **最低配置**: 
  - CPU: 2核
  - 内存: 4GB
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

# 进入工作目录
cd /opt/simpletrade

# 克隆代码仓库（使用您的实际仓库地址）
git clone https://github.com/yourusername/simpletrade.git .
```

运行环境设置脚本，安装Docker和其他必要软件：

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
- 安装Git和其他有用的工具

使用方法：

```bash
./deploy/scripts/centos_setup.sh --all
```

或者使用特定选项：

```bash
# 只安装Docker
./deploy/scripts/centos_setup.sh --install

# 只配置SELinux
./deploy/scripts/centos_setup.sh --selinux

# 只配置防火墙
./deploy/scripts/centos_setup.sh --firewall
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

### 部署面板

部署面板是一个简单的Web界面，用于管理应用的部署。通过部署面板，您可以：

1. 查看当前版本信息
2. 部署新版本：
   - 输入要部署的版本标识（分支名、标签名或提交哈希）
   - 点击"开始部署"按钮
   - 确认部署
   - 等待部署完成
   - 查看部署日志

## 网络受限环境的特殊处理

### 使用阿里云镜像加速器

在网络受限环境中，您可能无法直接从Docker Hub拉取镜像。我们的部署脚本已集成了阿里云镜像加速器的配置，可以显著提高镜像拉取速度。

脚本会自动执行以下操作：

```bash
# 创建daemon.json文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://qoy9ouh4.mirror.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

如果您想手动配置阿里云镜像加速器，可以执行上述命令。

在大多数情况下，使用阿里云镜像加速器应该能够成功拉取CentOS 8镜像。如果仍然无法拉取，可以尝试以下方法：

### 基础镜像准备

如果使用阿里云镜像加速器仍然无法拉取镜像，您可以手动准备镜像并导入到服务器。

如果您的环境中没有CentOS 8镜像，您可以在可访问互联网的环境中准备镜像：

1. 在可访问互联网的环境中拉取镜像：
   ```bash
   docker pull centos:8
   ```

2. 将镜像保存为tar文件：
   ```bash
   docker save -o centos8.tar centos:8
   ```

3. 将tar文件传输到服务器：
   ```bash
   scp centos8.tar user@your-server-ip:/path/to/save
   ```

4. 在服务器上加载镜像：
   ```bash
   docker load -i /path/to/save/centos8.tar
   ```

### npm和pip镜像源配置

如果npm或pip安装过程中遇到网络问题，可以配置国内镜像源：

```bash
# 配置npm使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 配置pip使用阿里云镜像
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

您可以修改`Dockerfile.centos`文件，添加这些配置：

```dockerfile
# 配置npm镜像
RUN npm config set registry https://registry.npmmirror.com

# 配置pip镜像
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

## CentOS 8.5 特有问题及解决方案

### SELinux 相关问题

如果遇到权限问题，可能是由于SELinux的限制：

```bash
# 查看SELinux状态
getenforce

# 临时禁用SELinux
sudo setenforce 0

# 永久禁用SELinux（需要重启）
sudo sed -i 's/^SELINUX=enforcing$/SELINUX=disabled/' /etc/selinux/config
sudo reboot
```

### 防火墙配置

确保防火墙已开放HTTP端口：

```bash
# 查看防火墙状态
sudo systemctl status firewalld

# 开放HTTP端口
sudo firewall-cmd --permanent --add-service=http

# 重新加载防火墙配置
sudo firewall-cmd --reload
```

### CentOS 8 存储库问题

由于CentOS 8已经结束生命周期，默认存储库可能不可用。我们的Dockerfile已经处理了这个问题，但如果您需要手动修复：

```bash
# 将镜像源从mirror.centos.org切换到vault.centos.org
sudo sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
sudo sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
```

### 系统限制调整

如果遇到"too many open files"等系统限制问题：

```bash
# 增加文件描述符限制
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 应用更改（需要重新登录）
sudo sysctl -p
```

## 维护操作

### 更新应用

要更新应用，只需拉取最新代码并重新部署：

```bash
# 拉取最新代码
cd /opt/simpletrade
git pull

# 重新构建和运行
./deploy/scripts/deploy_centos8.sh --build --run
```

### 查看日志

```bash
# 查看容器日志
./deploy/scripts/deploy_centos8.sh --logs

# 或者直接使用Docker命令
docker logs simpletrade

# 查看部署日志
ls -la /opt/simpletrade/deploy/logs/
```

### 备份数据

```bash
# 备份数据目录
sudo cp -r /opt/simpletrade/data /opt/simpletrade/data_backup_$(date +%Y%m%d)

# 备份日志目录
sudo cp -r /opt/simpletrade/deploy/logs /opt/simpletrade/logs_backup_$(date +%Y%m%d)
```

### 重启服务

```bash
# 重启容器
docker restart simpletrade

# 或者使用脚本停止后再运行
./deploy/scripts/deploy_centos8.sh --stop
./deploy/scripts/deploy_centos8.sh --run
```

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
- 如果无法从Docker Hub拉取，请参考"基础镜像准备"部分

### 问题3: 容器无法启动

**症状**：运行`deploy_centos8.sh --run`时，容器无法启动。

**解决方案**：
- 查看Docker错误日志：`docker logs simpletrade`
- 检查SELinux状态：`getenforce`
- 如果SELinux是问题，可以临时禁用：`sudo setenforce 0`
- 手动运行容器，添加更多参数：
  ```bash
  docker run -d --name simpletrade \
      -p 80:80 \
      -v "$(pwd)/deploy/logs:/app/logs" \
      -v "$(pwd)/data:/app/data" \
      --security-opt label=disable \
      simpletrade:latest
  ```

### 问题4: 无法访问应用

**症状**：容器已启动，但无法通过浏览器访问应用。

**解决方案**：
- 检查容器是否正在运行：`docker ps | grep simpletrade`
- 检查端口是否已开放：`sudo ss -tulpn | grep 80`
- 检查防火墙设置：`sudo firewall-cmd --list-all`
- 如果需要，开放HTTP端口：`sudo firewall-cmd --permanent --add-service=http && sudo firewall-cmd --reload`

## 结论

通过本文档的指导，您应该能够在CentOS 8.5服务器上成功部署SimpleTrade应用，即使在网络受限的环境中也能优雅地完成部署。我们的方案使用本地CentOS 8镜像作为基础镜像，避免了对Docker Hub的依赖，同时保留了Docker的所有优势。

如果您在部署过程中遇到任何问题，请参考故障排除部分或联系技术支持团队获取帮助。

---

**文档版本**: 1.0  
**最后更新**: 2023年11月15日  
**适用环境**: CentOS 8.5 64位  
**文档作者**: SimpleTrade团队
