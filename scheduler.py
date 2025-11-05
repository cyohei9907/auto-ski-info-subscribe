"""
Scheduler for periodic crawling tasks
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from config import Config
from crawlers import TwitterCrawler, XiaohongshuCrawler
from ai_research import DeepResearcher
from utils.database import db_manager
from utils.logger import app_logger


class CrawlerScheduler:
    """Scheduler for periodic social media crawling"""
    
    def __init__(self):
        """Initialize the scheduler"""
        self.scheduler = BackgroundScheduler()
        self.twitter_crawler = TwitterCrawler()
        self.xiaohongshu_crawler = XiaohongshuCrawler()
        self.researcher = DeepResearcher()
        self.logger = app_logger
    
    def start(self):
        """Start the scheduler"""
        if not Config.ENABLE_SCHEDULER:
            self.logger.info("Scheduler is disabled in configuration")
            return
        
        # Schedule Twitter crawling
        if Config.TWITTER_TARGET_USERS and any(Config.TWITTER_TARGET_USERS):
            self.scheduler.add_job(
                func=self.crawl_twitter,
                trigger=IntervalTrigger(hours=Config.SCRAPE_INTERVAL_HOURS),
                id='twitter_crawl',
                name='Crawl Twitter posts',
                replace_existing=True
            )
            self.logger.info(
                f"Scheduled Twitter crawling every {Config.SCRAPE_INTERVAL_HOURS} hours"
            )
        
        # Schedule Xiaohongshu crawling
        if Config.XIAOHONGSHU_TARGET_USERS and any(Config.XIAOHONGSHU_TARGET_USERS):
            self.scheduler.add_job(
                func=self.crawl_xiaohongshu,
                trigger=IntervalTrigger(hours=Config.SCRAPE_INTERVAL_HOURS),
                id='xiaohongshu_crawl',
                name='Crawl Xiaohongshu posts',
                replace_existing=True
            )
            self.logger.info(
                f"Scheduled Xiaohongshu crawling every {Config.SCRAPE_INTERVAL_HOURS} hours"
            )
        
        # Schedule AI research processing
        self.scheduler.add_job(
            func=self.process_ai_research,
            trigger=IntervalTrigger(hours=1),
            id='ai_research',
            name='Process AI research',
            replace_existing=True
        )
        self.logger.info("Scheduled AI research processing every 1 hour")
        
        # Start the scheduler
        self.scheduler.start()
        self.logger.info("Scheduler started successfully")
        
        # Run initial crawl
        self.logger.info("Running initial crawl...")
        self.crawl_twitter()
        self.crawl_xiaohongshu()
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        self.logger.info("Scheduler stopped")
    
    def crawl_twitter(self):
        """Crawl Twitter posts from target users"""
        try:
            self.logger.info("Starting Twitter crawl job")
            
            results = self.twitter_crawler.crawl_users(
                Config.TWITTER_TARGET_USERS,
                limit=10
            )
            
            # Store results in database
            for username, posts in results.items():
                for post in posts:
                    db_manager.store_post('Twitter', username, post)
            
            total_posts = sum(len(posts) for posts in results.values())
            self.logger.info(f"Twitter crawl completed: {total_posts} posts retrieved")
            
        except Exception as e:
            self.logger.error(f"Twitter crawl job failed: {e}")
    
    def crawl_xiaohongshu(self):
        """Crawl Xiaohongshu posts from target users"""
        try:
            self.logger.info("Starting Xiaohongshu crawl job")
            
            results = self.xiaohongshu_crawler.crawl_users(
                Config.XIAOHONGSHU_TARGET_USERS,
                limit=10
            )
            
            # Store results in database
            for username, posts in results.items():
                for post in posts:
                    db_manager.store_post('Xiaohongshu', username, post)
            
            total_posts = sum(len(posts) for posts in results.values())
            self.logger.info(f"Xiaohongshu crawl completed: {total_posts} posts retrieved")
            
        except Exception as e:
            self.logger.error(f"Xiaohongshu crawl job failed: {e}")
    
    def process_ai_research(self):
        """Process unprocessed posts with AI research"""
        try:
            self.logger.info("Starting AI research processing")
            
            # Get unprocessed posts
            posts = db_manager.get_unprocessed_posts(limit=10)
            
            if not posts:
                self.logger.info("No unprocessed posts found")
                return
            
            # Analyze each post
            for post in posts:
                try:
                    post_id = str(post.get('_id'))
                    platform = post.get('platform', 'Unknown')
                    
                    # Perform AI analysis
                    analysis = self.researcher.analyze_post(post, platform)
                    
                    # Store research results
                    db_manager.store_research(post_id, analysis)
                    
                    # Mark post as processed
                    db_manager.mark_post_processed(post_id)
                    
                    self.logger.info(f"Processed post {post_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process post: {e}")
            
            self.logger.info(f"AI research processing completed: {len(posts)} posts processed")
            
        except Exception as e:
            self.logger.error(f"AI research job failed: {e}")


# Global scheduler instance
crawler_scheduler = CrawlerScheduler()
