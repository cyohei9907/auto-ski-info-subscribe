#!/usr/bin/env python
"""测试获取当日所有推文功能"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from x_monitor.models import XAccount, Tweet
from x_monitor.services import XMonitorService

def test_fetch_today_tweets():
    """测试获取当日推文"""
    print("=" * 60)
    print("测试: 获取当日所有推文（24小时内）")
    print("=" * 60)
    
    # 获取账户
    account = XAccount.objects.filter(username='skiinfomation').first()
    if not account:
        print("❌ 未找到账户 skiinfomation")
        return
    
    print(f"✓ 找到账户: @{account.username}")
    
    # 清空数据库（测试用）
    old_count = Tweet.objects.filter(x_account=account).count()
    print(f"✓ 数据库中现有推文数: {old_count}")
    
    # 删除旧推文以便测试
    if old_count > 0:
        Tweet.objects.filter(x_account=account).delete()
        print(f"✓ 已删除旧推文，准备重新获取")
    
    # 使用 today_only=True 获取当日推文
    service = XMonitorService()
    print("\n开始获取24小时内的所有推文...")
    result = service.monitor_account(account, today_only=True, max_tweets=50)
    
    print(f"\n结果:")
    print(f"  - 成功: {result['success']}")
    print(f"  - 新推文数: {result['new_tweets']}")
    print(f"  - 执行时间: {result['execution_time']:.2f}秒")
    
    # 获取数据库中的推文
    tweets = Tweet.objects.filter(x_account=account).order_by('-posted_at')
    print(f"  - 数据库中总推文数: {tweets.count()}")
    
    if result['new_tweets'] > 0:
        print("\n✅ 成功获取推文!")
        print("\n最新推文列表:")
        for i, tweet in enumerate(tweets[:10], 1):
            print(f"  {i}. [{tweet.posted_at}] {tweet.content[:50]}...")
    else:
        print("\n⚠️ 未获取到新推文")

if __name__ == '__main__':
    test_fetch_today_tweets()
