# 使用多阶段构建
# 阶段1: 构建前端
FROM node:16 as frontend-builder
WORKDIR /app/frontend
COPY web-frontend/package*.json ./
RUN npm install
COPY web-frontend/ ./
RUN npm run build

# 阶段2: 构建后端
FROM python:3.9 as backend-builder
WORKDIR /app/backend
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY simpletrade/ ./simpletrade/
COPY setup.py ./

# 阶段3: 最终镜像
FROM python:3.9-slim
WORKDIR /app

# 安装 Nginx 和其他必要工具
RUN apt-get update && \
    apt-get install -y nginx curl procps net-tools vim && \
    rm -rf /var/lib/apt/lists/*

# 创建数据目录
RUN mkdir -p /app/data

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist /app/frontend

# 复制后端
COPY --from=backend-builder /app/backend /app/backend
COPY --from=backend-builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# 复制部署面板
COPY deploy/panel/ /app/panel/

# 复制配置文件
COPY deploy/config/nginx.conf /etc/nginx/conf.d/default.conf

# 复制启动脚本
COPY deploy/scripts/start.sh /app/
RUN chmod +x /app/start.sh

# 创建日志目录
RUN mkdir -p /app/logs

EXPOSE 80

# 启动服务
CMD ["/app/start.sh"]
