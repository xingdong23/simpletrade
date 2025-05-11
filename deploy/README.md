# SimpleTrade 一体化部署系统

这个部署系统提供了一种简单的方式来部署 SimpleTrade 应用，包括前端和后端组件。它使用 Docker 容器化技术将前后端打包为一个整体，并提供了一个简单的 Web 界面来管理部署。

## 系统组件

1. **Docker 容器**：包含前端、后端和部署面板
2. **Nginx**：作为反向代理，将请求分发到前端、后端和部署 API
3. **部署面板**：一个简单的 Web 界面，用于管理部署
4. **部署 API**：处理部署请求的 Python API 服务器

## 目录结构

```
deploy/
├── Dockerfile          # Docker 构建文件
├── README.md           # 本文档
├── config/             # 配置文件
│   └── nginx.conf      # Nginx 配置
├── panel/              # 部署面板
│   ├── deploy.py       # 部署 API 服务器
│   └── index.html      # 部署面板 Web 界面
└── scripts/            # 脚本
    └── start.sh        # 容器启动脚本
```

## 使用方法

### CentOS 8.5 环境设置

如果您使用的是 CentOS 8.5 服务器，我们提供了一个专门的设置脚本：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/centos_setup.sh

# 运行设置脚本，执行所有操作
sudo ./deploy/scripts/centos_setup.sh --all
```

这个脚本会安装 Docker、配置 SELinux 和防火墙。

### 初始构建和部署

1. 确保已安装 Docker
2. 克隆项目代码
3. 使用提供的部署脚本：

```bash
# 给脚本添加执行权限
chmod +x deploy/scripts/local_deploy.sh

# 构建 Docker 镜像
./deploy/scripts/local_deploy.sh --build

# 运行容器
./deploy/scripts/local_deploy.sh --run

# 或者一步完成构建和运行
./deploy/scripts/local_deploy.sh --build --run
```

如果您想手动执行命令，也可以使用以下命令：

```bash
# 构建 Docker 镜像
docker build -t simpletrade:latest -f deploy/Dockerfile .

# 运行容器
docker run -d --name simpletrade -p 80:80 -v "$(pwd)/deploy/logs:/app/logs" -v "$(pwd)/data:/app/data" simpletrade:latest
```

### 访问应用

- **前端应用**：http://localhost/
- **部署面板**：http://localhost/deploy/
  - 用户名：admin
  - 密码：admin123

### 部署新版本

1. 访问部署面板
2. 输入要部署的版本标识（分支名、标签名或提交哈希）
3. 点击"开始部署"按钮
4. 确认部署
5. 等待部署完成
6. 查看部署日志

## 注意事项

### 通用注意事项

1. **安全性**：部署面板使用基本认证保护，但在生产环境中应该使用更强的安全措施
2. **数据持久化**：容器重启后，数据库数据将丢失，应该使用数据卷或外部数据库
3. **日志管理**：部署日志会保存在容器内的 `/app/logs` 目录，可以使用数据卷将其映射到主机
4. **HTTPS**：在生产环境中，应该配置 SSL 证书以启用 HTTPS

### CentOS 8.5 特有注意事项

1. **SELinux**：如果遇到权限问题，可能是由于 SELinux 的限制。可以使用以下命令临时禁用 SELinux：
   ```bash
   sudo setenforce 0
   ```
   或者永久禁用（需要重启）：
   ```bash
   sudo sed -i 's/^SELINUX=enforcing$/SELINUX=disabled/' /etc/selinux/config
   sudo reboot
   ```

2. **防火墙**：CentOS 8.5 默认使用 firewalld 作为防火墙。确保已经开放 HTTP 端口：
   ```bash
   sudo firewall-cmd --permanent --add-service=http
   sudo firewall-cmd --reload
   ```

3. **系统限制**：如果遇到系统限制相关的问题，可以调整以下设置：
   ```bash
   echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
   echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
   sudo sysctl -p
   ```

4. **CentOS 8 生命周期**：CentOS 8 已于 2021 年底结束支持，建议考虑升级到 CentOS Stream 8 或迁移到 Rocky Linux/AlmaLinux。

## 自定义

### 修改认证信息

默认的用户名和密码是 `admin` / `admin123`。要修改它们，可以编辑 `start.sh` 脚本中的相关部分。

### 添加更多功能

可以根据需要扩展部署面板和 API，例如：

- 添加回滚功能
- 添加数据库迁移功能
- 添加监控功能
- 添加多环境支持（开发、测试、生产）

## 故障排除

### 容器无法启动

检查 Docker 日志：

```bash
docker logs simpletrade
```

### 部署失败

查看部署日志：

1. 访问部署面板
2. 在右侧的日志部分选择最新的日志文件
3. 查看详细错误信息

### API 无法访问

检查 Nginx 日志：

```bash
docker exec simpletrade cat /var/log/nginx/error.log
```
