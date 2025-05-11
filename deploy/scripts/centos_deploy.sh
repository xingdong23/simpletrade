#!/bin/bash

# CentOS 8.5专用部署脚本
# 用于在网络受限的CentOS 8.5环境中部署SimpleTrade应用

# 设置变量
REPO_DIR="/opt/simpletrade"
DOCKER_IMAGE="simpletrade"
CONTAINER_NAME="simpletrade"

# 显示帮助信息
show_help() {
    echo "SimpleTrade CentOS 8.5专用部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -b, --build     构建Docker镜像"
    echo "  -r, --run       运行Docker容器"
    echo "  -s, --stop      停止Docker容器"
    echo "  -d, --delete    删除Docker容器"
    echo "  -h, --help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --build      # 构建Docker镜像"
    echo "  $0 --run        # 运行Docker容器"
    echo "  $0 --stop       # 停止Docker容器"
    echo "  $0 --delete     # 删除Docker容器"
    echo "  $0 -b -r        # 构建并运行"
    echo ""
}

# 构建Docker镜像
build_image() {
    echo "构建Docker镜像..."
    cd "$REPO_DIR"
    
    # 使用CentOS专用的Dockerfile
    docker build -t "$DOCKER_IMAGE:latest" -f deploy/Dockerfile.centos .
    
    if [ $? -eq 0 ]; then
        echo "Docker镜像构建成功!"
    else
        echo "Docker镜像构建失败!"
        exit 1
    fi
}

# 运行Docker容器
run_container() {
    echo "运行Docker容器..."
    
    # 检查容器是否已存在
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        echo "容器已存在，先停止并删除..."
        docker stop "$CONTAINER_NAME" > /dev/null 2>&1
        docker rm "$CONTAINER_NAME" > /dev/null 2>&1
    fi
    
    # 创建日志目录
    mkdir -p "$REPO_DIR/deploy/logs"
    
    # 创建数据目录
    mkdir -p "$REPO_DIR/data"
    
    # 运行容器
    docker run -d --name "$CONTAINER_NAME" \
        -p 80:80 \
        -v "$REPO_DIR/deploy/logs:/app/logs" \
        -v "$REPO_DIR/data:/app/data" \
        --security-opt label=disable \
        "$DOCKER_IMAGE:latest"
    
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
        exit 1
    fi
}

# 停止Docker容器
stop_container() {
    echo "停止Docker容器..."
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
    docker rm "$CONTAINER_NAME"
    
    if [ $? -eq 0 ]; then
        echo "Docker容器已删除!"
    else
        echo "Docker容器删除失败!"
        exit 1
    fi
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

exit 0
