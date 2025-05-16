#!/bin/bash

# CentOS 8.5 低内存环境优化部署脚本
# 适用于2核2GB内存的服务器
# 用于在网络受限的CentOS 8.5环境中部署SimpleTrade应用

# 设置变量
REPO_DIR="/opt/simpletrade"
DOCKER_IMAGE="simpletrade-lowmem"
CONTAINER_NAME="simpletrade"
LOG_DIR="$REPO_DIR/deploy/logs"
DATA_DIR="$REPO_DIR/data"

# 显示帮助信息
show_help() {
    echo "SimpleTrade CentOS 8.5 低内存环境优化部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -b, --build     构建Docker镜像"
    echo "  -r, --run       运行Docker容器"
    echo "  -s, --stop      停止Docker容器"
    echo "  -d, --delete    删除Docker容器"
    echo "  -c, --clean     清理系统缓存和Docker缓存"
    echo "  -w, --swap      创建交换文件（如果没有）"
    echo "  -l, --logs      查看容器日志"
    echo "  -h, --help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --clean --swap --build --run  # 清理缓存，创建交换文件，构建并运行"
    echo "  $0 --build                       # 构建Docker镜像"
    echo "  $0 --run                         # 运行Docker容器"
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

# 配置镜像加速器
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

# 清理系统缓存和Docker缓存
clean_cache() {
    echo "清理系统缓存和Docker缓存..."

    # 清理Docker缓存
    docker system prune -af

    # 清理系统缓存
    sudo sh -c "sync && echo 3 > /proc/sys/vm/drop_caches"

    echo "缓存清理完成。"
}

# 创建交换文件
create_swap() {
    echo "检查交换空间..."

    # 检查是否已有交换空间
    if [ "$(free | grep -i swap | awk '{print $2}')" -gt "0" ]; then
        echo "系统已有交换空间，无需创建。"
        return
    fi

    echo "未检测到交换空间，创建2GB交换文件..."

    # 创建2GB的交换文件
    sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile

    # 永久挂载交换文件
    if ! grep -q "/swapfile" /etc/fstab; then
        echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    fi

    echo "交换文件创建完成。"
}

# 构建Docker镜像
build_image() {
    echo "构建Docker镜像..."

    # 检查Docker和基础镜像
    check_docker
    configure_mirror
    check_base_images

    # 创建日志目录
    mkdir -p "$LOG_DIR"

    # 记录构建开始
    BUILD_LOG="$LOG_DIR/build_$(date +%Y%m%d_%H%M%S).log"
    echo "===== 构建开始 $(date) =====" | tee -a "$BUILD_LOG"

    # 前端路由问题已在代码仓库中直接修复

    # 复制CentOS 8软件源配置脚本到构建上下文
    cp /tmp/configure_centos_repos.sh "$REPO_DIR/configure_centos_repos.sh"

    # 创建低内存优化的Dockerfile
    cat > "$REPO_DIR/deploy/Dockerfile.lowmem" << 'EOF'
# 使用CentOS 8作为基础镜像
FROM centos:8
WORKDIR /app

# 添加构建参数
ARG CONFIGURE_REPOS_SCRIPT=configure_centos_repos.sh

# 复制配置脚本
COPY ${CONFIGURE_REPOS_SCRIPT} /tmp/configure_centos_repos.sh

# 配置CentOS 8的存储库（使用阿里云镜像源）
RUN chmod +x /tmp/configure_centos_repos.sh && \
    /tmp/configure_centos_repos.sh && \
    rm -f /tmp/configure_centos_repos.sh

# 安装必要的软件
RUN dnf clean all && \
    dnf makecache && \
    dnf install -y epel-release && \
    dnf install -y nginx curl procps net-tools vim wget git gcc gcc-c++ make zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel && \
    dnf module install -y nodejs:16 && \
    dnf clean all && \
    # 安装Python 3.10
    dnf install -y python3.10 python3.10-devel python3.10-pip && \
    # 创建虚拟环境
    python3.10 -m venv /opt/venv

# 配置环境
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 配置pip使用国内镜像
RUN mkdir -p /root/.pip && \
    echo '[global]' > /root/.pip/pip.conf && \
    echo 'index-url = https://pypi.tuna.tsinghua.edu.cn/simple' >> /root/.pip/pip.conf && \
    echo 'trusted-host = pypi.tuna.tsinghua.edu.cn' >> /root/.pip/pip.conf && \
    # 更新pip
    python -m pip install --upgrade pip && \
    # 验证安装
    echo "Python version:" && \
    python --version && \
    echo "Python3 version:" && \
    python3 --version && \
    echo "Python path:" && \
    which python && \
    echo "Python3 path:" && \
    which python3

# 配置npm和pip镜像源
RUN npm config set registry https://registry.npmmirror.com && \
    pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip3 config set install.trusted-host mirrors.aliyun.com

# 配置网络设置
# 注意：在Docker中，/etc/resolv.conf是只读的，无法直接修改
# 我们在配置脚本中已经添加了hosts条目来解决一些DNS问题

# 创建目录
RUN mkdir -p /app/frontend /app/backend /app/panel /app/logs /app/data

# 复制前端代码
COPY web-frontend/ /app/frontend-src/

# 构建前端（低内存环境优化）
WORKDIR /app/frontend-src
# 分步执行，减少内存使用
# 注意：不使用--production参数，因为需要安装@vue/cli-service等开发依赖
RUN npm config set cache /tmp/npm-cache && \
    npm install --legacy-peer-deps --no-optional --no-audit --no-fund --prefer-offline && \
    rm -rf /tmp/npm-cache && \
    export NODE_OPTIONS="--max-old-space-size=1024" && \
    npm run build && \
    mkdir -p /app/frontend && \
    cp -r dist/* /app/frontend/ && \
    rm -rf node_modules && \
    rm -rf /app/frontend-src

# 复制后端代码
COPY simpletrade/ /app/backend/simpletrade/
COPY vnpy_custom/ /app/backend/vnpy_custom/
COPY setup.py requirements.txt /app/backend/

# 检查vnpy_custom目录是否存在
RUN ls -la /app/backend/vnpy_custom || echo "Warning: vnpy_custom directory does not exist!"

# 安装后端依赖
WORKDIR /app/backend
# 安装系统依赖
RUN dnf install -y gcc gcc-c++ make cmake python39-devel wget

# 安装Python依赖
RUN pip3.9 install --no-cache-dir -r requirements.txt

# 安装TA-Lib替代品
RUN pip3.9 install --no-cache-dir pandas-ta ta finta

# 使用vnpy_custom目录中的vnpy源码
# 不需要安装vnpy包或创建mock模块

# 复制部署面板
COPY deploy/panel/ /app/panel/

# 复制配置文件
COPY deploy/config/nginx.conf /etc/nginx/conf.d/default.conf

# 复制启动脚本
COPY deploy/scripts/start.sh /app/
RUN chmod +x /app/start.sh

WORKDIR /app
EXPOSE 80

# 启动服务
CMD ["/app/start.sh"]
EOF

    # 构建Docker镜像
    cd "$REPO_DIR"
    docker build -t "$DOCKER_IMAGE:latest" \
        --build-arg CONFIGURE_REPOS_SCRIPT=./configure_centos_repos.sh \
        -f deploy/Dockerfile.lowmem . 2>&1 | tee -a "$BUILD_LOG"

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

    # 检查镜像是否存在
    if ! docker images | grep -q "$DOCKER_IMAGE"; then
        echo "错误: 未找到镜像 $DOCKER_IMAGE。构建可能失败。"
        exit 1
    fi

    # 运行容器，使用内存限制以适应低内存环境
    docker run -d --name "$CONTAINER_NAME" \
        -p 80:80 \
        -v "$LOG_DIR:/app/logs" \
        -v "$DATA_DIR:/app/data" \
        --security-opt label=disable \
        --dns 8.8.8.8 \
        --dns 114.114.114.114 \
        --memory="1024m" \
        --memory-swap="1536m" \
        --memory-swappiness=60 \
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
CLEAN=false
SWAP=false

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
        -c | --clean )    CLEAN=true
                          ;;
        -w | --swap )     SWAP=true
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
if [ "$CLEAN" = true ]; then
    clean_cache
fi

if [ "$SWAP" = true ]; then
    create_swap
fi

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
