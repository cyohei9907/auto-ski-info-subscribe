#!/usr/bin/env python
"""模拟前端调用 monitor_account_now API"""
import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from x_monitor.views import monitor_account_now
from x_monitor.models import XAccount

User = get_user_model()

# 获取用户和账户
user = User.objects.first()
if not user:
    print("没有用户")
    sys.exit(1)

account = XAccount.objects.filter(username='skiinfomation').first()
if not account:
    print("账户不存在")
    sys.exit(1)

print("=" * 80)
print(f"测试 monitor_account_now API")
print("=" * 80)
print(f"用户: {user.email}")
print(f"账户: @{account.username} (ID: {account.id})")
print()

# 创建 mock request
factory = RequestFactory()
request = factory.post(f'/api/monitor/accounts/{account.id}/monitor/')
request.user = user

print("调用 monitor_account_now...")
try:
    response = monitor_account_now(request, account.id)
    print(f"✅ API 调用成功!")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.data}")
except Exception as e:
    print(f"❌ API 调用失败:")
    print(f"   错误: {e}")
    import traceback
    traceback.print_exc()
