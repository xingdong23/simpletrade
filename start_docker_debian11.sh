#!/bin/bash

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
  echo -e "${BLUE}[SimpleTrade]${NC} $1"
}

print_success() {
  echo -e "${GREEN}[成功]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
  echo -e "${RED}[错误]${NC} $1"
}

# 确保脚本在项目根目录运行
cd "$(dirname "$0")"

# 如果.env文件不存在，复制.env.example
if [ ! -f .env ]; then
  print_message "创建.env文件..."
  cp .env.example .env 2>/dev/null || {
    cat > .env << EOF
SIMPLETRADE_DB_USER=root
SIMPLETRADE_DB_PASSWORD=Cz159csa
SIMPLETRADE_DB_NAME=simpletrade
SIMPLETRADE_API_PORT=8003
EOF
  }
  print_success ".env文件已创建。"
else
  print_message ".env文件已存在，跳过创建。"
fi

# 创建必要的目录
print_message "创建必要的目录..."
mkdir -p data logs configs notebooks mysql-init docker_scripts
print_success "目录已创建。"

# 检查是否有正在运行的容器
if docker ps | grep -q "simpletrade"; then
  print_warning "检测到SimpleTrade容器已经在运行。"
  read -p "是否停止现有容器并重新启动？(y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_message "停止现有容器..."
    docker-compose -f docker-compose.debian11.yml down
  else
    print_message "操作已取消。"
    exit 0
  fi
fi

# 清理Docker缓存
print_message "清理Docker缓存..."
docker system prune -f > /dev/null 2>&1

# 启动服务
print_message "使用Debian 11基础镜像构建并启动服务..."

# 先启动MySQL服务
print_message "启动MySQL服务..."
docker-compose -f docker-compose.debian11.yml up -d mysql

# 等待MySQL服务启动
print_message "等待MySQL服务启动..."
sleep 10

# 构建并启动前端服务
print_message "启动前端服务..."
docker-compose -f docker-compose.debian11.yml up -d frontend

# 构建并启动API服务
print_message "构建并启动API服务..."
docker-compose -f docker-compose.debian11.yml build --no-cache api
docker-compose -f docker-compose.debian11.yml up -d api

# 构建并启动Jupyter服务
print_message "构建并启动Jupyter服务..."
docker-compose -f docker-compose.debian11.yml build --no-cache jupyter
docker-compose -f docker-compose.debian11.yml up -d jupyter

# 检查服务是否成功启动
if [ $? -eq 0 ]; then
  print_success "SimpleTrade服务已成功启动！"
  
  # 显示服务信息
  print_message "服务信息："
  echo "--------------------------------------"
  echo "API服务: http://localhost:8003"
  echo "API文档: http://localhost:8003/docs"
  echo "前端界面: http://localhost:8080"
  echo "Jupyter Notebook: http://localhost:8888 (用于数据分析和策略开发)"
  echo "MySQL数据库: localhost:3306"
  echo "  - 用户名: root"
  echo "  - 密码: Cz159csa (可在.env文件中修改)"
  echo "  - 数据库名: simpletrade"
  echo "--------------------------------------"
  echo
  echo "您可以使用以下命令查看容器状态："
  echo "  docker-compose -f docker-compose.debian11.yml ps"
  echo
  echo "您可以使用以下命令查看容器日志："
  echo "  docker-compose -f docker-compose.debian11.yml logs api"
  echo "  docker-compose -f docker-compose.debian11.yml logs frontend"
  echo "  docker-compose -f docker-compose.debian11.yml logs mysql"
  echo "  docker-compose -f docker-compose.debian11.yml logs jupyter"
  echo
  echo "您可以使用以下命令停止服务："
  echo "  docker-compose -f docker-compose.debian11.yml down"
  echo "--------------------------------------"
else
  print_error "启动服务时出错。请检查日志获取详细信息。"
  exit 1
fi
