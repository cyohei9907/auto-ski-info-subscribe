import logging
import re
import asyncio
import random
import time
from typing import List, Optional, Dict
from datetime import datetime, timezone
from django.conf import settings
from django.utils import timezone as django_timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from .models import XAccount, Tweet, MonitoringLog

logger = logging.getLogger(__name__)

# 临时使用workaround scraper（因为authenticated_scraper被X.com检测）
USE_WORKAROUND = True  # 临时启用workaround
if USE_WORKAROUND:
    logger.info("🔧 Using workaround scraper (temporary fix for X.com anti-automation)")
    from .workaround_scraper import scrape_with_working_method
    SCRAPER_AVAILABLE = True
else:
    # 根据配置选择爬虫实现
    USE_AUTHENTICATED = getattr(settings, 'USE_AUTHENTICATED_SCRAPER', False)
    if USE_AUTHENTICATED:
        logger.info("Using authenticated X.com scraper (requires cookies, can access full timeline)")
        try:
            from .authenticated_scraper import AuthenticatedXScraperClient
            SCRAPER_AVAILABLE = True
        except ImportError as e:
            logger.warning(f"Failed to import authenticated scraper: {e}, falling back to guest scraper")
            SCRAPER_AVAILABLE = False
    else:
        logger.info("Using guest X.com scraper (limited to visible tweets)")
        SCRAPER_AVAILABLE = False



class XScraperClient:
    """X (Twitter) Webスクレイピングクライアント"""
    
    def __init__(self):
        self.base_url = "https://x.com"  # 使用新域名 x.com
    
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
    
    def _add_random_delay(self):
        """添加随机延迟以避免被检测为机器人 (15-30秒)"""
        delay = random.uniform(15, 30)
        logger.info(f"Waiting {delay:.1f} seconds before next request...")
        time.sleep(delay)
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """ユーザー名からユーザー情報をスクレイピング"""
        try:
            # 添加随机延迟
            self._add_random_delay()
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    extra_http_headers={
                        'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
                    }
                )
                page = context.new_page()
                
                # ユーザープロフィールページにアクセス
                url = f"{self.base_url}/{username}"
                logger.info(f"Navigating to user profile: {url}")
                
                try:
                    page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    # 等待用户信息加载
                    page.wait_for_selector('[data-testid="UserName"]', timeout=20000)
                except PlaywrightTimeoutError as e:
                    logger.error(f"Timeout loading user profile: {e}")
                    browser.close()
                    return None
                
                # 随机等待 2-5 秒
                wait_time = random.uniform(2000, 5000)
                page.wait_for_timeout(int(wait_time))
                
                # HTMLを取得
                html = page.content()
                soup = BeautifulSoup(html, 'lxml')
                
                # ユーザー名を取得（displayName）
                display_name = username
                try:
                    # 尝试多种选择器获取显示名称
                    name_elem = soup.select_one('[data-testid="UserName"] span') or \
                               soup.select_one('[data-testid="UserProfileHeader_Items"] span')
                    if name_elem:
                        # 获取第一个span的文本（通常是display name）
                        display_name = name_elem.get_text().strip()
                except Exception as e:
                    logger.warning(f"Failed to extract display name: {e}")
                
                # プロフィール画像を取得（多种方法尝试）
                avatar_url = None
                try:
                    # 方法1: 查找包含profile_images的img标签
                    avatar_elem = soup.find('img', src=re.compile(r'profile_images'))
                    if avatar_elem and 'src' in avatar_elem.attrs:
                        avatar_url = avatar_elem['src']
                        # 获取更高清版本（将_normal替换为_400x400）
                        avatar_url = avatar_url.replace('_normal', '_400x400')
                    
                    # 方法2: 查找data-testid="UserAvatar-Container"下的img
                    if not avatar_url:
                        avatar_container = soup.find('div', {'data-testid': 'UserAvatar-Container-'}) or \
                                         soup.find('div', class_=re.compile(r'css.*Avatar'))
                        if avatar_container:
                            avatar_elem = avatar_container.find('img')
                            if avatar_elem and 'src' in avatar_elem.attrs:
                                avatar_url = avatar_elem['src'].replace('_normal', '_400x400')
                    
                    # 方法3: 如果还没找到，使用默认头像
                    if not avatar_url:
                        avatar_url = 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png'
                        
                except Exception as e:
                    logger.warning(f"Failed to extract avatar: {e}")
                    avatar_url = 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png'
                
                browser.close()
                
                logger.info(f"User info scraped - username: {username}, display_name: {display_name}, avatar: {avatar_url}")
                
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
    
    def get_recent_tweets(self, username: str, max_results: int = 10, hours: int = 6) -> List[Dict]:
        """最新のツイートをスクレイピング（指定時間以内のツイートのみ）
        
        Args:
            username: X.com用户名
            max_results: 最大取得ツイート数
            hours: 時間範囲（デフォルト: 6時間）
        """
        try:
            # 如果启用了workaround，使用它
            if USE_WORKAROUND:
                logger.info(f"使用workaround scraper获取 @{username} 的推文")
                tweets = scrape_with_working_method(username, max_tweets=max_results)
                
                # 过滤指定时间内的推文
                time_ago = django_timezone.now() - django_timezone.timedelta(hours=hours)
                recent_tweets = []
                for tweet in tweets:
                    try:
                        tweet_time = django_timezone.datetime.fromisoformat(tweet['published_at'].replace('Z', '+00:00'))
                        if tweet_time >= time_ago:
                            recent_tweets.append(tweet)
                    except:
                        pass
                
                logger.info(f"Workaround scraper找到 {len(tweets)} 条推文，其中 {len(recent_tweets)} 条在{hours}小时内")
                return recent_tweets
            
            # 原有逻辑...
            # 添加随机延迟
            self._add_random_delay()
            
            # 计算6小时前的时间
            six_hours_ago = django_timezone.now() - django_timezone.timedelta(hours=6)
            logger.info(f"Fetching tweets since: {six_hours_ago}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-gpu',
                        '--disable-software-rasterizer'
                    ]
                )
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    extra_http_headers={
                        'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    }
                )
                
                # 禁用字体、样式表等非必要资源以加快加载速度（保留图片和视频）
                def block_resources(route):
                    resource_type = route.request.resource_type
                    if resource_type in ['font', 'stylesheet']:
                        route.abort()
                    else:
                        route.continue_()
                
                context.route("**/*", block_resources)
                page = context.new_page()
                
                # ユーザーのタイムラインにアクセス
                url = f"{self.base_url}/{username}"
                logger.info(f"Navigating to {url}")
                
                try:
                    # 使用更长的超时和更宽松的等待条件
                    page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    # 等待推文加载
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=30000)
                except PlaywrightTimeoutError as e:
                    logger.error(f"Timeout waiting for page or tweets: {e}")
                    # 保存截图用于调试
                    screenshot_path = f"/tmp/x_scrape_error_{username}.png"
                    page.screenshot(path=screenshot_path)
                    logger.error(f"Screenshot saved to {screenshot_path}")
                    browser.close()
                    return []
                
                # 最小化滚动：只滚动一次，快速获取最新推文
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                # 短暂等待内容加载
                wait_time = random.uniform(1000, 2000)
                page.wait_for_timeout(int(wait_time))
                
                # HTMLを取得
                html = page.content()
                soup = BeautifulSoup(html, 'lxml')
                
                # ツイートを解析
                tweets = []
                tweet_articles = soup.find_all('article', {'data-testid': 'tweet'})
                logger.info(f"Found {len(tweet_articles)} tweet articles on page")
                
                # 统计：发现了多少6小时内的推文
                recent_count = 0
                old_count = 0
                
                if len(tweet_articles) == 0:
                    # 保存HTML用于调试
                    with open(f'/tmp/x_page_{username}.html', 'w', encoding='utf-8') as f:
                        f.write(html)
                    logger.warning(f"No tweets found. HTML saved to /tmp/x_page_{username}.html")
                
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
                        
                        # 6時間以内のツイートのみ処理
                        if posted_at and posted_at < six_hours_ago:
                            old_count += 1
                            logger.info(f"Tweet {tweet_id} is older than 6 hours ({posted_at}), skipping")
                            continue
                        
                        recent_count += 1
                        
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
                        
                        tweet_data = {
                            'id': tweet_id,
                            'text': tweet_text,
                            'created_at': posted_at,
                            'retweet_count': retweet_count,
                            'like_count': like_count,
                            'reply_count': reply_count,
                            'hashtags': hashtags,
                            'mentions': mentions,
                            'media_urls': []
                        }
                        tweets.append(tweet_data)
                        logger.info(f"Parsed tweet {tweet_id}: {tweet_text[:50]}...")
                        
                    except Exception as e:
                        logger.warning(f"Error parsing individual tweet: {e}")
                        continue
                
                browser.close()
                logger.info(f"Successfully scraped {len(tweets)} tweets for @{username} (recent: {recent_count}, old: {old_count})")
                return tweets
                
        except Exception as e:
            logger.error(f"Error scraping tweets for user {username}: {e}")
            return []
    
    def get_today_tweets(self, username: str) -> List[Dict]:
        """当日のツイートのみを取得（24小時以内）"""
        try:
            # 如果启用了workaround，使用它获取更多推文
            if USE_WORKAROUND:
                logger.info(f"使用workaround scraper获取 @{username} 当日推文")
                tweets = scrape_with_working_method(username, max_tweets=50)  # 获取更多推文
                
                # 过滤24小时内的推文
                twenty_four_hours_ago = django_timezone.now() - django_timezone.timedelta(hours=24)
                today_tweets = []
                for tweet in tweets:
                    try:
                        tweet_time = django_timezone.datetime.fromisoformat(tweet['published_at'].replace('Z', '+00:00'))
                        if tweet_time >= twenty_four_hours_ago:
                            today_tweets.append(tweet)
                    except:
                        pass
                
                logger.info(f"Workaround scraper找到 {len(tweets)} 条推文，其中 {len(today_tweets)} 条在24小时内")
                return today_tweets
            
            # 原有逻辑（作为后备）
            all_tweets = self.get_recent_tweets(username, max_results=50)
            
            # 今日の日付を取得
            today = django_timezone.now().date()
            
            # 当日のツイートのみをフィルタリング
            today_tweets = [
                tweet for tweet in all_tweets 
                if tweet['created_at'].date() == today
            ]
            
            logger.info(f"Found {len(today_tweets)} tweets today for @{username}")
            return today_tweets
            
        except Exception as e:
            logger.error(f"Error getting today's tweets for user {username}: {e}")
            return []


class XMonitorService:
    """X監視サービス"""
    
    def __init__(self):
        # 根据配置选择爬虫实现
        if USE_WORKAROUND:
            self.scraper_client = XScraperClient()  # 使用基础client，但get_recent_tweets会调用workaround
            logger.info("XMonitorService initialized with workaround scraper")
        elif 'USE_AUTHENTICATED' in globals() and USE_AUTHENTICATED and SCRAPER_AVAILABLE:
            self.scraper_client = AuthenticatedXScraperClient()
            logger.info("XMonitorService initialized with authenticated scraper")
        else:
            self.scraper_client = XScraperClient()
            logger.info("XMonitorService initialized with guest scraper")
    
    def monitor_account(self, x_account: XAccount, today_only: bool = False, max_tweets: int = 20, hours: int = 6) -> dict:
        """アカウントを監視して新しいツイートを取得
        
        Args:
            x_account: 監視するXアカウント
            today_only: Trueの場合、当日のツイートのみを取得
            max_tweets: 取得する最大ツイート数（デフォルト: 20）
            hours: 時間範囲（デフォルト: 6時間、today_onlyがFalseの場合のみ有効）
        """
        start_time = django_timezone.now()
        
        try:
            # Webスクレイピングでツイートを取得
            if today_only:
                tweets_data = self.scraper_client.get_today_tweets(
                    username=x_account.username
                )
            else:
                tweets_data = self.scraper_client.get_recent_tweets(
                    username=x_account.username,
                    max_results=max_tweets,
                    hours=hours
                )
            
            new_tweets_count = 0
            
            # 不再从推文中更新账户头像
            # 头像应该只在首次添加账户时从用户资料页获取，之后不再变更
            
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