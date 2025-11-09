#!/usr/bin/env python
"""测试 Celery 连接"""
import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from celery import Celery
from django.conf import settings

print("=" * 80)
print("Celery 配置检查:")
print("=" * 80)
print(f"CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
print(f"CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}")
print("=" * 80)

# 创建 Celery app
app = Celery('auto_ski_info')
app.config_from_object('django.conf:settings', namespace='CELERY')

print("\n测试连接到 Celery broker...")
try:
    # 检查连接
    conn = app.connection()
    conn.ensure_connection(max_retries=3)
    print("✅ Celery broker 连接成功!")
    conn.release()
except Exception as e:
    print(f"❌ Celery broker 连接失败:")
    print(f"   错误: {e}")
    print(f"\n解决方案:")
    print(f"   需要在本地启动 Celery worker:")
    print(f"   celery -A auto_ski_info worker -l info")
