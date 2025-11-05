from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class XAccount(models.Model):
    """X(Twitter)アカウント監視設定"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='x_accounts')
    username = models.CharField(max_length=255, help_text="X username (without @)")
    display_name = models.CharField(max_length=255, blank=True)
    x_user_id = models.CharField(max_length=255, blank=True, help_text="X user ID")
    avatar_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_checked = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'username']
        
    def __str__(self):
        return f"@{self.username} monitored by {self.user.email}"


class Tweet(models.Model):
    """取得したツイート"""
    x_account = models.ForeignKey(XAccount, on_delete=models.CASCADE, related_name='tweets')
    tweet_id = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    media_urls = models.JSONField(default=list, blank=True)
    hashtags = models.JSONField(default=list, blank=True)
    mentions = models.JSONField(default=list, blank=True)
    retweet_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    is_retweet = models.BooleanField(default=False)
    original_tweet_id = models.CharField(max_length=255, blank=True, null=True)
    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-posted_at']
        
    def __str__(self):
        return f"Tweet {self.tweet_id} from @{self.x_account.username}"


class MonitoringLog(models.Model):
    """監視ログ"""
    RESULT_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
        ('no_new_tweets', 'No New Tweets'),
    ]
    
    x_account = models.ForeignKey(XAccount, on_delete=models.CASCADE, related_name='logs')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    tweets_found = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    execution_time = models.FloatField(help_text="Execution time in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Log for @{self.x_account.username} - {self.result}"


class AIAnalysis(models.Model):
    """AI分析結果"""
    tweet = models.OneToOneField(Tweet, on_delete=models.CASCADE, related_name='ai_analysis')
    sentiment = models.CharField(max_length=20, blank=True)  # positive, negative, neutral
    summary = models.TextField(blank=True)
    topics = models.JSONField(default=list, blank=True)
    importance_score = models.FloatField(default=0.0)  # 0-1
    processed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"AI Analysis for Tweet {self.tweet.tweet_id}"


class UserNotification(models.Model):
    """ユーザー通知"""
    TYPE_CHOICES = [
        ('new_tweet', 'New Tweet'),
        ('important_tweet', 'Important Tweet'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Notification for {self.user.email}: {self.title}"