#!/bin/bash
# 部署脚本 - 用于在容器内部执行部署操作

# 设置变量
REPO_DIR="/app"
LOG_DIR="/app/logs"
VERSION="$1"
DEPLOY_LOG="$LOG_DIR/deploy_$(date +%Y%m%d_%H%M%S).log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 记录部署开始
echo "===== 部署开始: $(date) =====" | tee -a "$DEPLOY_LOG"
echo "部署版本: $VERSION" | tee -a "$DEPLOY_LOG"

# 进入仓库目录
cd "$REPO_DIR" || {
    echo "错误: 无法进入仓库目录 $REPO_DIR" | tee -a "$DEPLOY_LOG"
    exit 1
}

# 保存当前分支
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "当前分支: $CURRENT_BRANCH" | tee -a "$DEPLOY_LOG"

# 拉取最新代码
echo "拉取最新代码..." | tee -a "$DEPLOY_LOG"
git fetch --all 2>&1 | tee -a "$DEPLOY_LOG"

# 检出指定版本
echo "检出版本: $VERSION" | tee -a "$DEPLOY_LOG"
git checkout "$VERSION" 2>&1 | tee -a "$DEPLOY_LOG"

# 拉取最新更改
echo "拉取最新更改..." | tee -a "$DEPLOY_LOG"
git pull 2>&1 | tee -a "$DEPLOY_LOG"

# 记录当前提交信息
COMMIT=$(git rev-parse --short HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)
echo "当前提交: $COMMIT" | tee -a "$DEPLOY_LOG"
echo "提交信息: $COMMIT_MSG" | tee -a "$DEPLOY_LOG"

# 构建前端
echo "构建前端..." | tee -a "$DEPLOY_LOG"
cd "$REPO_DIR/web-frontend" || {
    echo "错误: 无法进入前端目录" | tee -a "$DEPLOY_LOG"
    exit 1
}

npm install --legacy-peer-deps 2>&1 | tee -a "$DEPLOY_LOG"
npm run build 2>&1 | tee -a "$DEPLOY_LOG"

# 复制前端构建结果
echo "复制前端构建结果..." | tee -a "$DEPLOY_LOG"
rm -rf "$REPO_DIR/frontend"/*
mkdir -p "$REPO_DIR/frontend"
cp -r dist/* "$REPO_DIR/frontend/"

# 构建后端
echo "构建后端..." | tee -a "$DEPLOY_LOG"
cd "$REPO_DIR/backend" || {
    echo "错误: 无法进入后端目录" | tee -a "$DEPLOY_LOG"
    exit 1
}

pip install -r requirements.txt 2>&1 | tee -a "$DEPLOY_LOG"

# 重启服务
echo "重启服务..." | tee -a "$DEPLOY_LOG"

# 保存版本信息
echo "$VERSION" > "$REPO_DIR/panel/version.txt"
date "+%Y-%m-%d %H:%M:%S" > "$REPO_DIR/panel/deploy_time.txt"

# 重启Nginx
echo "重启Nginx..." | tee -a "$DEPLOY_LOG"
nginx -s reload 2>&1 | tee -a "$DEPLOY_LOG"

# 重启后端服务
echo "重启后端服务..." | tee -a "$DEPLOY_LOG"
pkill -f "python3.9 -m simpletrade.main" || true
cd "$REPO_DIR/backend"
python3.9 -m simpletrade.main > "$LOG_DIR/backend.log" 2>&1 &

# 记录部署完成
echo "===== 部署完成: $(date) =====" | tee -a "$DEPLOY_LOG"
echo "部署日志: $DEPLOY_LOG" | tee -a "$DEPLOY_LOG"

exit 0
