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

# 删除ta-lib相关文件
echo "Removing ta-lib related files..."
rm -rf /app/logs/ta-lib /app/logs/ta-lib-0.4.0-src.tar.gz

# 启动部署API服务器
echo "Starting deployment API server..."
python3 /app/panel/deploy.py > /app/logs/deploy_panel.log 2>&1 &

# 启动部署处理服务器
echo "Starting deployment handler server..."
python3 /app/panel/deploy_handler.py > /app/logs/deploy_handler.log 2>&1 &

# 启动后端服务
echo "Starting backend service..."
cd /app/backend

# 检查vnpy_custom目录是否存在
if [ ! -d "/app/backend/vnpy_custom" ]; then
    echo "Error: vnpy_custom directory does not exist!"
    exit 1
fi

# 添加vnpy_custom目录到Python路径
echo "Adding vnpy_custom to Python path..."
cat > /app/backend/simpletrade/__init__.py << 'EOF'
"""
SimpleTrade - 一个简单的交易系统
"""

# 修复numpy.NaN问题
import numpy as np
import sys

# 如果numpy没有NaN属性，添加它
if not hasattr(np, 'NaN'):
    np.NaN = np.nan

# 设置版本号
__version__ = "0.1.0"

# 添加vnpy源码路径
from pathlib import Path

# 添加vnpy源码目录到Python路径
VNPY_CUSTOM_DIR = Path(__file__).parent.parent / "vnpy_custom"
if VNPY_CUSTOM_DIR.exists() and str(VNPY_CUSTOM_DIR) not in sys.path:
    sys.path.insert(0, str(VNPY_CUSTOM_DIR))
    print(f"Added vnpy_custom to sys.path: {VNPY_CUSTOM_DIR}")

# 设置日志格式
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
EOF

# 启动后端服务
echo "Starting backend service..."
python3 -m simpletrade.main > /app/logs/backend.log 2>&1 &

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
