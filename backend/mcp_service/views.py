from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Prefetch
from django.utils import timezone
from datetime import timedelta

from x_monitor.models import Tweet, XAccount, AIAnalysis
from .serializers import (
    MCPTweetResourceSerializer,
    MCPTweetListSerializer,
    MCPAccountResourceSerializer,
)


class MCPResourcePagination(PageNumberPagination):
    """Custom pagination for MCP resources."""
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100


class MCPTweetResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    MCP Resource endpoint for AI-analyzed tweets.
    
    Provides MCP-compliant access to tweets with AI analysis.
    
    Endpoints:
    - GET /api/mcp/tweets/ - List all available tweet resources
    - GET /api/mcp/tweets/{tweet_id}/ - Get specific tweet resource
    - GET /api/mcp/tweets/relevant/ - List only AI-relevant tweets
    - GET /api/mcp/tweets/search/ - Search tweets by content
    """
    serializer_class = MCPTweetResourceSerializer
    pagination_class = MCPResourcePagination
    permission_classes = [permissions.AllowAny]  # MCP resources are publicly accessible
    lookup_field = 'tweet_id'
    
    def get_queryset(self):
        """
        Return tweets with AI analysis, ordered by importance and recency.
        """
        queryset = Tweet.objects.select_related(
            'x_account',
            'ai_analysis'
        ).filter(
            ai_analyzed=True  # Only return analyzed tweets
        ).order_by(
            '-ai_analysis__importance_score',  # Higher importance first
            '-posted_at'  # Then by recency
        )
        
        # Filter by user if authenticated
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(x_account__user=user)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific tweet resource by tweet_id.
        
        Returns MCP-compliant resource representation.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """
        List all available tweet resources.
        
        Query parameters:
        - limit: Number of resources per page (default: 20, max: 100)
        - page: Page number
        - sentiment: Filter by sentiment (positive/negative/neutral)
        - min_importance: Minimum importance score (0.0-1.0)
        - account: Filter by account username
        - days: Filter tweets from last N days
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply additional filters
        sentiment = request.query_params.get('sentiment')
        if sentiment:
            queryset = queryset.filter(ai_analysis__sentiment=sentiment)
        
        min_importance = request.query_params.get('min_importance')
        if min_importance:
            try:
                queryset = queryset.filter(
                    ai_analysis__importance_score__gte=float(min_importance)
                )
            except ValueError:
                pass
        
        account = request.query_params.get('account')
        if account:
            queryset = queryset.filter(x_account__username=account)
        
        days = request.query_params.get('days')
        if days:
            try:
                since_date = timezone.now() - timedelta(days=int(days))
                queryset = queryset.filter(posted_at__gte=since_date)
            except ValueError:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            
            # Add MCP-specific metadata
            paginated_response.data['mcp_version'] = '1.0'
            paginated_response.data['resource_type'] = 'tweet'
            
            return paginated_response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'mcp_version': '1.0',
            'resource_type': 'tweet',
            'resources': serializer.data,
            'total_count': queryset.count(),
        })
    
    @action(detail=False, methods=['get'])
    def relevant(self, request):
        """
        List only AI-relevant tweets.
        
        Returns tweets that AI has marked as relevant/important.
        """
        queryset = self.get_queryset().filter(ai_relevant=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            paginated_response.data['mcp_version'] = '1.0'
            paginated_response.data['resource_type'] = 'tweet'
            paginated_response.data['filter'] = 'ai_relevant'
            return paginated_response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'mcp_version': '1.0',
            'resource_type': 'tweet',
            'filter': 'ai_relevant',
            'resources': serializer.data,
            'total_count': queryset.count(),
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search tweets by content, topics, or hashtags.
        
        Query parameters:
        - q: Search query
        - topics: Filter by topics (comma-separated)
        - hashtags: Filter by hashtags (comma-separated)
        """
        queryset = self.get_queryset()
        
        query = request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(content__icontains=query) |
                Q(ai_analysis__summary__icontains=query)
            )
        
        topics = request.query_params.get('topics')
        if topics:
            topic_list = [t.strip() for t in topics.split(',')]
            for topic in topic_list:
                queryset = queryset.filter(ai_analysis__topics__contains=[topic])
        
        hashtags = request.query_params.get('hashtags')
        if hashtags:
            hashtag_list = [h.strip() for h in hashtags.split(',')]
            for hashtag in hashtag_list:
                queryset = queryset.filter(hashtags__contains=[hashtag])
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            paginated_response.data['mcp_version'] = '1.0'
            paginated_response.data['resource_type'] = 'tweet'
            paginated_response.data['search_query'] = query
            return paginated_response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'mcp_version': '1.0',
            'resource_type': 'tweet',
            'search_query': query,
            'resources': serializer.data,
            'total_count': queryset.count(),
        })
    
    @action(detail=False, methods=['get'])
    def by_sentiment(self, request, sentiment=None):
        """
        List tweets filtered by sentiment.
        
        Path parameter:
        - sentiment: positive, negative, or neutral
        """
        sentiment = request.query_params.get('sentiment', sentiment)
        if not sentiment:
            return Response(
                {'error': 'sentiment parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(ai_analysis__sentiment=sentiment)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            paginated_response.data['mcp_version'] = '1.0'
            paginated_response.data['resource_type'] = 'tweet'
            paginated_response.data['filter'] = f'sentiment:{sentiment}'
            return paginated_response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'mcp_version': '1.0',
            'resource_type': 'tweet',
            'filter': f'sentiment:{sentiment}',
            'resources': serializer.data,
            'total_count': queryset.count(),
        })


class MCPAccountResourceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    MCP Resource endpoint for X accounts.
    
    Provides MCP-compliant access to monitored X accounts.
    
    Endpoints:
    - GET /api/mcp/accounts/ - List all monitored accounts
    - GET /api/mcp/accounts/{username}/ - Get specific account resource
    - GET /api/mcp/accounts/{username}/tweets/ - Get tweets from specific account
    """
    serializer_class = MCPAccountResourceSerializer
    pagination_class = MCPResourcePagination
    permission_classes = [permissions.AllowAny]
    lookup_field = 'username'
    
    def get_queryset(self):
        """Return active X accounts."""
        queryset = XAccount.objects.filter(is_active=True)
        
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.filter(user=user)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def tweets(self, request, username=None):
        """
        Get all tweets from a specific account.
        
        Returns MCP tweet resources for the specified account.
        """
        account = self.get_object()
        tweets = Tweet.objects.select_related(
            'x_account',
            'ai_analysis'
        ).filter(
            x_account=account,
            ai_analyzed=True
        ).order_by('-posted_at')
        
        # Apply pagination
        page = self.paginate_queryset(tweets)
        if page is not None:
            serializer = MCPTweetResourceSerializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            paginated_response.data['mcp_version'] = '1.0'
            paginated_response.data['resource_type'] = 'tweet'
            paginated_response.data['account'] = username
            return paginated_response
        
        serializer = MCPTweetResourceSerializer(tweets, many=True)
        return Response({
            'mcp_version': '1.0',
            'resource_type': 'tweet',
            'account': username,
            'resources': serializer.data,
            'total_count': tweets.count(),
        })
