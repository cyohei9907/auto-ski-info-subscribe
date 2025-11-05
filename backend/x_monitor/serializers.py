from rest_framework import serializers
from .models import XAccount, Tweet, MonitoringLog, AIAnalysis, UserNotification


class XAccountSerializer(serializers.ModelSerializer):
    tweets_count = serializers.SerializerMethodField()
    
    class Meta:
        model = XAccount
        fields = ['id', 'username', 'display_name', 'avatar_url', 'is_active', 
                 'created_at', 'last_checked', 'tweets_count']
        read_only_fields = ['user_id', 'created_at', 'last_checked']
    
    def get_tweets_count(self, obj):
        return obj.tweets.count()


class XAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = XAccount
        fields = ['username']
    
    def validate_username(self, value):
        # Remove @ if present
        username = value.lstrip('@')
        
        # Check if already monitoring this account for this user
        user = self.context['request'].user
        if XAccount.objects.filter(user=user, username=username).exists():
            raise serializers.ValidationError("このアカウントは既に監視対象に追加されています")
        
        return username


class AIAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysis
        fields = ['sentiment', 'summary', 'topics', 'importance_score', 'processed_at']


class TweetSerializer(serializers.ModelSerializer):
    x_account_username = serializers.CharField(source='x_account.username', read_only=True)
    ai_analysis = AIAnalysisSerializer(read_only=True)
    
    class Meta:
        model = Tweet
        fields = ['id', 'tweet_id', 'content', 'media_urls', 'hashtags', 'mentions',
                 'retweet_count', 'like_count', 'reply_count', 'posted_at', 
                 'x_account_username', 'ai_analysis']


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