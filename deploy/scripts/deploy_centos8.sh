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

# 配置阴镜像加速器
configure_mirror() {
    echo "检查镜像加速器配置..."

    # 检查是否已配置镜像加速器
    if [ ! -f /etc/docker/daemon.json ] || ! grep -q "registry-mirrors" /etc/docker/daemon.json; then
        echo "未找到镜像加速器配置，正在配置阿里云镜像加速器..."

        # 创建daemon.json文件
        sudo mkdir -p /etc/docker

        # 如果文件已存在，先备份
        if [ -f /etc/docker/daemon.json ]; then
            sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak
            echo "原有配置已备份为 /etc/docker/daemon.json.bak"

            # 如果文件已存在但不包含 registry-mirrors，则添加
            if ! grep -q "registry-mirrors" /etc/docker/daemon.json; then
                # 使用jq工具合并JSON（如果安装了jq）
                if command -v jq &> /dev/null; then
                    sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.tmp
                    jq '. + {"registry-mirrors": ["https://qoy9ouh4.mirror.aliyuncs.com"]}' /etc/docker/daemon.json.tmp | sudo tee /etc/docker/daemon.json > /dev/null
                    sudo rm -f /etc/docker/daemon.json.tmp
                else
                    # 如果没有jq，则直接覆盖
                    sudo tee /etc/docker/daemon.json > /dev/null << EOF
{
  "registry-mirrors": ["https://qoy9ouh4.mirror.aliyuncs.com"]
}
EOF
                fi
            fi
        else
            # 创建新的daemon.json文件
            sudo tee /etc/docker/daemon.json > /dev/null << EOF
{
  "registry-mirrors": ["https://qoy9ouh4.mirror.aliyuncs.com"]
}
EOF
        fi

        # 重启Docker服务
        echo "重启Docker服务以应用镜像加速器配置..."
        sudo systemctl daemon-reload
        sudo systemctl restart docker

        # 等待Docker服务重启
        sleep 3

        # 检查Docker服务状态
        if ! systemctl is-active --quiet docker; then
            echo "错误: Docker服务重启失败。请手动检查配置。"
            exit 1
        fi

        echo "阿里云镜像加速器配置成功。"
    else
        echo "镜像加速器已配置。"
    fi
}

# 配置CentOS 8软件源
configure_centos_repos() {
    echo "检查CentOS 8软件源配置..."

    # 创建一个临时脚本来配置CentOS 8软件源
    cat > /tmp/configure_centos_repos.sh << 'EOF'
#!/bin/bash

# 备份原始的repo文件
mkdir -p /etc/yum.repos.d/backup
cp /etc/yum.repos.d/CentOS-* /etc/yum.repos.d/backup/ 2>/dev/null || true

# 移除原有的repo文件
rm -f /etc/yum.repos.d/CentOS-*.repo

# 创建新的Base仓库文件
cat > /etc/yum.repos.d/CentOS-Base.repo << 'REPO'
[base]
name=CentOS-$releasever - Base - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/BaseOS/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[updates]
name=CentOS-$releasever - Updates - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/BaseOS/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[extras]
name=CentOS-$releasever - Extras - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/extras/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[centosplus]
name=CentOS-$releasever - Plus - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/centosplus/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[PowerTools]
name=CentOS-$releasever - PowerTools - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/PowerTools/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[AppStream]
name=CentOS-$releasever - AppStream - mirrors.aliyun.com
failovermethod=priority
baseurl=https://mirrors.aliyun.com/centos-vault/8.5.2111/AppStream/x86_64/os/
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official
REPO

# 创建 EPEL 仓库文件
cat > /etc/yum.repos.d/epel.repo << 'REPO'
[epel]
name=Extra Packages for Enterprise Linux $releasever - $basearch
baseurl=https://mirrors.aliyun.com/epel/8/Everything/x86_64/
enabled=1
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/epel/RPM-GPG-KEY-EPEL-8

[epel-debuginfo]
name=Extra Packages for Enterprise Linux $releasever - $basearch - Debug
baseurl=https://mirrors.aliyun.com/epel/8/Everything/x86_64/debug/
enabled=0
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/epel/RPM-GPG-KEY-EPEL-8

[epel-source]
name=Extra Packages for Enterprise Linux $releasever - $basearch - Source
baseurl=https://mirrors.aliyun.com/epel/8/Everything/source/tree/
enabled=0
gpgcheck=0
gpgkey=https://mirrors.aliyun.com/epel/RPM-GPG-KEY-EPEL-8
REPO

# 添加 hosts 条目以解决 DNS 问题
echo "199.232.28.133 raw.githubusercontent.com" >> /etc/hosts
echo "185.199.108.133 raw.github.com" >> /etc/hosts

# 清理缓存并重新生成
dnf clean all
dnf makecache

echo "CentOS 8软件源配置完成"
EOF

    chmod +x /tmp/configure_centos_repos.sh

    echo "已创建CentOS 8软件源配置脚本。该脚本将在构建过程中使用。"
}

# 检查基础镜像是否已加载
check_base_images() {
    echo "检查基础镜像..."

    # 检查CentOS 8镜像
    if ! docker images | grep -q "centos.*8"; then
        echo "警告: 未找到CentOS 8镜像。"
        echo "将尝试使用阿里云镜像加速器拉取..."

        # 先配置镜像加速器
        configure_mirror

        # 尝试拉取CentOS 8镜像
        docker pull centos:8 || {
            echo "错误: 即使使用阿里云镜像加速器仍无法拉取CentOS 8镜像。"
            echo "请确保网络连接正常或手动加载CentOS 8镜像。"
            exit 1
        }
    else
        echo "已找到CentOS 8镜像。"
    fi

    # 配置CentOS 8软件源
    configure_centos_repos
}

# 构建Docker镜像
build_image() {
    echo "构建Docker镜像..."

    # 检查Docker、配置镜像加速器和基础镜像
    check_docker
    configure_mirror
    check_base_images

    # 创建日志目录
    mkdir -p "$LOG_DIR"

    # 记录构建开始
    BUILD_LOG="$LOG_DIR/build_$(date +%Y%m%d_%H%M%S).log"
    echo "===== 构建开始 $(date) =====" | tee -a "$BUILD_LOG"

    # 复制CentOS 8软件源配置脚本到构建上下文
    cp /tmp/configure_centos_repos.sh "$REPO_DIR/configure_centos_repos.sh"

    # 构建Docker镜像
    cd "$REPO_DIR"
    docker build -t "$DOCKER_IMAGE:latest" \
        --build-arg CONFIGURE_REPOS_SCRIPT=./configure_centos_repos.sh \
        -f deploy/Dockerfile.centos . 2>&1 | tee -a "$BUILD_LOG"

    # 清理临时文件
    rm -f "$REPO_DIR/configure_centos_repos.sh"

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
        --dns 8.8.8.8 \
        --dns 114.114.114.114 \
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
