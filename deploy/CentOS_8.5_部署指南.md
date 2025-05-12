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

由于 CentOS 8 已经结束生命周期，默认存储库可能不可用。我们的 Dockerfile 使用了阿里云的 CentOS 8 镜像源，避免了连接官方存储库的问题。

如果您需要手动配置 CentOS 8 的镜像源，可以执行以下命令：

```bash
# 备份原始的repo文件
sudo mkdir -p /etc/yum.repos.d/backup
sudo cp /etc/yum.repos.d/CentOS-* /etc/yum.repos.d/backup/ 2>/dev/null || true

# 移除原有的repo文件
sudo rm -f /etc/yum.repos.d/CentOS-*.repo

# 创建新的Base仓库文件
sudo cat > /etc/yum.repos.d/CentOS-Base.repo << 'REPO'
[base]
name=CentOS-$releasever - Base - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/BaseOS/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[updates]
name=CentOS-$releasever - Updates - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/BaseOS/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[extras]
name=CentOS-$releasever - Extras - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/extras/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[centosplus]
name=CentOS-$releasever - Plus - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/centosplus/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[PowerTools]
name=CentOS-$releasever - PowerTools - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/PowerTools/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[AppStream]
name=CentOS-$releasever - AppStream - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/AppStream/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official
REPO

# 创建 EPEL 仓库文件
sudo cat > /etc/yum.repos.d/epel.repo << 'REPO'
[epel]
name=Extra Packages for Enterprise Linux $releasever - $basearch
baseurl=https://mirrors.aliyun.com/epel/8/Everything/x86_64/
enabled=1
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/epel/RPM-GPG-KEY-EPEL-8

[epel-debuginfo]
name=Extra Packages for Enterprise Linux $releasever - $basearch - Debug
baseurl=https://mirrors.aliyun.com/epel/8/Everything/x86_64/debug/
enabled=0
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/epel/RPM-GPG-KEY-EPEL-8

[epel-source]
name=Extra Packages for Enterprise Linux $releasever - $basearch - Source
baseurl=https://mirrors.aliyun.com/epel/8/Everything/source/tree/
enabled=0
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/epel/RPM-GPG-KEY-EPEL-8
REPO

# 清理缓存并重新生成
sudo dnf clean all
sudo dnf makecache
```

这将完全替换原有的软件源配置，使用阿里云的镜像源，并且禁用了mirrorlist，直接使用baseurl，避免了DNS解析问题。

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


**npm依赖冲突问题**：

如果遇到npm依赖冲突错误，例如：
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE could not resolve
```

可以尝试修改Dockerfile.centos文件，在npm install命令中添加`--legacy-peer-deps`参数：
```dockerfile
RUN npm install --legacy-peer-deps && \
    npm run build && \
    ...
```

这个参数告诉npm忽略对等依赖的检查，可以解决大多数依赖冲突问题。
**Node.js内存溢出问题**：

### 问题3: 容器无法启动

如果在构建前端项目时遇到内存溢出错误，例如：
```
FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory
```

可以尝试增加Node.js的内存限制：
```dockerfile
RUN npm install --legacy-peer-deps && \
    export NODE_OPTIONS="--max-old-space-size=2048" && \
    npm run build && \
    ...
```

这会将Node.js的堆内存限制增加到2GB。如果服务器内存充足，可以考虑设置更高的值，例如`4096`（4GB）。

另外，还可以尝试使用其他参数减少内存使用：
```dockerfile
RUN npm install --legacy-peer-deps --no-optional --no-audit --no-fund --prefer-offline && \
    export NODE_OPTIONS="--max-old-space-size=2048" && \
    npm run build && \
    ...

注意：不要使用`--production`参数，因为前端构建需要`@vue/cli-service`等开发依赖。
**低内存环境优化**：

如果您的服务器内存有限（例如只有2GB内存），可以尝试以下优化方法：

1. 在Dockerfile中使用更多的内存优化参数：
```dockerfile
RUN npm config set cache /tmp/npm-cache && \
    npm install --legacy-peer-deps --no-optional --production --no-audit --no-fund --prefer-offline && \
    rm -rf /tmp/npm-cache && \
    export NODE_OPTIONS="--max-old-space-size=1536" && \
    npm run build && \
    rm -rf node_modules
```

2. 在运行容器时限制内存使用：
```bash
docker run -d --name simpletrade \
    --memory="1536m" \
    --memory-swap="1536m" \
    ... \
    simpletrade:latest
```

3. 在构建过程中清理临时文件和缓存：
```bash
# 清理Docker缓存
docker system prune -af

# 清理系统缓存
sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches"
```

4. 如果服务器没有交换分区，可以添加一个：
```bash
# 创建2GB的交换文件
sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# 永久挂载交换文件
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 前端路由问题

如果在构建前端时遇到类似以下错误：

```
This relative module was not found:
* ../views/AIAnalysisView.vue in ./src/router/index.js
```

这是因为路由配置中引用了不存在的视图文件。直接修改前端路由文件，注释掉对应的路由配置：

```bash
# 编辑路由文件
vi web-frontend/src/router/index.js

# 注释掉如下代码
# {
#   path: '/ai-analysis',
#   name: 'aiAnalysis',
#   component: () => import(/* webpackChunkName: "ai" */ '../views/AIAnalysisView.vue')
# },
```

我们已经在代码仓库中直接修改了这个文件，注释掉了对AIAnalysisView.vue的引用。如果您使用最新的代码，应该不会遇到这个问题。
### Python命令问题

在CentOS 8.5中，安装的Python版本是`python39`，而不是默认的`python`。如果遇到类似以下错误：

```
/app/start.sh: line 58: python: command not found
```

有两种解决方法：

1. 修改启动脚本，将`python`命令改为`python3.9`：
```bash
# 编辑启动脚本
vi deploy/scripts/start.sh

# 将所有的python命令改为python3.9
```

2. 创建python符号链接：
```bash
ln -sf /usr/bin/python3.9 /usr/bin/python
ln -sf /usr/bin/pip3.9 /usr/bin/pip
```

我们已经在低内存环境的Dockerfile中添加了符号链接创建的命令，并且修改了启动脚本使用`python3.9`命令。如果您使用最新的代码，应该不会遇到这个问题。

### 低内存环境专用脚本

对于2核心2GB内存的低配置服务器，我们提供了一个专用的部署脚本：`deploy_centos8_lowmem.sh`。这个脚本包含了多种内存优化措施，可以在低内存环境中更可靠地运行。

使用方法：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/deploy_centos8_lowmem.sh

# 清理缓存并创建交换文件
./deploy/scripts/deploy_centos8_lowmem.sh --clean --swap

# 构建和运行
./deploy/scripts/deploy_centos8_lowmem.sh --build --run
```

这个脚本的主要特点：

1. 清理系统和Docker缓存，释放内存
2. 创建交换文件，增加可用内存
3. 使用优化的Dockerfile，减少内存使用
4. 限制容器内存使用，避免耗尽系统资源
5. 分步执行前端构建，减少内存压力

如果您的服务器内存只有2GB，强烈建议使用这个脚本而不是标准的`deploy_centos8.sh`脚本。

注意：不要使用`--production`参数，因为前端构建需要`@vue/cli-service`等开发依赖。但可以使用`--no-optional`、`--no-audit`、`--no-fund`等参数减少内存使用。

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
      --dns 8.8.8.8 \
      --dns 114.114.114.114 \
      simpletrade:latest
  ```

### 问题4: DNS解析问题

**症状**：在构建或运行过程中遇到DNS解析错误，无法访问某些域名。

**解决方案**：
- 在运行容器时指定DNS服务器：
  ```bash
  docker run -d --name simpletrade \
      --dns 8.8.8.8 \
      --dns 114.114.114.114 \
      ... \
      simpletrade:latest
  ```
- 或者在容器内部手动添加hosts条目：
  ```bash
  docker exec -it simpletrade bash -c "echo '185.199.108.133 raw.github.com' >> /etc/hosts"
  ```

### 问题5: 无法访问应用

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
