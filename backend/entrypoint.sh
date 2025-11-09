#!/bin/bash

# Cloud SQL 使用時のみ PostgreSQL 待機
if [ "$USE_CLOUD_SQL" = "True" ]; then
  echo "Waiting for Cloud SQL to be ready..."
  sleep 5
fi

# データディレクトリを作成（SQLite用）
mkdir -p /app/data

# Check if frontend build exists
echo "Checking frontend build directory..."
if [ -d "/app/frontend_build" ]; then
  echo "✅ Frontend build directory exists"
  ls -la /app/frontend_build/ | head -10
else
  echo "⚠️  Frontend build directory NOT found at /app/frontend_build"
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Initialize users
echo "Initializing users..."
python init_users.py || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --verbosity 2

# Verify static files were collected
echo "Checking staticfiles directory..."
if [ -d "/app/staticfiles" ]; then
  echo "✅ Staticfiles directory exists"
  ls -la /app/staticfiles/ | head -10
else
  echo "⚠️  Staticfiles directory NOT found"
fi

# Create superuser if not exists (optional for production)
if [ "$DEBUG" = "True" ]; then
  python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(username='admin', email='admin@example.com', password='admin@123')
    print('Development superuser created')
    print('Email: admin@example.com')
    print('Password: admin@123')
" || echo "Superuser creation skipped"
fi

# Start server
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 300 auto_ski_info.wsgi:application