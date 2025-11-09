from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class XAccount(models.Model):
    """X(Twitter)アカウント監視設定"""
    
    # 监控间隔选项（分钟）
    INTERVAL_CHOICES = [
        (30, '每30分钟'),
        (60, '每1小时'),
        (240, '每4小时'),
        (720, '每12小时'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='x_accounts')
    username = models.CharField(max_length=255, help_text="X username (without @)")
    display_name = models.CharField(max_length=255, blank=True)
    x_user_id = models.CharField(max_length=255, blank=True, help_text="X user ID")
    avatar_url = models.URLField(blank=True, null=True, default='https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png')
    is_active = models.BooleanField(default=True)
    monitoring_interval = models.IntegerField(
        choices=INTERVAL_CHOICES, 
        default=240,
        help_text="监控间隔（分钟）"
    )
    ai_filter_enabled = models.BooleanField(default=False, help_text="智能推荐开关")
    fetch_from_date = models.DateField(blank=True, null=True, help_text="开始拉取推文的日期")
    fetch_to_date = models.DateField(blank=True, null=True, help_text="结束拉取推文的日期")
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
    ai_analyzed = models.BooleanField(default=False, help_text="是否已进行AI分析")
    ai_relevant = models.BooleanField(default=False, help_text="AI判断是否相关")
    ai_summary = models.TextField(blank=True, help_text="AI生成的摘要")
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
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='success')
    tweets_found = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    execution_time = models.FloatField(help_text="Execution time in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Log for @{self.x_account.username} - {self.result}"


class AIPromptRule(models.Model):
    """AI推荐规则"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_prompt_rules')
    name = models.CharField(max_length=255, help_text="规则名称")
    prompt = models.TextField(help_text="AI筛选提示词")
    target_accounts = models.ManyToManyField(
        XAccount, 
        related_name='ai_rules',
        blank=True,
        help_text="应用此规则的Twitter账号（为空表示应用到所有账号）"
    )
    is_active = models.BooleanField(default=True, help_text="是否启用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_applied = models.DateTimeField(null=True, blank=True, help_text="最后应用时间")
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.user.email}"


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


class RecommendedTweet(models.Model):
    """AI推荐的推文"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommended_tweets')
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='recommendations')
    prompt_rule = models.ForeignKey(
        'AIPromptRule', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='recommended_tweets',
        help_text="使用的推荐规则"
    )
    ai_reason = models.TextField(help_text="AI推荐理由")
    relevance_score = models.FloatField(default=0.0, help_text="相关度评分 0-1")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'tweet', 'prompt_rule']
        
    def __str__(self):
        return f"Recommended Tweet {self.tweet.tweet_id} for {self.user.email}"


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