"""
Twitter (X) crawler implementation
"""
from typing import List, Dict
import tweepy
from config import Config
from .base_crawler import BaseCrawler


class TwitterCrawler(BaseCrawler):
    """Crawler for Twitter/X platform"""
    
    def __init__(self):
        """Initialize Twitter crawler"""
        super().__init__('Twitter')
        self.client = None
        self.api = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Twitter API
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Try Bearer Token authentication (Twitter API v2)
            if Config.TWITTER_BEARER_TOKEN:
                self.client = tweepy.Client(
                    bearer_token=Config.TWITTER_BEARER_TOKEN,
                    wait_on_rate_limit=True
                )
                self.logger.info("Twitter authentication successful (Bearer Token)")
                return True
            
            # Fallback to OAuth 1.0a (API v1.1)
            if all([Config.TWITTER_API_KEY, Config.TWITTER_API_SECRET,
                   Config.TWITTER_ACCESS_TOKEN, Config.TWITTER_ACCESS_TOKEN_SECRET]):
                auth = tweepy.OAuthHandler(
                    Config.TWITTER_API_KEY,
                    Config.TWITTER_API_SECRET
                )
                auth.set_access_token(
                    Config.TWITTER_ACCESS_TOKEN,
                    Config.TWITTER_ACCESS_TOKEN_SECRET
                )
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
                
                # Also create v2 client for better features
                self.client = tweepy.Client(
                    consumer_key=Config.TWITTER_API_KEY,
                    consumer_secret=Config.TWITTER_API_SECRET,
                    access_token=Config.TWITTER_ACCESS_TOKEN,
                    access_token_secret=Config.TWITTER_ACCESS_TOKEN_SECRET,
                    wait_on_rate_limit=True
                )
                
                self.logger.info("Twitter authentication successful (OAuth)")
                return True
            
            self.logger.error("No Twitter credentials configured")
            return False
            
        except Exception as e:
            self.logger.error(f"Twitter authentication failed: {e}")
            return False
    
    def get_user_posts(self, username: str, limit: int = 10) -> List[Dict]:
        """
        Get recent posts from a Twitter user
        
        Args:
            username: Twitter username
            limit: Maximum number of tweets to fetch
            
        Returns:
            List of tweet dictionaries
        """
        posts = []
        
        try:
            if not self.client:
                self.logger.error("Twitter client not initialized")
                return posts
            
            # Get user ID from username
            user = self.client.get_user(username=username)
            if not user or not user.data:
                self.logger.warning(f"User {username} not found")
                return posts
            
            user_id = user.data.id
            
            # Fetch tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(limit, 100),  # API limit
                tweet_fields=['created_at', 'text', 'public_metrics', 'lang'],
                exclude=['retweets', 'replies']
            )
            
            if not tweets or not tweets.data:
                self.logger.info(f"No tweets found for {username}")
                return posts
            
            # Parse tweets
            for tweet in tweets.data:
                post = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'language': getattr(tweet, 'lang', 'unknown'),
                    'metrics': {
                        'likes': tweet.public_metrics.get('like_count', 0),
                        'retweets': tweet.public_metrics.get('retweet_count', 0),
                        'replies': tweet.public_metrics.get('reply_count', 0),
                    } if hasattr(tweet, 'public_metrics') else {}
                }
                posts.append(post)
            
            self.logger.info(f"Retrieved {len(posts)} tweets from @{username}")
            
        except tweepy.errors.TweepyException as e:
            self.logger.error(f"Twitter API error for {username}: {e}")
        except Exception as e:
            self.logger.error(f"Error fetching tweets for {username}: {e}")
        
        return posts
