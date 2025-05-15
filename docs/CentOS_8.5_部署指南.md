# CentOS 8.5 部署指南

本指南适用于在CentOS 8.5环境中部署SimpleTrade应用，特别优化了对低内存环境（2核2GB内存）的支持。

## 系统要求

- CentOS 8.5 64位操作系统
- 至少2GB内存
- 至少20GB磁盘空间
- 互联网连接（用于下载依赖）

## 部署步骤

### 1. 准备工作

首先，确保您有root权限，并且系统已经更新到最新状态：

```bash
# 切换到root用户
sudo -i

# 更新系统
dnf update -y
```

### 2. 克隆代码仓库

```bash
# 创建目录
mkdir -p /opt
cd /opt

# 克隆代码仓库
git clone https://github.com/yourusername/simpletrade.git
cd simpletrade
```

### 3. 系统初始化

运行系统初始化脚本，安装Docker和其他必要软件：

```bash
# 赋予脚本执行权限
chmod +x deploy/scripts/centos_setup.sh

# 运行系统初始化脚本
./deploy/scripts/centos_setup.sh --all
```

### 4. 部署应用

使用低内存环境优化的部署脚本部署应用：

```bash
# 赋予脚本执行权限
chmod +x deploy/scripts/deploy_centos8_lowmem.sh

# 构建Docker镜像并运行容器
./deploy/scripts/deploy_centos8_lowmem.sh --build --run
```

### 5. 验证部署

部署完成后，您可以通过以下方式验证应用是否正常运行：

```bash
# 查看容器状态
docker ps

# 查看容器日志
./deploy/scripts/deploy_centos8_lowmem.sh --logs
```

应用将在以下地址可用：
- 前端界面：http://your_server_ip
- 部署面板：http://your_server_ip/deploy/
  - 用户名：admin
  - 密码：admin123

## 常用操作

### 停止容器

```bash
./deploy/scripts/deploy_centos8_lowmem.sh --stop
```

### 启动容器

```bash
./deploy/scripts/deploy_centos8_lowmem.sh --run
```

### 删除容器

```bash
./deploy/scripts/deploy_centos8_lowmem.sh --delete
```

### 清理系统缓存和Docker缓存

```bash
./deploy/scripts/deploy_centos8_lowmem.sh --clean
```

### 创建交换文件（如果内存不足）

```bash
./deploy/scripts/deploy_centos8_lowmem.sh --swap
```

## 低内存环境优化

对于2核2GB内存的服务器，我们进行了以下优化：

1. **使用轻量级的Docker镜像**：基于CentOS 8的最小化镜像
2. **优化Node.js构建过程**：限制内存使用，避免OOM错误
3. **添加交换文件支持**：在内存不足时使用磁盘空间作为虚拟内存
4. **清理系统缓存**：定期清理系统缓存，释放内存

## 故障排除

### 1. Docker镜像构建失败

如果Docker镜像构建失败，可能是由于内存不足。尝试以下解决方案：

```bash
# 清理系统缓存
./deploy/scripts/deploy_centos8_lowmem.sh --clean

# 创建交换文件
./deploy/scripts/deploy_centos8_lowmem.sh --swap

# 重新构建镜像
./deploy/scripts/deploy_centos8_lowmem.sh --build
```

### 2. 容器启动失败

如果容器启动失败，检查日志：

```bash
./deploy/scripts/deploy_centos8_lowmem.sh --logs
```

### 3. 无法访问应用

如果无法访问应用，检查防火墙设置：

```bash
# 检查防火墙状态
systemctl status firewalld

# 如果防火墙启用，允许HTTP流量
firewall-cmd --permanent --add-service=http
firewall-cmd --reload
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
