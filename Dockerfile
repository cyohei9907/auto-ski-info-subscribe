# 多阶段构建 Dockerfile
# 阶段 1: 构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --prefer-offline --no-audit
COPY frontend/ ./
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

# 阶段 3: 最终运行镜像
FROM nginx:alpine

# 安装 Python、Supervisor 和依赖
RUN apk add --no-cache \
    python3 \
    py3-pip \
    postgresql-client \
    supervisor \
    bash \
    && ln -sf python3 /usr/bin/python

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

WORKDIR /app

EXPOSE 8080

# 使用 Supervisor 同时运行 Nginx 和 Django
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
