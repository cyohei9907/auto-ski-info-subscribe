#!/usr/bin/env python
"""测试 workaround scraper 返回的数据"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from x_monitor.workaround_scraper import scrape_with_working_method

def test_scraper_output():
    """测试scraper返回的数据"""
    print("=" * 60)
    print("测试 Workaround Scraper 输出")
    print("=" * 60)
    
    tweets = scrape_with_working_method('skiinfomation', max_tweets=10)
    
    print(f"\n找到 {len(tweets)} 条推文\n")
    
    for i, tweet in enumerate(tweets[:3], 1):
        print(f"推文 {i}:")
        print(f"  ID: {tweet.get('id', 'NO_ID')}")
        print(f"  text 字段: '{tweet.get('text', 'NO_TEXT')}'")
        print(f"  text 长度: {len(tweet.get('text', ''))}")
        print(f"  created_at: {tweet.get('created_at', 'NO_TIME')}")
        print(f"  published_at: {tweet.get('published_at', 'NO_TIME')}")
        print(f"\n  所有字段:")
        for key, value in tweet.items():
            if key not in ['html']:
                if isinstance(value, str) and len(value) > 100:
                    print(f"    {key}: {value[:100]}...")
                else:
                    print(f"    {key}: {value}")
        print()

if __name__ == '__main__':
    test_scraper_output()
