FROM continuumio/miniconda3

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安装 TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib-0.4.0-src.tar.gz ta-lib/

# 创建 conda 环境
RUN conda create -n simpletrade python=3.12 -y

# 安装依赖
RUN conda install -n simpletrade -c conda-forge ta-lib -y && \
    conda run -n simpletrade pip install vnpy vnpy_sqlite fastapi uvicorn[standard] pydantic[email] tigeropen

# 暴露端口
EXPOSE 8002

# 启动命令
CMD ["conda", "run", "--no-capture-output", "-n", "simpletrade", "python", "-m", "uvicorn", "simpletrade.api.server:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
