from rest_framework import serializers
from x_monitor.models import Tweet, AIAnalysis, XAccount


class MCPTweetResourceSerializer(serializers.ModelSerializer):
    """
    MCP Resource serializer for tweets with AI analysis.
    
    Follows MCP protocol specification for resource representation.
    """
    # MCP standard fields
    uri = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    mimeType = serializers.SerializerMethodField()
    
    # Tweet content
    text = serializers.CharField(source='content')
    
    # Metadata with AI analysis
    metadata = serializers.SerializerMethodField()
    
    class Meta:
        model = Tweet
        fields = [
            'uri',
            'name',
            'description',
            'mimeType',
            'text',
            'metadata',
        ]
    
    def get_uri(self, obj):
        """Generate MCP URI for the tweet resource."""
        return f"mcp://tweets/{obj.tweet_id}"
    
    def get_name(self, obj):
        """Generate resource name."""
        return f"Tweet from @{obj.x_account.username}"
    
    def get_description(self, obj):
        """Generate resource description using AI summary if available."""
        try:
            if hasattr(obj, 'ai_analysis') and obj.ai_analysis.summary:
                return obj.ai_analysis.summary
            return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        except AIAnalysis.DoesNotExist:
            return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    
    def get_mimeType(self, obj):
        """Return MIME type for the resource."""
        return "application/json"
    
    def get_metadata(self, obj):
        """
        Generate metadata including AI analysis results.
        
        Returns comprehensive metadata about the tweet including:
        - Author information
        - Posting time
        - Engagement metrics
        - AI analysis (sentiment, topics, importance)
        - Media URLs
        """
        metadata = {
            # Author info
            'author': obj.x_account.username,
            'author_name': obj.x_account.display_name or obj.x_account.username,
            'author_avatar': obj.x_account.avatar_url,
            
            # Tweet info
            'tweet_id': obj.tweet_id,
            'tweet_url': f"https://twitter.com/{obj.x_account.username}/status/{obj.tweet_id}",
            'posted_at': obj.posted_at.isoformat(),
            'created_at': obj.created_at.isoformat(),
            
            # Engagement metrics
            'engagement': {
                'retweets': obj.retweet_count,
                'likes': obj.like_count,
                'replies': obj.reply_count,
            },
            
            # Content metadata
            'is_retweet': obj.is_retweet,
            'has_media': len(obj.media_urls) > 0,
            'media_urls': obj.media_urls,
            'hashtags': obj.hashtags,
            'mentions': obj.mentions,
        }
        
        # Add AI analysis if available
        try:
            if hasattr(obj, 'ai_analysis'):
                ai = obj.ai_analysis
                metadata['ai_analysis'] = {
                    'sentiment': ai.sentiment,
                    'summary': ai.summary,
                    'topics': ai.topics,
                    'importance_score': ai.importance_score,
                    'processed_at': ai.processed_at.isoformat(),
                }
                
                # Add AI relevant flags from Tweet model
                metadata['ai_relevant'] = obj.ai_relevant
                metadata['ai_analyzed'] = obj.ai_analyzed
        except AIAnalysis.DoesNotExist:
            metadata['ai_analyzed'] = False
            metadata['ai_relevant'] = obj.ai_relevant
        
        return metadata


class MCPTweetListSerializer(serializers.Serializer):
    """
    MCP Resource List serializer.
    
    Follows MCP protocol for listing available resources.
    """
    resources = MCPTweetResourceSerializer(many=True)
    total_count = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_previous = serializers.BooleanField()


class MCPAccountResourceSerializer(serializers.ModelSerializer):
    """
    MCP Resource serializer for X accounts.
    """
    uri = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    mimeType = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    
    class Meta:
        model = XAccount
        fields = ['uri', 'name', 'description', 'mimeType', 'metadata']
    
    def get_uri(self, obj):
        return f"mcp://accounts/{obj.username}"
    
    def get_name(self, obj):
        return f"X Account @{obj.username}"
    
    def get_description(self, obj):
        return obj.display_name or f"Twitter account @{obj.username}"
    
    def get_mimeType(self, obj):
        return "application/json"
    
    def get_metadata(self, obj):
        return {
            'username': obj.username,
            'display_name': obj.display_name,
            'x_user_id': obj.x_user_id,
            'avatar_url': obj.avatar_url,
            'is_active': obj.is_active,
            'monitoring_interval': obj.monitoring_interval,
            'ai_filter_enabled': obj.ai_filter_enabled,
            'total_tweets': obj.tweets.count(),
            'analyzed_tweets': obj.tweets.filter(ai_analyzed=True).count(),
            'relevant_tweets': obj.tweets.filter(ai_relevant=True).count(),
            'last_checked': obj.last_checked.isoformat() if obj.last_checked else None,
            'created_at': obj.created_at.isoformat(),
        }
