"""
Django settings for auto_ski_info project.
"""

import os
from pathlib import Path
from decouple import config
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-changeme-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Parse ALLOWED_HOSTS from environment variable
allowed_hosts_str = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0')
ALLOWED_HOSTS = [s.strip() for s in allowed_hosts_str.split(',')]

# Add common internal hostnames for Docker/Kubernetes environments
if not DEBUG or config('USE_CLOUD_SQL', default=False, cast=bool):
    ALLOWED_HOSTS.extend(['backend', '127.0.0.1', 'localhost'])
    # In production, accept all hosts if configured with *
    if '*' in allowed_hosts_str:
        ALLOWED_HOSTS = ['*']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_yasg',
]

LOCAL_APPS = [
    'accounts',
    'x_monitor',
    'ai_service',
    'mcp_service',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'auto_ski_info.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'auto_ski_info.wsgi.application'

# Database
# ローカル開発環境では SQLite を使用、本番環境では Cloud SQL (PostgreSQL) を使用
USE_CLOUD_SQL = config('USE_CLOUD_SQL', default=False, cast=bool)

if USE_CLOUD_SQL:
    # 本番環境 (Cloud Run + Cloud SQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': '/cloudsql/gen-lang-client-0543160602:asia-northeast1:ai-project-database',
            'NAME': config('CLOUD_DB_NAME', default='ski-scrapy'),
            'USER': config('CLOUD_DB_USER', default='postgres'),
            'PASSWORD': config('DATABASE_PASSWORD'),  # Secret Manager から取得
        }
    }
else:
    # ローカル開発環境 (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# CSRF Cookie設定
CSRF_COOKIE_HTTPONLY = False  # JavaScriptからアクセス可能にする
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False  # 開発環境用、本番環境ではTrueに
CSRF_USE_SESSIONS = False

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'LOGIN_URL': '/admin/login/',
    'LOGOUT_URL': '/admin/logout/',
}

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat スケジュール設定
CELERY_BEAT_SCHEDULE = {
    'monitor-all-accounts-every-30-minutes': {
        'task': 'x_monitor.tasks.monitor_all_active_accounts',
        'schedule': 1800.0,  # 30分ごと（最短间隔检查，实际监控由各账户的monitoring_interval控制）
    },
    'monitor-today-tweets-morning': {
        'task': 'x_monitor.tasks.monitor_today_tweets',
        'schedule': crontab(hour=9, minute=0),  # 毎日9:00
    },
    'monitor-today-tweets-noon': {
        'task': 'x_monitor.tasks.monitor_today_tweets',
        'schedule': crontab(hour=12, minute=0),  # 毎日12:00
    },
    'monitor-today-tweets-evening': {
        'task': 'x_monitor.tasks.monitor_today_tweets',
        'schedule': crontab(hour=18, minute=0),  # 毎日18:00
    },
}

# X.com Scraper Settings
# USE_AUTHENTICATED_SCRAPER=True: 使用登录凭证访问（需要先运行setup_authentication保存cookies）
# USE_AUTHENTICATED_SCRAPER=False: 游客模式访问（仅能看到4-6条置顶推文）
USE_AUTHENTICATED_SCRAPER = config('USE_AUTHENTICATED_SCRAPER', default=False, cast=bool)

# Gemini AI settings
# ローカルでは環境変数、Cloud Run では Secret Manager から取得
GEMINI_API_KEY = config('AI_API_KEY_GOOGLE', default='')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}