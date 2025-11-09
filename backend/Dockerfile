FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    postgresql-client \
    wget \
    gnupg \
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

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt whitenoise

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy project (this will include frontend_build if it exists)
COPY . .

EXPOSE 8000

# Default command (can be overridden in docker-compose.yml)
# Increased timeout to 600s for Playwright operations
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "600", "auto_ski_info.wsgi:application"]