#!/usr/bin/env python
"""测试推文时间解析"""
import os
import sys
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from x_monitor.workaround_scraper import scrape_with_working_method
from django.utils import timezone as django_timezone

def test_time_parsing():
    """测试时间解析"""
    print("=" * 60)
    print("测试: 检查推文时间解析")
    print("=" * 60)
    
    tweets = scrape_with_working_method('skiinfomation', max_tweets=20)
    
    print(f"\n找到 {len(tweets)} 条推文\n")
    
    now = django_timezone.now()
    six_hours_ago = now - django_timezone.timedelta(hours=6)
    
    for i, tweet in enumerate(tweets, 1):
        tweet_id = tweet.get('id', 'NO_ID')
        created_at = tweet.get('created_at', 'NO_TIME')
        published_at = tweet.get('published_at', 'NO_TIME')
        text_preview = tweet.get('text', '')[:50]
        
        print(f"{i}. ID: {tweet_id}")
        print(f"   created_at: {created_at}")
        print(f"   published_at: {published_at}")
        
        # 尝试解析时间并检查是否在6小时内
        if published_at != 'NO_TIME':
            try:
                tweet_time = django_timezone.datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                hours_ago = (now - tweet_time).total_seconds() / 3600
                in_range = "✅ 在6小时内" if tweet_time >= six_hours_ago else f"❌ {hours_ago:.1f}小时前"
                print(f"   解析时间: {tweet_time} ({in_range})")
            except Exception as e:
                print(f"   ⚠️ 时间解析失败: {e}")
        
        print(f"   文本: {text_preview}...")
        print()

if __name__ == '__main__':
    test_time_parsing()
