"""
Database management utilities
"""
from datetime import datetime
from typing import Dict, List, Optional
from pymongo import MongoClient
from config import Config
from utils.logger import app_logger


class DatabaseManager:
    """MongoDB database manager for storing crawler results"""
    
    def __init__(self):
        """Initialize database connection"""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client[Config.MONGODB_DATABASE]
            self.posts_collection = self.db['posts']
            self.research_collection = self.db['research']
            app_logger.info("Database connection established")
        except Exception as e:
            app_logger.error(f"Failed to connect to database: {e}")
            # Use in-memory storage as fallback
            self.client = None
            self.db = None
            self.posts_collection = None
            self.research_collection = None
    
    def store_post(self, platform: str, username: str, post_data: Dict) -> Optional[str]:
        """
        Store a scraped post
        
        Args:
            platform: Social media platform name
            username: Username of the blogger
            post_data: Post data dictionary
            
        Returns:
            Inserted post ID or None
        """
        if not self.posts_collection:
            app_logger.warning("Database not available, skipping post storage")
            return None
            
        try:
            post_data.update({
                'platform': platform,
                'username': username,
                'created_at': datetime.utcnow(),
                'processed': False
            })
            result = self.posts_collection.insert_one(post_data)
            app_logger.info(f"Stored post from {username} on {platform}")
            return str(result.inserted_id)
        except Exception as e:
            app_logger.error(f"Failed to store post: {e}")
            return None
    
    def store_research(self, post_id: str, research_data: Dict) -> Optional[str]:
        """
        Store AI research results
        
        Args:
            post_id: ID of the related post
            research_data: Research results dictionary
            
        Returns:
            Inserted research ID or None
        """
        if not self.research_collection:
            app_logger.warning("Database not available, skipping research storage")
            return None
            
        try:
            research_data.update({
                'post_id': post_id,
                'created_at': datetime.utcnow()
            })
            result = self.research_collection.insert_one(research_data)
            app_logger.info(f"Stored research for post {post_id}")
            return str(result.inserted_id)
        except Exception as e:
            app_logger.error(f"Failed to store research: {e}")
            return None
    
    def get_unprocessed_posts(self, limit: int = 10) -> List[Dict]:
        """
        Get unprocessed posts for AI research
        
        Args:
            limit: Maximum number of posts to retrieve
            
        Returns:
            List of unprocessed posts
        """
        if not self.posts_collection:
            return []
            
        try:
            posts = list(self.posts_collection.find(
                {'processed': False}
            ).limit(limit))
            return posts
        except Exception as e:
            app_logger.error(f"Failed to retrieve unprocessed posts: {e}")
            return []
    
    def mark_post_processed(self, post_id: str) -> bool:
        """
        Mark a post as processed
        
        Args:
            post_id: Post ID to mark as processed
            
        Returns:
            True if successful, False otherwise
        """
        if not self.posts_collection:
            return False
            
        try:
            from bson.objectid import ObjectId
            self.posts_collection.update_one(
                {'_id': ObjectId(post_id)},
                {'$set': {'processed': True, 'processed_at': datetime.utcnow()}}
            )
            return True
        except Exception as e:
            app_logger.error(f"Failed to mark post as processed: {e}")
            return False
    
    def get_research_results(self, platform: str = None, username: str = None, 
                            limit: int = 50) -> List[Dict]:
        """
        Get research results with optional filters
        
        Args:
            platform: Filter by platform
            username: Filter by username
            limit: Maximum number of results
            
        Returns:
            List of research results
        """
        if not self.research_collection:
            return []
            
        try:
            query = {}
            if platform or username:
                # Join with posts collection to filter
                pipeline = [
                    {'$lookup': {
                        'from': 'posts',
                        'localField': 'post_id',
                        'foreignField': '_id',
                        'as': 'post'
                    }},
                    {'$unwind': '$post'}
                ]
                
                if platform:
                    pipeline.append({'$match': {'post.platform': platform}})
                if username:
                    pipeline.append({'$match': {'post.username': username}})
                    
                pipeline.extend([
                    {'$sort': {'created_at': -1}},
                    {'$limit': limit}
                ])
                
                results = list(self.research_collection.aggregate(pipeline))
            else:
                results = list(self.research_collection.find().sort(
                    'created_at', -1
                ).limit(limit))
            
            return results
        except Exception as e:
            app_logger.error(f"Failed to retrieve research results: {e}")
            return []


# Global database instance
db_manager = DatabaseManager()
