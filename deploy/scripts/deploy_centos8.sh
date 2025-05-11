#!/bin/bash

# CentOS 8.5 优雅部署脚本
# 用于在网络受限的CentOS 8.5环境中部署SimpleTrade应用
# 使用预先加载的Docker镜像，避免从Docker Hub拉取

# 设置变量
REPO_DIR="/opt/simpletrade"
DOCKER_IMAGE="simpletrade"
CONTAINER_NAME="simpletrade"
LOG_DIR="$REPO_DIR/deploy/logs"
DATA_DIR="$REPO_DIR/data"

# 显示帮助信息
show_help() {
    echo "SimpleTrade CentOS 8.5 优雅部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -b, --build     构建Docker镜像"
    echo "  -r, --run       运行Docker容器"
    echo "  -s, --stop      停止Docker容器"
    echo "  -d, --delete    删除Docker容器"
    echo "  -l, --logs      查看容器日志"
    echo "  -h, --help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --build      # 构建Docker镜像"
    echo "  $0 --run        # 运行Docker容器"
    echo "  $0 --stop       # 停止Docker容器"
    echo "  $0 --delete     # 删除Docker容器"
    echo "  $0 -b -r        # 构建并运行"
    echo "  $0 --logs       # 查看容器日志"
    echo ""
}

# 检查Docker是否已安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "错误: Docker未安装。请先安装Docker。"
        echo "可以使用以下命令安装Docker:"
        echo "  sudo ./deploy/scripts/centos_setup.sh --all"
        exit 1
    fi
}

# 检查基础镜像是否已加载
check_base_images() {
    echo "检查基础镜像..."
    
    # 检查CentOS 8镜像
    if ! docker images | grep -q "centos.*8"; then
        echo "警告: 未找到CentOS 8镜像。"
        echo "将尝试从本地仓库拉取..."
        
        # 尝试拉取CentOS 8镜像
        docker pull centos:8 || {
            echo "错误: 无法拉取CentOS 8镜像。"
            echo "请确保已加载CentOS 8镜像或配置了可用的镜像源。"
            exit 1
        }
    else
        echo "已找到CentOS 8镜像。"
    fi
}

# 构建Docker镜像
build_image() {
    echo "构建Docker镜像..."
    
    # 检查Docker和基础镜像
    check_docker
    check_base_images
    
    # 创建日志目录
    mkdir -p "$LOG_DIR"
    
    # 记录构建开始
    BUILD_LOG="$LOG_DIR/build_$(date +%Y%m%d_%H%M%S).log"
    echo "===== 构建开始 $(date) =====" | tee -a "$BUILD_LOG"
    
    # 构建Docker镜像
    cd "$REPO_DIR"
    docker build -t "$DOCKER_IMAGE:latest" -f deploy/Dockerfile.centos . 2>&1 | tee -a "$BUILD_LOG"
    
    # 检查构建结果
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "===== 构建成功 $(date) =====" | tee -a "$BUILD_LOG"
        echo "Docker镜像构建成功!"
    else
        echo "===== 构建失败 $(date) =====" | tee -a "$BUILD_LOG"
        echo "Docker镜像构建失败!"
        echo "请查看构建日志: $BUILD_LOG"
        exit 1
    fi
}

# 运行Docker容器
run_container() {
    echo "运行Docker容器..."
    
    # 检查Docker
    check_docker
    
    # 检查镜像是否存在
    if ! docker images | grep -q "$DOCKER_IMAGE"; then
        echo "错误: 未找到镜像 $DOCKER_IMAGE。请先构建镜像。"
        echo "  $0 --build"
        exit 1
    fi
    
    # 检查容器是否已存在
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        echo "容器已存在，先停止并删除..."
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1
    fi
    
    # 创建日志和数据目录
    mkdir -p "$LOG_DIR" "$DATA_DIR"
    
    # 运行容器
    docker run -d --name "$CONTAINER_NAME" \
        -p 80:80 \
        -v "$LOG_DIR:/app/logs" \
        -v "$DATA_DIR:/app/data" \
        --security-opt label=disable \
        "$DOCKER_IMAGE:latest"
    
    # 检查运行结果
    if [ $? -eq 0 ]; then
        # 获取服务器IP地址
        SERVER_IP=$(hostname -I | awk '{print $1}')
        
        echo "Docker容器启动成功!"
        echo "访问地址: http://$SERVER_IP"
        echo "部署面板: http://$SERVER_IP/deploy/"
        echo "  用户名: admin"
        echo "  密码: admin123"
    else
        echo "Docker容器启动失败!"
        echo "请检查Docker日志:"
        echo "  docker logs $CONTAINER_NAME"
        exit 1
    fi
}

# 停止Docker容器
stop_container() {
    echo "停止Docker容器..."
    
    # 检查Docker
    check_docker
    
    # 检查容器是否存在
    if ! docker ps -a | grep -q "$CONTAINER_NAME"; then
        echo "容器 $CONTAINER_NAME 不存在。"
        exit 0
    fi
    
    # 停止容器
    docker stop "$CONTAINER_NAME"
    
    if [ $? -eq 0 ]; then
        echo "Docker容器已停止!"
    else
        echo "Docker容器停止失败!"
        exit 1
    fi
}

# 删除Docker容器
delete_container() {
    echo "删除Docker容器..."
    
    # 检查Docker
    check_docker
    
    # 检查容器是否存在
    if ! docker ps -a | grep -q "$CONTAINER_NAME"; then
        echo "容器 $CONTAINER_NAME 不存在。"
        exit 0
    fi
    
    # 停止容器（如果正在运行）
    if docker ps | grep -q "$CONTAINER_NAME"; then
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1
    fi
    
    # 删除容器
    docker rm "$CONTAINER_NAME"
    
    if [ $? -eq 0 ]; then
        echo "Docker容器已删除!"
    else
        echo "Docker容器删除失败!"
        exit 1
    fi
}

# 查看容器日志
view_logs() {
    echo "查看容器日志..."
    
    # 检查Docker
    check_docker
    
    # 检查容器是否存在
    if ! docker ps -a | grep -q "$CONTAINER_NAME"; then
        echo "容器 $CONTAINER_NAME 不存在。"
        exit 1
    fi
    
    # 查看日志
    docker logs -f "$CONTAINER_NAME"
}

# 处理命令行参数
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

BUILD=false
RUN=false
STOP=false
DELETE=false
LOGS=false

while [ "$1" != "" ]; do
    case $1 in
        -b | --build )    BUILD=true
                          ;;
        -r | --run )      RUN=true
                          ;;
        -s | --stop )     STOP=true
                          ;;
        -d | --delete )   DELETE=true
                          ;;
        -l | --logs )     LOGS=true
                          ;;
        -h | --help )     show_help
                          exit 0
                          ;;
        * )               show_help
                          exit 1
    esac
    shift
done

# 执行操作
if [ "$BUILD" = true ]; then
    build_image
fi

if [ "$STOP" = true ]; then
    stop_container
fi

if [ "$DELETE" = true ]; then
    delete_container
fi

if [ "$RUN" = true ]; then
    run_container
fi

if [ "$LOGS" = true ]; then
    view_logs
fi

exit 0
