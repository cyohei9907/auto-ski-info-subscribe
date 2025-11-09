#!/usr/bin/env python
"""模拟前端按钮点击 - 获取当日所有推文"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from x_monitor.models import XAccount, Tweet
from x_monitor.services import XMonitorService

def simulate_button_click():
    """模拟前端"当日全て"按钮点击"""
    print("=" * 60)
    print("模拟前端操作: 点击「当日全て」按钮")
    print("=" * 60)
    
    # 获取账户（模拟从前端传来的 account_id）
    account = XAccount.objects.filter(username='skiinfomation').first()
    if not account:
        print("❌ 未找到账户")
        return
    
    print(f"\n账户信息:")
    print(f"  用户名: @{account.username}")
    print(f"  显示名: {account.display_name or 'N/A'}")
    
    # 获取当前推文数
    before_count = Tweet.objects.filter(x_account=account).count()
    print(f"  数据库现有推文: {before_count} 条")
    
    # 执行获取（模拟 views.py 中的 fetch_latest_tweets）
    print(f"\n执行: 获取24小时内的所有推文...")
    service = XMonitorService()
    result = service.monitor_account(account, today_only=True, max_tweets=50)
    
    # 显示结果（模拟前端显示的消息）
    if result.get('success'):
        new_tweets = result.get('new_tweets', 0)
        exec_time = result.get('execution_time', 0)
        
        print(f"\n✅ 成功!")
        print(f"   {new_tweets}条の新しい推文を取得しました（24時間以内）")
        print(f"   执行时间: {exec_time:.2f}秒")
        
        # 显示数据库更新
        after_count = Tweet.objects.filter(x_account=account).count()
        print(f"   数据库推文总数: {before_count} → {after_count}")
        
        if new_tweets > 0:
            print(f"\n新获取的推文:")
            recent_tweets = Tweet.objects.filter(x_account=account).order_by('-posted_at')[:new_tweets]
            for i, tweet in enumerate(recent_tweets, 1):
                import zoneinfo
                tokyo_tz = zoneinfo.ZoneInfo('Asia/Tokyo')
                tweet_tokyo = tweet.posted_at.astimezone(tokyo_tz)
                print(f"   {i}. [{tweet_tokyo.strftime('%m-%d %H:%M')}] {tweet.content[:40]}...")
    else:
        print(f"\n❌ 失败")
        print(f"   推文の取得に失敗しました")

if __name__ == '__main__':
    simulate_button_click()
