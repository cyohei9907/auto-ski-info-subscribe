#!/bin/bash

# Cloud SQL 使用時のみ PostgreSQL 待機
if [ "$USE_CLOUD_SQL" = "True" ]; then
  echo "Waiting for Cloud SQL to be ready..."
  sleep 5
fi

# データディレクトリを作成（SQLite用）
mkdir -p /app/data

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Initialize users
echo "Initializing users..."
python init_users.py || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

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