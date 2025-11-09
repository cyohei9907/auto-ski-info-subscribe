from rest_framework import serializers
from .models import (
    XAccount, Tweet, MonitoringLog, AIAnalysis, 
    UserNotification, RecommendedTweet, AIPromptRule
)


class XAccountSerializer(serializers.ModelSerializer):
    tweets_count = serializers.SerializerMethodField()
    monitoring_interval_display = serializers.SerializerMethodField()
    
    class Meta:
        model = XAccount
        fields = ['id', 'username', 'display_name', 'avatar_url', 'is_active', 
                 'monitoring_interval', 'monitoring_interval_display',
                 'ai_filter_enabled', 'fetch_from_date', 'fetch_to_date',
                 'created_at', 'last_checked', 'tweets_count']
        read_only_fields = ['created_at', 'last_checked', 'username', 'display_name', 'avatar_url']
    
    def get_tweets_count(self, obj):
        return obj.tweets.count()
    
    def get_monitoring_interval_display(self, obj):
        return obj.get_monitoring_interval_display()


class XAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = XAccount
        fields = ['username']
    
    def validate_username(self, value):
        import re
        
        # Extract username from URL if full URL is provided
        # Supports: https://x.com/username, https://twitter.com/username, @username, username
        url_pattern = r'(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)'
        match = re.search(url_pattern, value)
        
        if match:
            username = match.group(1)
        else:
            # Remove @ if present
            username = value.lstrip('@')
        
        # Validate username format (Twitter usernames: alphanumeric and underscore, 1-15 chars)
        if not re.match(r'^[a-zA-Z0-9_]{1,15}$', username):
            raise serializers.ValidationError(
                'Invalid username format. Twitter usernames must be 1-15 characters (letters, numbers, underscore only).'
            )
        
        return username


class AIAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysis
        fields = ['sentiment', 'summary', 'topics', 'importance_score', 'processed_at']


class TweetSerializer(serializers.ModelSerializer):
    x_account_username = serializers.CharField(source='x_account.username', read_only=True)
    x_account_display_name = serializers.CharField(source='x_account.display_name', read_only=True)
    x_account_avatar = serializers.CharField(source='x_account.avatar_url', read_only=True)
    ai_analysis = AIAnalysisSerializer(read_only=True)
    tweet_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Tweet
        fields = ['id', 'tweet_id', 'content', 'media_urls', 'hashtags', 'mentions',
                 'retweet_count', 'like_count', 'reply_count', 'posted_at', 
                 'x_account_username', 'x_account_display_name', 'x_account_avatar',
                 'ai_analyzed', 'ai_relevant', 'ai_summary', 'ai_analysis', 'tweet_url']
    
    def get_tweet_url(self, obj):
        return f"https://twitter.com/{obj.x_account.username}/status/{obj.tweet_id}"


class MonitoringLogSerializer(serializers.ModelSerializer):
    x_account_username = serializers.CharField(source='x_account.username', read_only=True)
    
    class Meta:
        model = MonitoringLog
        fields = ['id', 'result', 'tweets_found', 'error_message', 
                 'execution_time', 'created_at', 'x_account_username']


class UserNotificationSerializer(serializers.ModelSerializer):
    tweet_content = serializers.CharField(source='tweet.content', read_only=True)
    
    class Meta:
        model = UserNotification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 
                 'created_at', 'tweet_content']


class AIPromptRuleSerializer(serializers.ModelSerializer):
    recommended_count = serializers.SerializerMethodField()
    target_accounts = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=XAccount.objects.none(),
        required=False,
        allow_empty=True
    )
    target_account_details = serializers.SerializerMethodField()
    
    class Meta:
        model = AIPromptRule
        fields = ['id', 'name', 'prompt', 'target_accounts', 'target_account_details',
                 'is_active', 'created_at', 'updated_at', 'last_applied', 'recommended_count']
        read_only_fields = ['created_at', 'updated_at', 'last_applied']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self.fields['target_accounts'].queryset = XAccount.objects.filter(user=request.user)
    
    def get_recommended_count(self, obj):
        """获取该规则推荐的推文数量"""
        return obj.recommended_tweets.count()
    
    def get_target_account_details(self, obj):
        """获取关联账号的详细信息"""
        return [
            {
                'id': account.id,
                'username': account.username,
                'display_name': account.display_name,
                'avatar_url': account.avatar_url
            }
            for account in obj.target_accounts.all()
        ]


class RecommendedTweetSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer(read_only=True)
    prompt_rule_name = serializers.CharField(source='prompt_rule.name', read_only=True, allow_null=True)
    
    class Meta:
        model = RecommendedTweet
        fields = ['id', 'tweet', 'prompt_rule_name', 'ai_reason', 
                 'relevance_score', 'is_read', 'created_at']