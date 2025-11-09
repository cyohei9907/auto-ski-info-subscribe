#!/usr/bin/env python
"""
测试认证爬虫
验证是否可以获取更多推文
"""
import os
import sys
import django

# Django setup
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

import logging
from x_monitor.authenticated_scraper import AuthenticatedXScraperClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_authenticated_scraper():
    """测试认证爬虫"""
    username = "skiinfomation"
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing Authenticated Scraper for @{username}")
    logger.info(f"{'='*60}\n")
    
    client = AuthenticatedXScraperClient()
    
    # 检查cookies文件
    if not client.cookies_file.exists():
        logger.error(f"❌ Cookies文件不存在: {client.cookies_file}")
        logger.info("\n请先运行认证设置：")
        logger.info("  docker-compose exec backend python manage.py setup_x_auth")
        logger.info("  或在本地运行：python backend/local_setup_auth.py")
        return
    
    logger.info(f"✓ Cookies文件存在: {client.cookies_file}")
    
    # 测试获取推文
    tweets = client.get_recent_tweets(username, max_results=20)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"结果: 获取到 {len(tweets)} 条推文")
    logger.info(f"{'='*60}\n")
    
    if len(tweets) > 0:
        logger.info("最近的推文：\n")
        for i, tweet in enumerate(tweets[:10], 1):
            logger.info(f"{i}. [{tweet.get('created_at')}] (ID: {tweet.get('id')})")
            logger.info(f"   {tweet.get('text', '')[:80]}...")
            logger.info(f"   💬 {tweet.get('reply_count')} 🔄 {tweet.get('retweet_count')} ❤️ {tweet.get('like_count')}\n")
        
        # 检查是否有今天的推文
        from django.utils import timezone
        today = timezone.now().date()
        today_tweets = [t for t in tweets if t['created_at'].date() == today]
        
        if today_tweets:
            logger.info(f"✓ 成功！找到 {len(today_tweets)} 条今天的推文")
        else:
            logger.info(f"⚠️ 没有今天的推文，最新推文来自: {tweets[0]['created_at']}")
    else:
        logger.error("❌ 没有获取到任何推文")
        logger.info("\n可能的原因：")
        logger.info("1. Cookies已过期，需要重新运行 setup_x_auth")
        logger.info("2. 账号被限制或需要验证")
        logger.info("3. 网络问题")

if __name__ == "__main__":
    test_authenticated_scraper()
