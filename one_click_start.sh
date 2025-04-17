#!/bin/bash

# SimpleTrade 一键启动脚本
# 这个脚本会检查Docker是否安装，如果没有安装则提示安装
# 然后启动所有服务

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

# 检查Docker是否安装
check_docker() {
  print_message "检查Docker是否安装..."
  if ! command -v docker &> /dev/null; then
    print_error "Docker未安装。请先安装Docker。"
    print_message "您可以访问 https://docs.docker.com/get-docker/ 获取安装指南。"
    exit 1
  fi
  print_success "Docker已安装。"

  print_message "检查Docker Compose是否安装..."
  if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose未安装。请先安装Docker Compose。"
    print_message "您可以访问 https://docs.docker.com/compose/install/ 获取安装指南。"
    exit 1
  fi
  print_success "Docker Compose已安装。"
}

# 检查是否有足够的磁盘空间
check_disk_space() {
  print_message "检查磁盘空间..."

  # 获取当前目录所在磁盘的可用空间（以KB为单位）
  available_space=$(df -k . | awk 'NR==2 {print $4}')

  # 转换为GB
  available_space_gb=$(echo "scale=2; $available_space / 1024 / 1024" | bc)

  # 检查是否有至少5GB的可用空间
  if (( $(echo "$available_space_gb < 5" | bc -l) )); then
    print_warning "磁盘空间不足。建议至少有5GB的可用空间，当前只有${available_space_gb}GB。"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      print_message "操作已取消。"
      exit 0
    fi
  else
    print_success "磁盘空间充足，当前有${available_space_gb}GB可用空间。"
  fi
}

# 创建.env文件（如果不存在）
create_env_file() {
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
}

# 创建必要的目录
create_directories() {
  print_message "创建必要的目录..."
  mkdir -p data logs configs notebooks mysql-init docker_scripts
  print_success "目录已创建。"
}

# 启动服务
start_services() {
  print_message "启动SimpleTrade服务..."

  # 检查是否有正在运行的容器
  if docker ps | grep -q "simpletrade"; then
    print_warning "检测到SimpleTrade容器已经在运行。"
    read -p "是否停止现有容器并重新启动？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      print_message "停止现有容器..."
      docker-compose down
    else
      print_message "操作已取消。"
      exit 0
    fi
  fi

  # 启动服务
  print_message "构建并启动服务..."
  docker-compose up -d

  # 检查服务是否成功启动
  if [ $? -eq 0 ]; then
    print_success "SimpleTrade服务已成功启动！"
  else
    print_error "启动服务时出错。请检查日志获取详细信息。"
    exit 1
  fi
}

# 显示服务信息
show_service_info() {
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
  echo "  docker-compose ps"
  echo
  echo "您可以使用以下命令查看容器日志："
  echo "  docker-compose logs api"
  echo "  docker-compose logs frontend"
  echo "  docker-compose logs mysql"
  echo "  docker-compose logs jupyter"
  echo
  echo "您可以使用以下命令停止服务："
  echo "  docker-compose down"
  echo "--------------------------------------"
}

# 主函数
main() {
  echo "========================================"
  echo "     SimpleTrade 一键启动脚本"
  echo "========================================"
  echo

  # 检查Docker
  check_docker

  # 检查磁盘空间
  check_disk_space

  # 创建.env文件
  create_env_file

  # 创建必要的目录
  create_directories

  # 启动服务
  start_services

  # 显示服务信息
  show_service_info

  echo
  print_success "SimpleTrade已成功启动！"
  echo "========================================"
}

# 执行主函数
main
