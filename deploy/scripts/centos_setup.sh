#!/bin/bash

# CentOS 8.5 环境设置脚本
# 用于在 CentOS 8.5 服务器上设置 SimpleTrade 部署环境

# 显示帮助信息
show_help() {
    echo "SimpleTrade CentOS 8.5 环境设置脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -i, --install   安装 Docker 和其他必要软件"
    echo "  -s, --selinux   配置 SELinux 以允许 Docker"
    echo "  -f, --firewall  配置防火墙以开放 HTTP 端口"
    echo "  -a, --all       执行所有操作"
    echo "  -h, --help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --all        # 执行所有操作"
    echo "  $0 --install    # 只安装 Docker"
    echo ""
}

# 检查是否为 root 用户
check_root() {
    if [ "$(id -u)" != "0" ]; then
        echo "此脚本需要 root 权限运行"
        echo "请使用 sudo $0 或以 root 用户身份运行"
        exit 1
    fi
}

# 检查是否为 CentOS 8
check_centos() {
    if [ ! -f /etc/centos-release ]; then
        echo "此脚本仅适用于 CentOS 系统"
        exit 1
    fi
    
    CENTOS_VERSION=$(cat /etc/centos-release | tr -dc '0-9.' | cut -d \. -f1)
    if [ "$CENTOS_VERSION" != "8" ]; then
        echo "此脚本仅适用于 CentOS 8.x 系统"
        echo "检测到 CentOS $CENTOS_VERSION"
        exit 1
    fi
    
    echo "检测到 CentOS 8 系统"
}

# 安装 Docker 和其他必要软件
install_docker() {
    echo "安装 Docker 和其他必要软件..."
    
    # 更新软件包
    dnf update -y
    
    # 安装必要的依赖
    dnf install -y dnf-utils device-mapper-persistent-data lvm2
    
    # 添加 Docker 仓库
    dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
    
    # 安装 Docker
    dnf install -y docker-ce docker-ce-cli containerd.io
    
    # 启动 Docker 服务
    systemctl start docker
    
    # 设置 Docker 开机自启
    systemctl enable docker
    
    # 安装 Git
    dnf install -y git
    
    # 安装其他有用的工具
    dnf install -y vim curl wget htop net-tools
    
    echo "Docker 和其他必要软件安装完成"
}

# 配置 SELinux
configure_selinux() {
    echo "配置 SELinux..."
    
    # 检查 SELinux 状态
    SELINUX_STATUS=$(getenforce)
    echo "当前 SELinux 状态: $SELINUX_STATUS"
    
    # 配置 SELinux 允许 Docker
    setsebool -P container_manage_cgroup 1
    
    echo "SELinux 配置完成"
    echo "如果仍然遇到 SELinux 相关问题，可以考虑临时禁用 SELinux:"
    echo "  sudo setenforce 0"
    echo "或永久禁用 SELinux (需要重启):"
    echo "  sudo sed -i 's/^SELINUX=enforcing$/SELINUX=disabled/' /etc/selinux/config"
    echo "  sudo reboot"
}

# 配置防火墙
configure_firewall() {
    echo "配置防火墙..."
    
    # 检查防火墙状态
    FIREWALL_STATUS=$(systemctl is-active firewalld)
    echo "当前防火墙状态: $FIREWALL_STATUS"
    
    if [ "$FIREWALL_STATUS" = "active" ]; then
        # 开放 HTTP 端口
        firewall-cmd --permanent --add-service=http
        
        # 重新加载防火墙配置
        firewall-cmd --reload
        
        echo "防火墙配置完成"
    else
        echo "防火墙未运行，跳过配置"
    fi
}

# 处理命令行参数
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

INSTALL=false
SELINUX=false
FIREWALL=false

while [ "$1" != "" ]; do
    case $1 in
        -i | --install )   INSTALL=true
                          ;;
        -s | --selinux )   SELINUX=true
                          ;;
        -f | --firewall )  FIREWALL=true
                          ;;
        -a | --all )       INSTALL=true
                           SELINUX=true
                           FIREWALL=true
                          ;;
        -h | --help )      show_help
                           exit 0
                          ;;
        * )                show_help
                           exit 1
    esac
    shift
done

# 检查是否为 root 用户
check_root

# 检查是否为 CentOS 8
check_centos

# 执行操作
if [ "$INSTALL" = true ]; then
    install_docker
fi

if [ "$SELINUX" = true ]; then
    configure_selinux
fi

if [ "$FIREWALL" = true ]; then
    configure_firewall
fi

echo "环境设置完成"
echo "现在您可以使用 local_deploy.sh 脚本部署 SimpleTrade 应用"
echo "  ./deploy/scripts/local_deploy.sh --build --run"

exit 0
