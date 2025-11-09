#!/usr/bin/env python
"""检查推文详细信息，包括图片和用户头像"""
import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from x_monitor.models import Tweet, XAccount

# 获取账户
account = XAccount.objects.filter(username='skiinfomation').first()
if not account:
    print("账户不存在")
    sys.exit(1)

print("=" * 80)
print("账户信息:")
print(f"  用户名: @{account.username}")
print(f"  头像URL: {account.avatar_url or '(无)'}")
print(f"  Display Name: {account.display_name or '(无)'}")
print("=" * 80)

# 检查推文
tweets = Tweet.objects.filter(x_account=account).order_by('-posted_at')[:5]
print(f"\n最新的 {len(tweets)} 条推文:")
print("=" * 80)

for i, tweet in enumerate(tweets, 1):
    print(f"\n推文 {i}:")
    print(f"  ID: {tweet.tweet_id}")
    print(f"  时间: {tweet.posted_at}")
    print(f"  内容: {tweet.content[:50]}...")
    print(f"  媒体URLs: {tweet.media_urls or '(无)'}")
    print(f"  媒体数量: {len(tweet.media_urls) if tweet.media_urls else 0}")
    print(f"  Hashtags: {tweet.hashtags or '(无)'}")
    print(f"  Mentions: {tweet.mentions or '(无)'}")
