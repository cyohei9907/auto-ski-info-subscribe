#!/bin/bash
set -e

echo "Waiting for database to be ready..."
sleep 2

echo "Running migrations..."
python manage.py migrate --noinput

echo "Initializing users..."
python init_users.py || true

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

# Check if DEBUG_MODE is enabled for remote debugging
if [ "$DEBUG_MODE" = "True" ]; then
    echo "Starting Django with debugpy on port 5678 (ready for remote debugging)..."
    python -m debugpy --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8000
else
    echo "Starting Django server..."
    python manage.py runserver 0.0.0.0:8000
fi
