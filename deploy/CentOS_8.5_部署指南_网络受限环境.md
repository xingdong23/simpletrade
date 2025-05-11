# SimpleTrade 在网络受限的 CentOS 8.5 上的部署指南

## 概述

本文档专门针对**网络受限的 CentOS 8.5** 环境，提供了详细的 SimpleTrade 应用部署步骤。通过本指南，您可以在无法正常访问 Docker Hub 的 CentOS 8.5 服务器上成功部署 SimpleTrade 应用，实现前后端一体化部署和可视化发布流程。

## 环境要求

- **操作系统**: CentOS 8.5 64位
- **最低配置**: 
  - CPU: 2核
  - 内存: 4GB
  - 磁盘: 20GB
- **网络**: 开放80端口(HTTP)和22端口(SSH)
- **特殊情况**: 无法正常访问 Docker Hub

## 详细步骤

### 步骤1: 准备环境

首先，通过SSH连接到您的CentOS 8.5服务器：

```bash
ssh username@your-server-ip
```

### 步骤2: 克隆代码仓库

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

### 步骤3: 运行CentOS 8.5专用设置脚本

我们提供了一个专门针对CentOS 8.5的环境设置脚本，它会自动安装Docker、配置SELinux和防火墙：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/centos_setup.sh

# 运行设置脚本（需要root权限）
sudo ./deploy/scripts/centos_setup.sh --all
```

脚本执行过程中会显示详细的输出信息，请注意观察是否有错误发生。

**脚本功能说明**:
- 安装Docker和必要的依赖
- 配置SELinux以允许Docker容器运行
- 配置防火墙开放HTTP端口
- 安装Git和其他有用的工具

### 步骤4: 构建和运行应用

由于CentOS 8.5环境可能存在网络限制，我们提供了一个专门的CentOS部署脚本，使用本地CentOS镜像进行构建：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/centos_deploy.sh

# 构建Docker镜像
./deploy/scripts/centos_deploy.sh --build

# 运行Docker容器
./deploy/scripts/centos_deploy.sh --run

# 或者一步完成构建和运行
./deploy/scripts/centos_deploy.sh --build --run
```

**脚本功能说明**:
- 使用CentOS 8作为基础镜像，避免从外部拉取镜像
- 在单个阶段中完成所有构建步骤
- 添加SELinux兼容参数
- 创建必要的数据和日志目录
- 设置数据卷映射，确保数据持久化
- 显示访问地址和认证信息

### 步骤5: 访问应用

部署完成后，您可以通过以下地址访问应用：

- **前端应用**: http://your-server-ip/
- **部署面板**: http://your-server-ip/deploy/
  - 用户名: admin
  - 密码: admin123

### 步骤6: 使用部署面板

通过部署面板，您可以：

1. 查看当前版本信息
2. 部署新版本：
   - 输入要部署的版本标识（分支名、标签名或提交哈希）
   - 点击"开始部署"按钮
   - 确认部署
   - 等待部署完成
   - 查看部署日志

## 网络受限环境的特殊处理

### Docker镜像构建策略

在网络受限环境中，我们采用以下策略来构建Docker镜像：

1. **使用本地基础镜像**: 使用CentOS 8作为基础镜像，避免从Docker Hub拉取镜像
2. **单阶段构建**: 在单个构建阶段中完成所有操作，避免多阶段构建需要的多个基础镜像
3. **本地安装依赖**: 使用CentOS的包管理器安装Node.js、Python和其他依赖

### npm和pip镜像源配置

如果npm或pip安装过程中遇到网络问题，可以配置国内镜像源：

```bash
# 配置npm使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 配置pip使用阿里云镜像
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

### 离线安装包准备

如果服务器完全无法访问外网，您可以在有网络的环境中准备离线安装包：

```bash
# 在有网络的环境中
# 下载Node.js和Python的rpm包
# 下载前端依赖
cd /path/to/web-frontend
npm install --package-lock-only
npm ci --offline

# 下载后端依赖
cd /path/to/backend
pip download -r requirements.txt -d ./pip-packages
```

然后将这些包传输到服务器，进行离线安装。

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

## 维护操作

### 查看容器日志

```bash
# 查看容器日志
docker logs simpletrade

# 实时查看日志
docker logs -f simpletrade
```

### 重启容器

```bash
# 重启容器
docker restart simpletrade
```

### 停止和删除容器

```bash
# 停止容器
./deploy/scripts/centos_deploy.sh --stop

# 删除容器
./deploy/scripts/centos_deploy.sh --delete
```

### 备份数据

```bash
# 备份数据目录
sudo cp -r /opt/simpletrade/data /opt/simpletrade/data_backup_$(date +%Y%m%d)

# 备份日志目录
sudo cp -r /opt/simpletrade/deploy/logs /opt/simpletrade/logs_backup_$(date +%Y%m%d)
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

### 问题2: 构建过程中npm或pip安装失败

**症状**：构建Docker镜像时，npm或pip安装依赖失败。

**解决方案**：
```bash
# 修改Dockerfile.centos，添加镜像源配置
# 在RUN npm install之前添加：
RUN npm config set registry https://registry.npmmirror.com

# 在RUN pip3 install之前添加：
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

### 问题3: 容器无法启动

**症状**：运行`centos_deploy.sh --run`时，容器无法启动。

**解决方案**：
```bash
# 查看Docker错误日志
docker logs simpletrade

# 如果是SELinux问题，临时禁用SELinux
sudo setenforce 0

# 手动运行容器，添加更多参数
docker run -d --name simpletrade \
    -p 80:80 \
    -v "$(pwd)/deploy/logs:/app/logs" \
    -v "$(pwd)/data:/app/data" \
    --security-opt label=disable \
    simpletrade:latest
```

## 结论

通过本文档的指导，您应该能够在网络受限的CentOS 8.5服务器上成功部署SimpleTrade应用。这个部署方案专门针对无法正常访问Docker Hub的环境，通过使用本地CentOS镜像和单阶段构建，避免了对外部镜像的依赖。

如果您在部署过程中遇到任何问题，请参考故障排除部分或联系技术支持团队获取帮助。

---

**文档版本**: 1.0  
**最后更新**: 2023年11月15日  
**适用环境**: 网络受限的CentOS 8.5 64位  
**文档作者**: SimpleTrade团队
