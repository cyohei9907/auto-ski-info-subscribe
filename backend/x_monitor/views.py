import logging
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import XAccount, Tweet, MonitoringLog, UserNotification

logger = logging.getLogger(__name__)
from .serializers import (
    XAccountSerializer, XAccountCreateSerializer, TweetSerializer,
    MonitoringLogSerializer, UserNotificationSerializer
)
from .services import XMonitorService
from .tasks import monitor_single_account
from ai_service.services import analyze_tweet_with_ai


class XAccountListCreateView(generics.ListCreateAPIView):
    """X アカウント一覧・作成API"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return XAccount.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return XAccountCreateSerializer
        return XAccountSerializer
    
    @swagger_auto_schema(
        operation_description="監視中のXアカウント一覧を取得",
        responses={200: XAccountSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="新しいXアカウントを監視対象に追加",
        request_body=XAccountCreateSerializer,
        responses={
            201: XAccountSerializer(),
            400: "バリデーションエラー"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        
        # Check if account already exists
        existing_account = XAccount.objects.filter(
            user=request.user, 
            username=username
        ).first()
        
        if existing_account:
            return Response(
                {'error': f'アカウント @{username} は既に追加されています'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # X APIを使ってアカウント情報を取得
        monitor_service = XMonitorService()
        account_info = monitor_service.setup_account_monitoring(username)
        
        if not account_info:
            # スクレイピング失敗時は、デフォルト値でアカウントを作成（開発用）
            logger.warning(f'Failed to scrape account @{username}, creating with default values')
            x_account = XAccount.objects.create(
                user=request.user,
                username=username,
                display_name=username,
                x_user_id=username,  # Use username as x_user_id fallback
                avatar_url='https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png'
            )
            return Response(
                XAccountSerializer(x_account).data,
                status=status.HTTP_201_CREATED
            )
        
        # アカウントを作成
        x_account = XAccount.objects.create(
            user=request.user,
            username=account_info['username'],
            display_name=account_info['display_name'],
            x_user_id=account_info['user_id'],
            avatar_url=account_info['avatar_url']
        )
        
        # 第一次添加账户时，自动获取10条最新推文（异步任务）
        from .tasks import fetch_initial_tweets
        fetch_initial_tweets.delay(x_account.id)
        
        return Response(
            XAccountSerializer(x_account).data,
            status=status.HTTP_201_CREATED
        )


class XAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """X アカウント詳細・更新・削除API"""
    serializer_class = XAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return XAccount.objects.filter(user=self.request.user)


@swagger_auto_schema(
    method='post',
    operation_description="指定したXアカウントを手動で監視実行",
    responses={
        200: openapi.Response(
            description="監視実行成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'new_tweets': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def monitor_account_now(request, account_id):
    """アカウントを今すぐ監視"""
    x_account = get_object_or_404(XAccount, id=account_id, user=request.user)
    
    # Celeryタスクを実行
    task = monitor_single_account.delay(account_id)
    
    return Response({
        'success': True,
        'message': '監視タスクを開始しました',
        'task_id': task.id
    })


class TweetListView(generics.ListAPIView):
    """ツイート一覧API"""
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_accounts = XAccount.objects.filter(user=self.request.user)
        queryset = Tweet.objects.filter(x_account__in=user_accounts)
        
        # フィルタリング
        account_id = self.request.query_params.get('account_id')
        if account_id:
            queryset = queryset.filter(x_account_id=account_id)
        
        sentiment = self.request.query_params.get('sentiment')
        if sentiment:
            queryset = queryset.filter(ai_analysis__sentiment=sentiment)
        
        min_importance = self.request.query_params.get('min_importance')
        if min_importance:
            try:
                importance = float(min_importance)
                queryset = queryset.filter(ai_analysis__importance_score__gte=importance)
            except ValueError:
                pass
        
        return queryset.select_related('x_account', 'ai_analysis').order_by('-posted_at')


@swagger_auto_schema(
    method='post',
    operation_description="指定したツイートをAIで分析",
    responses={
        200: openapi.Response(
            description="分析成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_tweet(request, tweet_id):
    """ツイートをAI分析"""
    # ユーザーが所有するアカウントのツイートかチェック
    tweet = get_object_or_404(
        Tweet, 
        id=tweet_id, 
        x_account__user=request.user
    )
    
    # AI分析を実行
    ai_analysis = analyze_tweet_with_ai(tweet_id)
    
    if ai_analysis:
        return Response({
            'success': True,
            'message': 'AI分析が完了しました'
        })
    else:
        return Response({
            'success': False,
            'message': 'AI分析に失敗しました'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MonitoringLogListView(generics.ListAPIView):
    """監視ログ一覧API"""
    serializer_class = MonitoringLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_accounts = XAccount.objects.filter(user=self.request.user)
        return MonitoringLog.objects.filter(
            x_account__in=user_accounts
        ).select_related('x_account').order_by('-created_at')


class NotificationListView(generics.ListAPIView):
    """通知一覧API"""
    serializer_class = UserNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserNotification.objects.filter(
            user=self.request.user
        ).select_related('tweet').order_by('-created_at')


@swagger_auto_schema(
    method='post',
    operation_description="通知を既読にする",
    responses={200: openapi.Response(description="更新成功")}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """通知を既読にする"""
    notification = get_object_or_404(
        UserNotification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    
    return Response({'success': True, 'message': '通知を既読にしました'})