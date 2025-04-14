#!/bin/bash

# 确保脚本在项目根目录运行
cd "$(dirname "$0")"

# 启动 Docker 容器
docker compose up --build
