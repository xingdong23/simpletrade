#!/bin/bash

# 检测系统环境
echo "Checking system environment..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "Detected OS: $NAME $VERSION_ID"
fi

# 创建基本认证用户
if [ ! -f /etc/nginx/.htpasswd ]; then
    echo "Creating basic auth user..."
    echo "admin:$(openssl passwd -apr1 admin123)" > /etc/nginx/.htpasswd
fi

# 记录当前版本
if [ -n "$VERSION" ]; then
    echo "$VERSION" > /app/panel/version.txt
else
    echo "unknown" > /app/panel/version.txt
fi

# 记录部署时间
date > /app/panel/deploy_time.txt

# 创建部署脚本
cat > /app/deploy.sh << 'EOF'
#!/bin/bash

# 部署脚本
# 用法: ./deploy.sh [version]

# 记录部署开始
LOG_FILE="/app/logs/deploy_$(date +%Y%m%d_%H%M%S).log"
echo "===== 部署开始 $(date) =====" | tee -a "$LOG_FILE"

# 如果提供了版本参数，则使用该版本
if [ -n "$1" ]; then
    VERSION="$1"
    echo "使用指定版本: $VERSION" | tee -a "$LOG_FILE"
else
    VERSION="latest"
    echo "使用默认版本: $VERSION" | tee -a "$LOG_FILE"
fi

# 更新版本信息
echo "$VERSION" > /app/panel/version.txt
date > /app/panel/deploy_time.txt

echo "===== 部署完成 $(date) =====" | tee -a "$LOG_FILE"
echo "当前版本: $VERSION" | tee -a "$LOG_FILE"
EOF

chmod +x /app/deploy.sh

# 创建日志目录
mkdir -p /app/logs

# 启动部署API服务器
echo "Starting deployment API server..."
python3.9 /app/panel/deploy.py > /app/logs/deploy_panel.log 2>&1 &

# 启动后端服务
echo "Starting backend service..."
cd /app/backend
python3.9 -m simpletrade.main > /app/logs/backend.log 2>&1 &

# 创建前端日志的符号链接
ln -sf /var/log/nginx/access.log /app/logs/frontend_access.log
ln -sf /var/log/nginx/error.log /app/logs/frontend_error.log

# 创建部署面板的符号链接
# 这是为了解决Nginx配置问题，确保/deploy/路径可访问
mkdir -p /usr/share/nginx/html/deploy
ln -sf /app/panel/* /usr/share/nginx/html/deploy/

# 启动 Nginx
echo "Starting Nginx..."
nginx -g "daemon off;"
