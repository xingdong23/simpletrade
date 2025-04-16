#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# 从环境变量或默认值获取数据库连接信息
MYSQL_USER="${SIMPLETRADE_DB_USER:-root}"
MYSQL_PASSWORD="${SIMPLETRADE_DB_PASSWORD:-Cz159csa}"
MYSQL_HOST="${SIMPLETRADE_DB_HOST:-localhost}"
MYSQL_PORT="${SIMPLETRADE_DB_PORT:-3306}"
DB_NAME="${SIMPLETRADE_DB_NAME:-simpletrade}"

# 显示数据库连接信息
echo "Using database connection:"
echo "  Host: $MYSQL_HOST:$MYSQL_PORT"
echo "  Database: $DB_NAME"
echo "  User: $MYSQL_USER"

# 创建数据库
echo "创建数据库 $DB_NAME..."
mysql -u$MYSQL_USER -p$MYSQL_PASSWORD -h$MYSQL_HOST -P$MYSQL_PORT -e "CREATE DATABASE IF NOT EXISTS $DB_NAME DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

if [ $? -eq 0 ]; then
    echo "数据库创建成功或已存在"
else
    echo "数据库创建失败"
    exit 1
fi

# 安装必要的Python包
echo "安装必要的Python包..."
conda run -n simpletrade pip install sqlalchemy pymysql

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# 初始化数据库表和示例数据
echo "初始化数据库表和示例数据..."
cd "$PROJECT_ROOT"
conda run -n simpletrade python "$SCRIPT_DIR/init_database.py"

echo "MySQL数据库设置完成"
