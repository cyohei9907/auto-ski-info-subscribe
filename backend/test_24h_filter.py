#!/usr/bin/env python
"""验证24小时过滤"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.utils import timezone
from datetime import datetime, timedelta
import zoneinfo

# 当前时间
now = timezone.now()
h24_ago = now - timedelta(hours=24)

print("24小时过滤测试")
print("=" * 60)
print(f"现在 (UTC): {now}")
print(f"24小时前 (UTC): {h24_ago}")
print()

# 测试推文时间
tweet_times = [
    "2025-11-08T03:03:02.000Z",
    "2025-11-08T03:02:33.000Z",
    "2025-11-08T02:59:36.000Z",
    "2025-11-08T01:05:13.000Z"
]

tokyo_tz = zoneinfo.ZoneInfo('Asia/Tokyo')

for tweet_time_str in tweet_times:
    tweet_time = datetime.fromisoformat(tweet_time_str.replace('Z', '+00:00'))
    tweet_tokyo = tweet_time.astimezone(tokyo_tz)
    hours_ago = (now - tweet_time).total_seconds() / 3600
    in_24h = "✅" if tweet_time >= h24_ago else "❌"
    
    print(f"推文: {tweet_time_str}")
    print(f"  UTC: {tweet_time}")
    print(f"  东京: {tweet_tokyo}")
    print(f"  距今: {hours_ago:.1f}小时")
    print(f"  在24小时内? {in_24h}")
    print()
