#!/usr/bin/env python
"""测试24小时范围获取推文"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from x_monitor.models import XAccount, Tweet
from x_monitor.services import XMonitorService

def test_fetch_24h():
    """测试获取24小时内的推文"""
    print("=" * 60)
    print("测试: 获取24小时内的推文")
    print("=" * 60)
    
    # 获取账户
    account = XAccount.objects.filter(username='skiinfomation').first()
    if not account:
        print("❌ 未找到账户 skiinfomation")
        return
    
    print(f"✓ 找到账户: @{account.username}")
    
    # 获取当前推文数
    before_count = Tweet.objects.filter(x_account=account).count()
    print(f"✓ 数据库中现有推文数: {before_count}")
    
    # 使用24小时范围获取推文
    service = XMonitorService()
    print("\n开始获取24小时内的推文...")
    result = service.monitor_account(account, max_tweets=10, hours=24)
    
    print(f"\n结果:")
    print(f"  - 成功: {result['success']}")
    print(f"  - 新推文数: {result['new_tweets']}")
    print(f"  - 执行时间: {result['execution_time']:.2f}秒")
    
    # 获取更新后的推文数
    after_count = Tweet.objects.filter(x_account=account).count()
    print(f"  - 数据库中总推文数: {after_count}")
    
    if result['new_tweets'] > 0:
        print("\n✅ 成功获取新推文!")
        # 显示最新的几条推文
        recent_tweets = Tweet.objects.filter(x_account=account).order_by('-posted_at')[:3]
        print("\n最新推文:")
        for tweet in recent_tweets:
            print(f"  - [{tweet.posted_at}] {tweet.content[:50]}...")
    else:
        print("\n⚠️ 未获取到新推文（可能都已存在）")

if __name__ == '__main__':
    test_fetch_24h()
