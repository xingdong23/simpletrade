FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 使用国内apt镜像
# 完全替换所有源为国内镜像
RUN echo "Configuring apt mirrors..." && \
    # 备份原始源配置
    if [ -f /etc/apt/sources.list ]; then \
        cp /etc/apt/sources.list /etc/apt/sources.list.bak; \
    fi && \
    # 清空所有源配置
    echo "" > /etc/apt/sources.list && \
    # 移除所有其他源配置
    rm -f /etc/apt/sources.list.d/*.list && \
    # 创建阿里云镜像源配置（速度更快）
    echo "deb https://mirrors.aliyun.com/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-backports main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list && \
    # 更新软件包列表
    apt-get clean && \
    apt-get update -y

# 安装系统依赖
RUN apt-get update && \
    echo "Installing system dependencies..." && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    libssl-dev \
    pkg-config \
    wget \
    curl \
    netcat-openbsd \
    vim \
    nano \
    htop \
    procps \
    iputils-ping \
    net-tools \
    telnet \
    dnsutils \
    lsof \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装TA-Lib
# 使用国内镜像下载TA-Lib
RUN cd /tmp && \
    echo "Downloading TA-Lib..." && \
    wget -q -O ta-lib-0.4.0-src.tar.gz https://gitee.com/mirrors/ta-lib/raw/master/ta-lib-0.4.0-src.tar.gz || \
    wget -q -O ta-lib-0.4.0-src.tar.gz https://jztkft.dl.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz || \
    wget -q -O ta-lib-0.4.0-src.tar.gz https://versaweb.dl.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz || \
    wget -q -O ta-lib-0.4.0-src.tar.gz http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    echo "Extracting TA-Lib..." && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    echo "Configuring TA-Lib..." && \
    ./configure --prefix=/usr && \
    echo "Building TA-Lib..." && \
    make && \
    echo "Installing TA-Lib..." && \
    make install && \
    cd /tmp && \
    rm -rf ta-lib-0.4.0-src.tar.gz ta-lib/

# 配置PIP国内镜像
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 安装常用Python工具
RUN pip install --no-cache-dir \
    ipython \
    jupyter \
    notebook \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scikit-learn \
    statsmodels \
    pytest \
    black \
    flake8 \
    isort \
    mypy \
    pylint

# 安装vnpy核心
RUN pip install --no-cache-dir \
    vnpy \
    vnpy_cta_strategy \
    vnpy_ctastrategy \
    vnpy_datamanager \
    vnpy_sqlite \
    vnpy_rest \
    vnpy_websocket \
    vnpy_csv \
    vnpy_mysql \
    vnpy_ctp \
    vnpy_ib \
    vnpy_tushare \
    vnpy_rqdata \
    vnpy_jotdx

# 安装应用依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 验证vnpy安装
RUN python -c "from vnpy.trader.engine import MainEngine; from vnpy.app.cta_strategy import CtaStrategyApp; print('VeighNa installation verified!')"

# 创建常用目录
RUN mkdir -p /app/data /app/logs /app/configs /app/notebooks

# 添加常用工具脚本
COPY docker_scripts/ /app/docker_scripts/
RUN chmod +x /app/docker_scripts/*.sh

# 复制启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 暴露端口
EXPOSE 8003

# 启动命令
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["conda", "run", "--no-capture-output", "-n", "simpletrade", "python", "-m", "uvicorn", "simpletrade.api.server:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
