#!/usr/bin/env python
"""检查时区问题"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.utils import timezone as django_timezone
from django.conf import settings
from datetime import datetime, timedelta
from x_monitor.models import Tweet, XAccount

def check_timezone_issue():
    """检查时区配置和推文时间"""
    print("=" * 60)
    print("时区配置检查")
    print("=" * 60)
    
    # Django设置
    print(f"\n1. Django 设置:")
    print(f"   TIME_ZONE: {settings.TIME_ZONE}")
    print(f"   USE_TZ: {settings.USE_TZ}")
    
    # 当前时间
    now = django_timezone.now()
    print(f"\n2. 当前时间:")
    print(f"   django_timezone.now(): {now}")
    print(f"   时区信息: {now.tzinfo}")
    print(f"   UTC偏移: {now.utcoffset()}")
    
    # 东京时间
    import zoneinfo
    tokyo_tz = zoneinfo.ZoneInfo('Asia/Tokyo')
    tokyo_now = datetime.now(tokyo_tz)
    print(f"\n3. 东京时间:")
    print(f"   datetime.now(tokyo_tz): {tokyo_now}")
    print(f"   与UTC时间差: {tokyo_now.utcoffset()}")
    
    # 检查时间过滤
    print(f"\n4. 时间过滤检查:")
    
    # UTC时间的6小时前
    six_hours_ago_utc = now - timedelta(hours=6)
    print(f"   6小时前 (UTC): {six_hours_ago_utc}")
    
    # 如果按东京时间理解，应该是
    six_hours_ago_tokyo = tokyo_now - timedelta(hours=6)
    print(f"   6小时前 (Tokyo): {six_hours_ago_tokyo}")
    
    # 检查数据库中的推文
    print(f"\n5. 数据库推文时间:")
    account = XAccount.objects.filter(username='skiinfomation').first()
    if account:
        tweets = Tweet.objects.filter(x_account=account).order_by('-posted_at')
        for i, tweet in enumerate(tweets[:5], 1):
            tweet_utc = tweet.posted_at
            # 转换到东京时间显示
            tweet_tokyo = tweet_utc.astimezone(tokyo_tz)
            
            # 计算时间差
            hours_from_now_utc = (now - tweet_utc).total_seconds() / 3600
            hours_from_now_tokyo = (tokyo_now - tweet_tokyo).total_seconds() / 3600
            
            in_6h_utc = "✅" if tweet_utc >= six_hours_ago_utc else "❌"
            
            print(f"\n   推文 {i}:")
            print(f"     数据库时间 (UTC): {tweet_utc}")
            print(f"     东京时间显示: {tweet_tokyo}")
            print(f"     距离现在: {hours_from_now_utc:.1f}小时 (UTC计算)")
            print(f"     在6小时内? {in_6h_utc} (按UTC计算)")
    
    # 时区问题说明
    print(f"\n6. 问题分析:")
    print(f"   - 当前系统使用 UTC 时间")
    print(f"   - 东京时间 = UTC + 9小时")
    print(f"   - 如果推文时间是 UTC 03:03，在东京显示为 12:03")
    print(f"   - 如果现在是东京时间 22:30 (UTC 13:30)，")
    print(f"     那么 UTC 03:03 距离现在是 10.5小时 (超过6小时)")

if __name__ == '__main__':
    check_timezone_issue()
