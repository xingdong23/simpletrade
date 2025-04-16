#!/bin/bash

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
  echo "5. 重置数据库："
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
  echo "=================================================================="
  echo ""
}

# 启动 Docker 容器
# 尝试使用 docker-compose 命令
if command -v docker-compose &> /dev/null; then
  # 使用 trap 来捕获 SIGINT 信号（Ctrl+C）
  trap 'print_common_operations' SIGINT
  docker-compose up --build
  # 如果正常退出（不是通过 Ctrl+C），也打印常用操作
  print_common_operations
# 如果不可用，尝试使用 docker compose 命令
elif command -v docker &> /dev/null; then
  trap 'print_common_operations' SIGINT
  docker compose build
  docker compose up
  print_common_operations
else
  echo "Error: Neither docker-compose nor docker compose commands are available."
  exit 1
fi
