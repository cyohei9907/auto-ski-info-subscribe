import tweepy
import logging
from typing import List, Optional
from datetime import datetime, timezone
from django.conf import settings
from django.utils import timezone as django_timezone
from .models import XAccount, Tweet, MonitoringLog

logger = logging.getLogger(__name__)


class XAPIClient:
    """X (Twitter) API クライアント"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """APIクライアントを初期化"""
        try:
            self.client = tweepy.Client(
                bearer_token=settings.X_BEARER_TOKEN,
                consumer_key=settings.X_API_KEY,
                consumer_secret=settings.X_API_SECRET,
                access_token=settings.X_ACCESS_TOKEN,
                access_token_secret=settings.X_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize X API client: {e}")
            
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """ユーザー名からユーザー情報を取得"""
        try:
            user = self.client.get_user(username=username, user_fields=['profile_image_url'])
            if user.data:
                return {
                    'id': user.data.id,
                    'username': user.data.username,
                    'name': user.data.name,
                    'profile_image_url': user.data.profile_image_url
                }
        except Exception as e:
            logger.error(f"Error getting user {username}: {e}")
        return None
    
    def get_recent_tweets(self, user_id: str, max_results: int = 10, since_id: Optional[str] = None) -> List[dict]:
        """最新のツイートを取得"""
        try:
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                since_id=since_id,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations', 'entities'],
                exclude=['retweets', 'replies']
            )
            
            if not tweets.data:
                return []
            
            tweet_list = []
            for tweet in tweets.data:
                tweet_data = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                    'like_count': tweet.public_metrics.get('like_count', 0),
                    'reply_count': tweet.public_metrics.get('reply_count', 0),
                    'hashtags': [],
                    'mentions': [],
                    'media_urls': []
                }
                
                # エンティティの解析
                if hasattr(tweet, 'entities'):
                    entities = tweet.entities
                    if 'hashtags' in entities:
                        tweet_data['hashtags'] = [tag['tag'] for tag in entities['hashtags']]
                    if 'mentions' in entities:
                        tweet_data['mentions'] = [mention['username'] for mention in entities['mentions']]
                
                tweet_list.append(tweet_data)
            
            return tweet_list
            
        except Exception as e:
            logger.error(f"Error getting tweets for user {user_id}: {e}")
            return []


class XMonitorService:
    """X監視サービス"""
    
    def __init__(self):
        self.api_client = XAPIClient()
    
    def monitor_account(self, x_account: XAccount) -> dict:
        """アカウントを監視して新しいツイートを取得"""
        start_time = django_timezone.now()
        
        try:
            # 最新のツイートIDを取得
            latest_tweet = x_account.tweets.first()
            since_id = latest_tweet.tweet_id if latest_tweet else None
            
            # APIからツイートを取得
            tweets_data = self.api_client.get_recent_tweets(
                user_id=x_account.user_id,
                since_id=since_id,
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
            user_info = self.api_client.get_user_by_username(username)
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