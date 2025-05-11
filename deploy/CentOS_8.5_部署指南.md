# SimpleTrade 在 CentOS 8.5 上的部署指南

## 概述

本文档专门针对 **CentOS 8.5** 环境，提供了详细的 SimpleTrade 应用部署步骤。通过本指南，您可以在 CentOS 8.5 服务器上成功部署 SimpleTrade 应用，实现前后端一体化部署和可视化发布流程。

## 环境要求

- **操作系统**: CentOS 8.5 64位
- **最低配置**: 
  - CPU: 2核
  - 内存: 4GB
  - 磁盘: 20GB
- **网络**: 开放80端口(HTTP)和22端口(SSH)

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

使用我们提供的本地部署脚本来构建Docker镜像并运行容器：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/local_deploy.sh

# 构建Docker镜像
./deploy/scripts/local_deploy.sh --build

# 运行Docker容器
./deploy/scripts/local_deploy.sh --run

# 或者一步完成构建和运行
./deploy/scripts/local_deploy.sh --build --run
```

**脚本功能说明**:
- 自动检测CentOS环境并应用相应的Docker参数
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

### 系统限制调整

如果遇到"too many open files"等系统限制问题：

```bash
# 增加文件描述符限制
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 应用更改（需要重新登录）
sudo sysctl -p
```

### Docker 相关问题

如果Docker无法正常启动或运行：

```bash
# 查看Docker状态
sudo systemctl status docker

# 重启Docker服务
sudo systemctl restart docker

# 查看Docker日志
sudo journalctl -u docker
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
./deploy/scripts/local_deploy.sh --stop

# 删除容器
./deploy/scripts/local_deploy.sh --delete
```

### 备份数据

```bash
# 备份数据目录
sudo cp -r /opt/simpletrade/data /opt/simpletrade/data_backup_$(date +%Y%m%d)

# 备份日志目录
sudo cp -r /opt/simpletrade/deploy/logs /opt/simpletrade/logs_backup_$(date +%Y%m%d)
```

## 安全建议

1. **修改默认密码**：
   - 编辑 `deploy/scripts/start.sh` 文件
   - 修改 `admin:$(openssl passwd -apr1 admin123)` 中的用户名和密码
   - 重新构建和运行容器

2. **配置HTTPS**：
   - 获取SSL证书（可使用Let's Encrypt）
   - 配置Nginx使用SSL证书
   - 重定向HTTP请求到HTTPS

3. **限制访问IP**：
   - 配置防火墙只允许特定IP访问部署面板
   - 在Nginx配置中添加IP限制

## 注意事项

1. **CentOS 8生命周期**：CentOS 8已于2021年底结束支持，建议考虑升级到CentOS Stream 8或迁移到Rocky Linux/AlmaLinux。

2. **数据持久化**：容器内的数据存储在 `/opt/simpletrade/data` 目录，请定期备份此目录。

3. **日志管理**：部署日志存储在 `/opt/simpletrade/deploy/logs` 目录，可以使用logrotate管理日志文件大小。

4. **系统更新**：定期更新系统和Docker：
   ```bash
   sudo dnf update -y
   sudo dnf update -y docker-ce docker-ce-cli containerd.io
   ```

## 故障排除

### 问题1: Docker安装失败

**症状**：运行 `centos_setup.sh` 脚本时，Docker安装失败。

**解决方案**：
```bash
# 手动安装Docker
sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y --nobest docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

### 问题2: 容器无法启动

**症状**：运行 `local_deploy.sh --run` 时，容器无法启动。

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

### 问题3: 无法访问应用

**症状**：容器已启动，但无法通过浏览器访问应用。

**解决方案**：
```bash
# 检查容器是否正在运行
docker ps | grep simpletrade

# 检查端口是否已开放
sudo ss -tulpn | grep 80

# 检查防火墙是否已配置
sudo firewall-cmd --list-all

# 如果需要，开放HTTP端口
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

## 结论

通过本文档的指导，您应该能够在CentOS 8.5服务器上成功部署SimpleTrade应用。这个部署方案提供了前后端一体化部署和可视化发布流程，简化了应用的管理和更新。

如果您在部署过程中遇到任何问题，请参考故障排除部分或联系技术支持团队获取帮助。

---

**文档版本**: 1.0  
**最后更新**: 2023年11月15日  
**适用环境**: CentOS 8.5 64位  
**文档作者**: SimpleTrade团队
