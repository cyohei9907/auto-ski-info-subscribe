#!/usr/bin/env python
"""检查推文内容"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from x_monitor.models import Tweet

def check_tweet_content():
    """检查推文内容字段"""
    print("=" * 60)
    print("检查推文内容")
    print("=" * 60)
    
    tweets = Tweet.objects.all().order_by('-posted_at')[:5]
    
    for i, tweet in enumerate(tweets, 1):
        print(f"\n推文 {i}:")
        print(f"  ID: {tweet.tweet_id}")
        print(f"  内容长度: {len(tweet.content)} 字符")
        print(f"  内容: '{tweet.content}'")
        print(f"  内容repr: {repr(tweet.content)}")
        print(f"  时间: {tweet.posted_at}")

if __name__ == '__main__':
    check_tweet_content()
