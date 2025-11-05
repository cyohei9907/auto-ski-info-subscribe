"""
Tests for crawler modules
"""
import pytest
from crawlers import TwitterCrawler, XiaohongshuCrawler


def test_twitter_crawler_init():
    """Test Twitter crawler initialization"""
    crawler = TwitterCrawler()
    assert crawler.platform_name == 'Twitter'
    assert crawler.client is None  # Not authenticated yet


def test_xiaohongshu_crawler_init():
    """Test Xiaohongshu crawler initialization"""
    crawler = XiaohongshuCrawler()
    assert crawler.platform_name == 'Xiaohongshu'
    assert crawler.base_url == 'https://www.xiaohongshu.com'


def test_crawler_empty_usernames():
    """Test crawler with empty username list"""
    crawler = TwitterCrawler()
    results = crawler.crawl_users([], limit=10)
    assert results == {}
