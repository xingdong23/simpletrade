#!/bin/bash
# SimpleTrade 环境设置脚本
# 此脚本会创建并配置 simpletrade conda 环境

# 检查是否安装了 conda
if ! command -v conda &> /dev/null; then
    echo "错误: 未找到 conda。请先安装 Anaconda 或 Miniconda。"
    exit 1
fi

# 创建 conda 环境
echo "创建 simpletrade 环境..."
conda create -n simpletrade python=3.12 -y

# 激活环境
echo "激活 simpletrade 环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate simpletrade

# 安装 TA-Lib
echo "安装 TA-Lib..."
conda install -c conda-forge ta-lib -y

# 安装 vnpy 相关包
echo "安装 vnpy 相关包..."
pip install vnpy vnpy_sqlite

# 安装 FastAPI 和 Uvicorn
echo "安装 FastAPI 和 Uvicorn..."
pip install fastapi uvicorn[standard] pydantic[email]

# 安装 tigeropen
echo "安装 tigeropen..."
pip install tigeropen

# 以开发模式安装项目
echo "以开发模式安装项目..."
pip install -e .

echo "环境设置完成！"
echo "使用以下命令启动服务器："
echo "conda run --no-capture-output -n simpletrade python -m uvicorn simpletrade.api.server:app --host 0.0.0.0 --port 8002 --reload"
