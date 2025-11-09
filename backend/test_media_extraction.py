#!/usr/bin/env python
"""测试图片和头像抓取"""
import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from x_monitor.models import XAccount, Tweet
from x_monitor.services import XMonitorService

# 获取账户
account = XAccount.objects.filter(username='skiinfomation').first()
if not account:
    print("账户不存在")
    sys.exit(1)

print("=" * 80)
print(f"账户: @{account.username}")
print(f"当前头像: {account.avatar_url}")
print("=" * 80)

# 删除旧推文
print("\n删除旧推文以便重新测试...")
deleted = Tweet.objects.filter(x_account=account).delete()[0]
print(f"已删除 {deleted} 条旧推文")
print("=" * 80)

# 重新抓取
print("\n开始抓取推文（带图片和头像）...")
service = XMonitorService()
result = service.monitor_account(account, today_only=True, max_tweets=50)

print(f"\n抓取结果: {result.get('new_tweets', 0)} 条新推文")
print("=" * 80)

# 检查结果
account.refresh_from_db()
print(f"\n更新后的头像: {account.avatar_url}")
print("=" * 80)

# 检查推文
tweets = Tweet.objects.filter(x_account=account).order_by('-posted_at')
print(f"\n推文详情:")
for i, tweet in enumerate(tweets, 1):
    print(f"\n推文 {i}:")
    print(f"  内容: {tweet.content[:50]}...")
    print(f"  时间: {tweet.posted_at}")
    print(f"  媒体数量: {len(tweet.media_urls) if tweet.media_urls else 0}")
    if tweet.media_urls:
        for j, url in enumerate(tweet.media_urls, 1):
            print(f"    图片{j}: {url[:80]}...")
