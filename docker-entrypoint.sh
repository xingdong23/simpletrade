#!/bin/bash

# 等待 MySQL 服务启动
echo "Waiting for MySQL to start..."
while ! nc -z $SIMPLETRADE_DB_HOST $SIMPLETRADE_DB_PORT; do
  sleep 1
done
echo "MySQL started"

# 初始化数据库
echo "Initializing database..."
conda run -n simpletrade python scripts/init_database.py

# 启动应用
echo "Starting application..."
exec "$@"
