# 多阶段构建 Dockerfile
# 阶段 1: 构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --prefer-offline --no-audit
COPY frontend/ ./

# 设置 API URL 为相对路径（通过 nginx 代理）
ENV REACT_APP_API_URL=/api

RUN npm run build

# 阶段 2: 构建后端
FROM python:3.11-slim AS backend-builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

COPY backend/ ./

# 阶段 3: 最终运行镜像 (使用 Debian 以保持 Python 兼容性)
FROM python:3.11-slim

# 安装 Nginx、Supervisor 和系统依赖
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    postgresql-client \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 从 backend-builder 复制 Python 依赖和应用
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=backend-builder /usr/local/bin/playwright /usr/local/bin/playwright
COPY --from=backend-builder /root/.cache/ms-playwright /root/.cache/ms-playwright
COPY --from=backend-builder /app /app

# 从 frontend-builder 复制前端构建文件
COPY --from=frontend-builder /frontend/build /usr/share/nginx/html

# 复制配置文件
COPY nginx.combined.conf /etc/nginx/nginx.conf
COPY supervisord.combined.conf /etc/supervisord.conf

# 创建必要的目录
RUN mkdir -p /var/log/supervisor /app/data /run

WORKDIR /app

# 创建启动脚本，先执行迁移再启动 Supervisor
RUN echo '#!/bin/bash\n\
    set -e\n\
    echo "Starting initialization..."\n\
    \n\
    # 设置默认端口（Cloud Run 会自动设置 PORT 环境变量）\n\
    export PORT=${PORT:-8080}\n\
    echo "Container will listen on port: $PORT"\n\
    \n\
    # 更新 nginx 配置以使用正确的端口\n\
    sed -i "s/listen 8080;/listen $PORT;/g" /etc/nginx/nginx.conf\n\
    \n\
    # 创建必要的目录\n\
    mkdir -p /var/log/supervisor /app/data /run\n\
    \n\
    # Cloud SQL 使用時のみ PostgreSQL 待機\n\
    if [ "$USE_CLOUD_SQL" = "True" ]; then\n\
    echo "Waiting for Cloud SQL to be ready..."\n\
    sleep 5\n\
    fi\n\
    \n\
    # Run migrations (with timeout protection for Cloud Run)\n\
    echo "Running database migrations..."\n\
    timeout 120 python manage.py migrate --noinput || echo "Migration timeout or failed, continuing..."\n\
    \n\
    # Initialize users (non-blocking)\n\
    echo "Initializing users..."\n\
    python init_users.py || true\n\
    \n\
    # Collect static files\n\
    echo "Collecting static files..."\n\
    python manage.py collectstatic --noinput --clear\n\
    \n\
    # Verify critical services can start\n\
    echo "Checking Python environment..."\n\
    python --version\n\
    \n\
    # Start Supervisor\n\
    echo "Starting Supervisor..."\n\
    exec /usr/bin/supervisord -c /etc/supervisord.conf\n\
    ' > /app/startup.sh && chmod +x /app/startup.sh

EXPOSE 8080

# 使用启动脚本
CMD ["/app/startup.sh"]
