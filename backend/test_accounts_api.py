#!/usr/bin/env python
"""测试账号列表 API"""
import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from x_monitor.models import XAccount

User = get_user_model()

# 获取第一个用户
user = User.objects.first()
if not user:
    print("没有用户")
    sys.exit(1)

print("=" * 80)
print(f"用户: {user.email}")
print("=" * 80)

# 检查账户
accounts = XAccount.objects.filter(user=user)
print(f"\n数据库中的账户: {accounts.count()} 个")
for account in accounts:
    print(f"  - @{account.username} (ID: {account.id}, Active: {account.is_active})")

# 测试 API
client = APIClient()
client.force_authenticate(user=user)

print("\n" + "=" * 80)
print("测试 API: GET /api/monitor/accounts/")
print("=" * 80)

response = client.get('/api/monitor/accounts/')
print(f"状态码: {response.status_code}")
print(f"响应类型: {type(response.data)}")
print(f"响应内容:")

import json
print(json.dumps(response.data, indent=2, ensure_ascii=False, default=str))
