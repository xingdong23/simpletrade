FROM continuumio/miniconda3

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    netcat-openbsd \
    libegl1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 直接用 conda 安装 TA-Lib，无需源码编译
# 创建 conda 环境
RUN conda create -n simpletrade python=3.12 -y

# 移除 conda 官方源，仅用清华镜像
RUN conda config --remove-key channels || true
RUN conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/ \
    && conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ \
    && conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ \
    && conda config --set show_channel_urls yes

# 安装依赖
RUN conda install -n simpletrade ta-lib -y && \
    conda run -n simpletrade pip install vnpy vnpy_sqlite fastapi uvicorn[standard] pydantic[email] tigeropen requests python-multipart python-jose sqlalchemy pymysql python-dotenv

# 复制启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 暴露端口
EXPOSE 8003

# 启动命令
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["conda", "run", "--no-capture-output", "-n", "simpletrade", "python", "-m", "uvicorn", "simpletrade.api.server:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
