#!/usr/bin/env python
"""测试Twitter爬虫"""
import sys
import os
import django

# 设置Django环境
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from x_monitor.services import XScraperClient
import json

def test_scrape():
    client = XScraperClient()
    
    # 测试获取用户信息
    print("\n=== Testing get_user_by_username ===")
    user_info = client.get_user_by_username('skiinfomation')
    if user_info:
        print(json.dumps(user_info, indent=2, ensure_ascii=False))
    else:
        print("Failed to get user info")
    
    # 测试获取推文
    print("\n=== Testing get_recent_tweets ===")
    tweets = client.get_recent_tweets('skiinfomation', max_results=2)
    print(f"Got {len(tweets)} tweets")
    
    for i, tweet in enumerate(tweets, 1):
        print(f"\nTweet {i}:")
        print(f"  ID: {tweet.get('id')}")
        print(f"  Text: {tweet.get('text', '')[:100]}")
        print(f"  Posted: {tweet.get('created_at')}")
        print(f"  Likes: {tweet.get('like_count')}")
        print(f"  Retweets: {tweet.get('retweet_count')}")

if __name__ == '__main__':
    test_scrape()
