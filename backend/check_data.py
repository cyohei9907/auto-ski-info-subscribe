#!/usr/bin/env python
"""检查数据库和API返回的推文数据"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from x_monitor.models import Tweet, XAccount
from django.contrib.auth import get_user_model

User = get_user_model()

def check_tweets_data():
    """检查推文数据"""
    print("=" * 60)
    print("检查数据库中的推文数据")
    print("=" * 60)
    
    # 检查账户
    accounts = XAccount.objects.all()
    print(f"\n账户数: {accounts.count()}")
    
    for account in accounts:
        print(f"\n账户: @{account.username}")
        print(f"  用户: {account.user.username if account.user else 'N/A'}")
        print(f"  ID: {account.id}")
        
        # 检查推文
        tweets = Tweet.objects.filter(x_account=account).order_by('-posted_at')
        print(f"  推文数: {tweets.count()}")
        
        if tweets.exists():
            print(f"\n  最新推文:")
            for i, tweet in enumerate(tweets[:5], 1):
                print(f"    {i}. ID: {tweet.tweet_id}")
                print(f"       时间: {tweet.posted_at}")
                print(f"       内容: {tweet.content[:50]}...")
                print(f"       AI推荐: {tweet.ai_relevant}")
                print()
    
    # 检查用户
    print("\n用户列表:")
    users = User.objects.all()
    for user in users:
        print(f"  - {user.username} (ID: {user.id})")
        user_accounts = XAccount.objects.filter(user=user)
        print(f"    拥有账户: {user_accounts.count()}个")

if __name__ == '__main__':
    check_tweets_data()
