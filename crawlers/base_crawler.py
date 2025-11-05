"""
Base crawler class for social media platforms
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from utils.logger import crawler_logger


class BaseCrawler(ABC):
    """Abstract base class for social media crawlers"""
    
    def __init__(self, platform_name: str):
        """
        Initialize base crawler
        
        Args:
            platform_name: Name of the social media platform
        """
        self.platform_name = platform_name
        self.logger = crawler_logger
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_user_posts(self, username: str, limit: int = 10) -> List[Dict]:
        """
        Get recent posts from a user
        
        Args:
            username: Username to fetch posts from
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post dictionaries
        """
        pass
    
    def crawl_users(self, usernames: List[str], limit: int = 10) -> Dict[str, List[Dict]]:
        """
        Crawl posts from multiple users
        
        Args:
            usernames: List of usernames to crawl
            limit: Maximum number of posts per user
            
        Returns:
            Dictionary mapping usernames to their posts
        """
        results = {}
        
        if not self.authenticate():
            self.logger.error(f"Failed to authenticate with {self.platform_name}")
            return results
        
        for username in usernames:
            if not username or not username.strip():
                continue
                
            try:
                self.logger.info(f"Crawling posts from {username} on {self.platform_name}")
                posts = self.get_user_posts(username.strip(), limit)
                results[username] = posts
                self.logger.info(f"Retrieved {len(posts)} posts from {username}")
            except Exception as e:
                self.logger.error(f"Failed to crawl {username}: {e}")
                results[username] = []
        
        return results
