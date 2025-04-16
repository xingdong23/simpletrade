#!/bin/bash

# 确保脚本在项目根目录运行
cd "$(dirname "$0")"

# 如果 .env 文件不存在，复制 .env.example
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example"
  cp .env.example .env
fi

# 启动 Docker 容器
# 尝试使用 docker-compose 命令
if command -v docker-compose &> /dev/null; then
  docker-compose up --build
# 如果不可用，尝试使用 docker compose 命令
elif command -v docker &> /dev/null; then
  docker compose build
  docker compose up
else
  echo "Error: Neither docker-compose nor docker compose commands are available."
  exit 1
fi
