#!/bin/bash

# 部署脚本
# 用法: ./deploy.sh [version]

# 设置变量
REPO_DIR="/Users/chengzheng/workspace/trade/simpletrade"
DOCKER_IMAGE="simpletrade"
CONTAINER_NAME="simpletrade"
LOG_FILE="$REPO_DIR/deploy/logs/deploy_$(date +%Y%m%d_%H%M%S).log"

# 确保日志目录存在
mkdir -p "$REPO_DIR/deploy/logs"

# 记录部署开始
echo "===== 部署开始 $(date) =====" | tee -a "$LOG_FILE"

# 如果提供了版本参数，则使用该版本
if [ -n "$1" ]; then
    VERSION="$1"
    echo "使用指定版本: $VERSION" | tee -a "$LOG_FILE"
else
    VERSION="latest"
    echo "使用默认版本: $VERSION" | tee -a "$LOG_FILE"
fi

# 构建 Docker 镜像
echo "开始构建 Docker 镜像..." | tee -a "$LOG_FILE"
cd "$REPO_DIR"
docker build -t "$DOCKER_IMAGE:$VERSION" -f deploy/Dockerfile . --build-arg VERSION="$VERSION" 2>&1 | tee -a "$LOG_FILE"

# 检查构建是否成功
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "Docker 镜像构建失败!" | tee -a "$LOG_FILE"
    exit 1
fi

# 停止并移除旧容器
echo "停止并移除旧容器..." | tee -a "$LOG_FILE"
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

# 启动新容器
echo "启动新容器..." | tee -a "$LOG_FILE"
docker run -d --name "$CONTAINER_NAME" \
    -p 80:80 \
    -e VERSION="$VERSION" \
    -v "$REPO_DIR/deploy/logs:/app/logs" \
    "$DOCKER_IMAGE:$VERSION" 2>&1 | tee -a "$LOG_FILE"

# 检查容器是否成功启动
if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "容器启动失败!" | tee -a "$LOG_FILE"
    exit 1
fi

# 记录部署结束
echo "===== 部署完成 $(date) =====" | tee -a "$LOG_FILE"
echo "容器 ID: $(docker ps -q -f name=$CONTAINER_NAME)" | tee -a "$LOG_FILE"
echo "访问地址: http://localhost" | tee -a "$LOG_FILE"
echo "部署面板: http://localhost/deploy/" | tee -a "$LOG_FILE"
echo "部署日志: http://localhost/deploy/logs/" | tee -a "$LOG_FILE"

# 输出部署日志路径
echo "部署日志已保存到: $LOG_FILE"
