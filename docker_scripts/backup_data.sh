#!/bin/bash

# 备份数据
BACKUP_DIR="/app/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz"

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 备份数据
echo "开始备份数据..."
tar -czf ${BACKUP_FILE} /app/data /app/configs /app/logs

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "备份成功: ${BACKUP_FILE}"
    echo "备份大小: $(du -h ${BACKUP_FILE} | cut -f1)"
else
    echo "备份失败!"
    exit 1
fi

# 清理旧备份（保留最近10个）
echo "清理旧备份..."
ls -t ${BACKUP_DIR}/backup_*.tar.gz | tail -n +11 | xargs -r rm

echo "备份完成!"
