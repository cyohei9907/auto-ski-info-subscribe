#!/usr/bin/env python
"""
测试脚本：验证爬虫只获取最近6小时内的推文
"""
import os
import sys
import django

# Django setup
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from x_monitor.services import XScraperClient
from django.utils import timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_6hour_filter():
    """测试6小时过滤功能"""
    scraper = XScraperClient()
    
    # 测试账号
    username = "skiinfomation"
    
    logger.info(f"Testing 6-hour filter for @{username}")
    logger.info(f"Current time: {timezone.now()}")
    logger.info(f"Will fetch tweets since: {timezone.now() - timezone.timedelta(hours=6)}")
    
    # 获取推文
    tweets = scraper.get_recent_tweets(username, max_results=20)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Total tweets within 6 hours: {len(tweets)}")
    logger.info(f"{'='*50}\n")
    
    if tweets:
        for i, tweet in enumerate(tweets, 1):
            time_diff = timezone.now() - tweet['created_at']
            hours = time_diff.total_seconds() / 3600
            
            logger.info(f"{i}. Tweet ID: {tweet['id']}")
            logger.info(f"   Time: {tweet['created_at']}")
            logger.info(f"   Age: {hours:.1f} hours ago")
            logger.info(f"   Text: {tweet['text'][:100]}...")
            logger.info(f"   Engagement: 💬{tweet['reply_count']} 🔄{tweet['retweet_count']} ❤️{tweet['like_count']}")
            logger.info("")
    else:
        logger.warning("No tweets found in the last 6 hours")
    
    return tweets

if __name__ == "__main__":
    test_6hour_filter()
