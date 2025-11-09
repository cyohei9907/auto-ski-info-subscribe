#!/usr/bin/env python
"""测试发送 Celery 任务"""
import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from x_monitor.tasks import monitor_single_account
from x_monitor.models import XAccount

# 获取账户
account = XAccount.objects.filter(username='skiinfomation').first()
if not account:
    print("账户不存在")
    sys.exit(1)

print("=" * 80)
print(f"测试发送 Celery 任务")
print("=" * 80)
print(f"账户: @{account.username} (ID: {account.id})")
print()

# 发送任务
print("发送任务到 Celery worker...")
task = monitor_single_account.delay(account.id)
print(f"✅ 任务已发送!")
print(f"   Task ID: {task.id}")
print(f"   状态: {task.state}")
print()
print("检查 Celery worker 终端窗口，应该会看到任务执行日志")
