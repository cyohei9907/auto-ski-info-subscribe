from rest_framework import serializers
from .models import XAccount, Tweet, MonitoringLog, AIAnalysis, UserNotification, RecommendedTweet


class XAccountSerializer(serializers.ModelSerializer):
    tweets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = XAccount
        fields = ['id', 'username', 'display_name', 'avatar_url', 'is_active', 
                 'ai_filter_enabled', 'fetch_from_date', 'fetch_to_date',
                 'created_at', 'last_checked', 'tweets_count']
        read_only_fields = ['created_at', 'last_checked']
    
    def get_tweets_count(self, obj):
        return obj.tweets.count()


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


class RecommendedTweetSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer(read_only=True)
    
    class Meta:
        model = RecommendedTweet
        fields = ['id', 'tweet', 'ai_reason', 'relevance_score', 'is_read', 'created_at']