import logging
import re
import asyncio
from typing import List, Optional, Dict
from datetime import datetime, timezone
from django.conf import settings
from django.utils import timezone as django_timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from .models import XAccount, Tweet, MonitoringLog

logger = logging.getLogger(__name__)


class XScraperClient:
    """X (Twitter) Webスクレイピングクライアント"""
    
    def __init__(self):
        self.base_url = "https://twitter.com"
    
    def _extract_tweet_id(self, tweet_url: str) -> Optional[str]:
        """ツイートURLからIDを抽出"""
        match = re.search(r'/status/(\d+)', tweet_url)
        return match.group(1) if match else None
    
    def _parse_tweet_time(self, time_str: str) -> datetime:
        """相対時間を絶対時間に変換"""
        now = django_timezone.now()
        
        # "2時間" -> 2時間前
        if '時間' in time_str or 'h' in time_str:
            hours = int(re.search(r'\d+', time_str).group())
            return now - django_timezone.timedelta(hours=hours)
        # "15分" -> 15分前
        elif '分' in time_str or 'm' in time_str:
            minutes = int(re.search(r'\d+', time_str).group())
            return now - django_timezone.timedelta(minutes=minutes)
        # "30秒" -> 30秒前
        elif '秒' in time_str or 's' in time_str:
            seconds = int(re.search(r'\d+', time_str).group())
            return now - django_timezone.timedelta(seconds=seconds)
        # "3日" -> 3日前
        elif '日' in time_str or 'd' in time_str:
            days = int(re.search(r'\d+', time_str).group())
            return now - django_timezone.timedelta(days=days)
        else:
            return now
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """ユーザー名からユーザー情報をスクレイピング"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # ユーザープロフィールページにアクセス
                url = f"{self.base_url}/{username}"
                page.goto(url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(2000)  # 2秒待機
                
                # HTMLを取得
                html = page.content()
                soup = BeautifulSoup(html, 'lxml')
                
                # ユーザー名を取得
                display_name_elem = soup.find('div', {'data-testid': 'UserName'})
                display_name = display_name_elem.get_text() if display_name_elem else username
                
                # プロフィール画像を取得
                avatar_elem = soup.find('img', {'alt': re.compile(f'.*{username}.*', re.IGNORECASE)})
                avatar_url = avatar_elem['src'] if avatar_elem and 'src' in avatar_elem.attrs else None
                
                browser.close()
                
                # ユーザーIDを生成(スクレイピングではユーザーIDを取得できないため、ユーザー名をIDとして使用)
                return {
                    'id': username,  # ユーザー名をIDとして使用
                    'username': username,
                    'name': display_name,
                    'profile_image_url': avatar_url
                }
                
        except Exception as e:
            logger.error(f"Error scraping user {username}: {e}")
            return None
    
    def get_recent_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """最新のツイートをスクレイピング"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # ユーザーのタイムラインにアクセス
                url = f"{self.base_url}/{username}"
                page.goto(url, wait_until='networkidle', timeout=30000)
                
                # ページをスクロールしてツイートを読み込む
                for _ in range(3):
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_timeout(1000)
                
                # HTMLを取得
                html = page.content()
                soup = BeautifulSoup(html, 'lxml')
                
                # ツイートを解析
                tweets = []
                tweet_articles = soup.find_all('article', {'data-testid': 'tweet'})
                
                for article in tweet_articles[:max_results]:
                    try:
                        # ツイートテキスト
                        tweet_text_elem = article.find('div', {'data-testid': 'tweetText'})
                        tweet_text = tweet_text_elem.get_text() if tweet_text_elem else ""
                        
                        # ツイートID (URLから取得)
                        tweet_link = article.find('a', href=re.compile(r'/status/\d+'))
                        tweet_id = None
                        if tweet_link and 'href' in tweet_link.attrs:
                            tweet_id = self._extract_tweet_id(tweet_link['href'])
                        
                        if not tweet_id:
                            continue
                        
                        # 投稿時間
                        time_elem = article.find('time')
                        posted_at = None
                        if time_elem and 'datetime' in time_elem.attrs:
                            posted_at = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                        else:
                            # 相対時間から推定
                            time_text = time_elem.get_text() if time_elem else ""
                            posted_at = self._parse_tweet_time(time_text)
                        
                        # ハッシュタグとメンション
                        hashtags = [tag.get_text()[1:] for tag in article.find_all('a', href=re.compile(r'/hashtag/'))]
                        mentions = [mention.get_text()[1:] for mention in article.find_all('a', href=re.compile(r'/[^/]+$')) if mention.get_text().startswith('@')]
                        
                        # エンゲージメント指標
                        reply_count = 0
                        retweet_count = 0
                        like_count = 0
                        
                        # 返信数
                        reply_elem = article.find('button', {'data-testid': 'reply'})
                        if reply_elem:
                            reply_text = reply_elem.get_text()
                            reply_match = re.search(r'\d+', reply_text)
                            reply_count = int(reply_match.group()) if reply_match else 0
                        
                        # リツイート数
                        retweet_elem = article.find('button', {'data-testid': 'retweet'})
                        if retweet_elem:
                            retweet_text = retweet_elem.get_text()
                            retweet_match = re.search(r'\d+', retweet_text)
                            retweet_count = int(retweet_match.group()) if retweet_match else 0
                        
                        # いいね数
                        like_elem = article.find('button', {'data-testid': 'like'})
                        if like_elem:
                            like_text = like_elem.get_text()
                            like_match = re.search(r'\d+', like_text)
                            like_count = int(like_match.group()) if like_match else 0
                        
                        tweets.append({
                            'id': tweet_id,
                            'text': tweet_text,
                            'created_at': posted_at,
                            'retweet_count': retweet_count,
                            'like_count': like_count,
                            'reply_count': reply_count,
                            'hashtags': hashtags,
                            'mentions': mentions,
                            'media_urls': []
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error parsing individual tweet: {e}")
                        continue
                
                browser.close()
                return tweets
                
        except Exception as e:
            logger.error(f"Error scraping tweets for user {username}: {e}")
            return []


class XMonitorService:
    """X監視サービス"""
    
    def __init__(self):
        self.scraper_client = XScraperClient()
    
    def monitor_account(self, x_account: XAccount) -> dict:
        """アカウントを監視して新しいツイートを取得"""
        start_time = django_timezone.now()
        
        try:
            # Webスクレイピングでツイートを取得
            tweets_data = self.scraper_client.get_recent_tweets(
                username=x_account.username,
                max_results=20
            )
            
            new_tweets_count = 0
            
            # 新しいツイートをデータベースに保存
            for tweet_data in tweets_data:
                if not Tweet.objects.filter(tweet_id=tweet_data['id']).exists():
                    Tweet.objects.create(
                        x_account=x_account,
                        tweet_id=tweet_data['id'],
                        content=tweet_data['text'],
                        hashtags=tweet_data['hashtags'],
                        mentions=tweet_data['mentions'],
                        media_urls=tweet_data['media_urls'],
                        retweet_count=tweet_data['retweet_count'],
                        like_count=tweet_data['like_count'],
                        reply_count=tweet_data['reply_count'],
                        posted_at=tweet_data['created_at']
                    )
                    new_tweets_count += 1
            
            # アカウントの最終チェック時刻を更新
            x_account.last_checked = django_timezone.now()
            x_account.save()
            
            # ログを記録
            execution_time = (django_timezone.now() - start_time).total_seconds()
            log_result = 'success' if new_tweets_count > 0 else 'no_new_tweets'
            
            MonitoringLog.objects.create(
                x_account=x_account,
                result=log_result,
                tweets_found=new_tweets_count,
                execution_time=execution_time
            )
            
            return {
                'success': True,
                'new_tweets': new_tweets_count,
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = (django_timezone.now() - start_time).total_seconds()
            
            # エラーログを記録
            MonitoringLog.objects.create(
                x_account=x_account,
                result='error',
                tweets_found=0,
                error_message=str(e),
                execution_time=execution_time
            )
            
            logger.error(f"Error monitoring account @{x_account.username}: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            }
    
    def setup_account_monitoring(self, username: str) -> Optional[dict]:
        """アカウント監視のセットアップ"""
        try:
            user_info = self.scraper_client.get_user_by_username(username)
            if not user_info:
                return None
                
            return {
                'user_id': user_info['id'],
                'username': user_info['username'],
                'display_name': user_info['name'],
                'avatar_url': user_info['profile_image_url']
            }
        except Exception as e:
            logger.error(f"Error setting up monitoring for @{username}: {e}")
            return None