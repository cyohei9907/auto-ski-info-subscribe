#!/usr/bin/env python
"""测试新的推文过滤逻辑"""
import os
import sys
import django
from datetime import datetime, timedelta

# Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from x_monitor.models import XAccount, Tweet
from x_monitor.services import XMonitorService

# 初始化服务
service = XMonitorService()

# 获取账户
account = XAccount.objects.filter(username='skiinfomation').first()
if not account:
    print("账户 @skiinfomation 不存在")
    sys.exit(1)

print(f"账户: @{account.username}")
print(f"当前数据库推文总数: {Tweet.objects.filter(x_account=account).count()}")
print("=" * 80)

# 删除所有旧推文以便重新测试
print("删除所有旧推文...")
deleted_count = Tweet.objects.filter(x_account=account).delete()[0]
print(f"已删除 {deleted_count} 条旧推文")
print("=" * 80)

# 测试抓取
print("开始抓取推文（只抓取24小时内的原创推文，跳过转发和回复）...")
print()

try:
    # 使用 monitor_account 方法
    result = service.monitor_account(account, today_only=True, max_tweets=50)
    print(f"\n抓取结果:")
    print(f"- 新推文: {result.get('new_tweets', 0)} 条")
    print(f"- 结果: {result.get('message', '未知')}")
    
    # 显示新推文
    new_tweets = Tweet.objects.filter(x_account=account).order_by('-posted_at')[:10]
    print(f"\n最新的推文:")
    for i, tweet in enumerate(new_tweets, 1):
        # 计算推文时间
        from django.utils import timezone
        now = timezone.now()
        hours_ago = (now - tweet.posted_at).total_seconds() / 3600
        
        content_preview = tweet.content[:50] + '...' if len(tweet.content) > 50 else tweet.content
        print(f"  {i}. [{tweet.posted_at.strftime('%m-%d %H:%M')}] ({hours_ago:.1f}小时前)")
        print(f"     {content_preview}")
        print()

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
