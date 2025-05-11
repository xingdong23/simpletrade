# SimpleTrade 部署

本目录包含SimpleTrade应用的部署相关文件。

## CentOS 8.5 部署

如果您使用的是CentOS 8.5环境，请参阅[CentOS 8.5 部署指南](./CentOS_8.5_部署指南.md)获取详细的部署步骤。

## 快速开始

```bash
# 设置环境（只需执行一次）
sudo ./scripts/centos_setup.sh --all

# 构建和运行应用
./scripts/deploy_centos8.sh --build --run
```

## 目录结构

```
deploy/
├── CentOS_8.5_部署指南.md              # 详细的部署指南
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
