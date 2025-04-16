#!/bin/bash

# =================================================================
# SimpleTrade Docker 启动脚本
# 功能：
# 1. 检查容器是否已经在运行，避免重复启动
# 2. 清理悬空镜像和未使用的资源，减少磁盘空间占用
# 3. 启动 MySQL、API 和前端服务
# 4. 显示常用操作命令
# =================================================================

# 确保脚本在项目根目录运行
cd "$(dirname "$0")"

# 如果 .env 文件不存在，复制 .env.example
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example"
  cp .env.example .env
fi

# 打印启动信息
echo "=================================================================="
echo "                 SimpleTrade Docker 启动脚本                "
echo "=================================================================="

# 检查容器是否已经在运行
# 这可以避免重复启动容器，导致资源浪费
if docker ps | grep -q "simpletrade-api\|simpletrade-mysql\|simpletrade-frontend"; then
  echo "警告：SimpleTrade 容器已经在运行中。"
  echo "您可以使用以下命令查看正在运行的容器："
  echo "  docker ps"
  echo ""
  echo "如果您想停止现有容器并重新启动，请先运行："
  echo "  docker-compose down"
  echo ""
  read -p "是否停止现有容器并重新启动？(y/n) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "停止现有容器..."
    docker-compose down
  else
    echo "操作已取消。"
    exit 0
  fi
fi

# 清理悬空镜像和未使用的资源
# 这可以减少磁盘空间占用，避免磁盘空间不足
echo "清理悬空镜像和未使用的资源..."
echo "注意：这将删除未使用的镜像、容器和网络，但不会删除数据卷。"
read -p "是否继续？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # 清理悬空镜像
  echo "清理悬空镜像..."
  docker image prune -f

  # 清理未使用的容器
  echo "清理未使用的容器..."
  docker container prune -f

  # 清理未使用的网络
  echo "清理未使用的网络..."
  docker network prune -f

  echo "清理完成！"
else
  echo "跳过清理步骤。"
fi

echo "正在启动 SimpleTrade 的 Docker 容器，包括："
echo "- MySQL 数据库容器 (simpletrade-mysql)"
echo "- API 服务容器 (simpletrade-api)"
echo "- 前端服务容器 (simpletrade-frontend)"
echo ""
echo "启动完成后，可以访问："
echo "- API 文档：http://localhost:8003/docs"
echo "- 前端页面：http://localhost:8080"
echo "- MySQL 数据库：localhost:3306 (用户名：root，密码：Cz159csa)"
echo ""
echo "按 Ctrl+C 可以停止容器运行。"
echo "建议使用 docker-compose down 命令完全停止容器。"
echo "=================================================================="
echo ""

# 创建一个函数来打印常用操作
print_common_operations() {
  echo ""
  echo "=================================================================="
  echo "                   Docker 容器常用操作                   "
  echo "=================================================================="
  echo "1. 进入容器："
  echo "   docker exec -it simpletrade-mysql bash     # 进入 MySQL 容器"
  echo "   docker exec -it simpletrade-api bash       # 进入 API 容器"
  echo "   docker exec -it simpletrade-frontend bash  # 进入前端容器"
  echo ""
  echo "2. 连接到 MySQL 数据库："
  echo "   docker exec -it simpletrade-mysql mysql -uroot -pCz159csa simpletrade"
  echo ""
  echo "3. 查看容器日志："
  echo "   docker-compose logs mysql     # 查看 MySQL 日志"
  echo "   docker-compose logs api       # 查看 API 日志"
  echo "   docker-compose logs frontend  # 查看前端日志"
  echo "   docker-compose logs -f api    # 实时查看 API 日志"
  echo ""
  echo "4. 重启容器："
  echo "   docker restart simpletrade-mysql    # 重启 MySQL 容器"
  echo "   docker restart simpletrade-api      # 重启 API 容器"
  echo "   docker restart simpletrade-frontend # 重启前端容器"
  echo ""
  echo "5. 停止和重置："
  echo "   docker-compose down                      # 停止所有容器"
  echo "   docker volume rm simpletrade_mysql-data  # 删除数据库卷"
  echo "   ./start_docker.sh                        # 重新启动容器"
  echo ""
  echo "6. 在容器中执行命令："
  echo "   docker exec -it simpletrade-mysql mysql -uroot -pCz159csa -e \"SHOW TABLES FROM simpletrade;\""
  echo ""
  echo "7. 备份和恢复数据："
  echo "   docker exec simpletrade-mysql sh -c 'exec mysqldump -uroot -pCz159csa simpletrade' > backup.sql  # 备份"
  echo "   cat backup.sql | docker exec -i simpletrade-mysql mysql -uroot -pCz159csa simpletrade            # 恢复"
  echo ""
  echo "8. 清理 Docker 资源："
  echo "   docker system prune -f                   # 清理所有未使用的资源"
  echo "   docker image prune -a                    # 清理所有未使用的镜像"
  echo "   docker system df                         # 查看 Docker 磁盘使用情况"
  echo "=================================================================="
  echo ""
}

# 启动 Docker 容器
# 尝试使用 docker-compose 命令
if command -v docker-compose &> /dev/null; then
  # 使用 trap 来捕获 SIGINT 信号（Ctrl+C）
  trap 'print_common_operations' SIGINT
  # 使用 docker-compose up 启动容器
  # --build: 在启动容器前重新构建镜像
  # 不使用 -d 参数，以便在终端中显示日志
  docker-compose up --build
  # 如果正常退出（不是通过 Ctrl+C），也打印常用操作
  print_common_operations
# 如果不可用，尝试使用 docker compose 命令
elif command -v docker &> /dev/null; then
  trap 'print_common_operations' SIGINT
  # 使用 docker compose 命令（新版 Docker 的命令格式）
  docker compose build
  docker compose up
  print_common_operations
else
  echo "Error: Neither docker-compose nor docker compose commands are available."
  echo "Please install Docker and Docker Compose first."
  exit 1
fi
