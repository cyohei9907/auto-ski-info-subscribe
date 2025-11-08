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


@swagger_auto_schema(
    method='post',
    operation_description="上传X.com cookies（适用于Google登录等无密码场景）",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['cookies'],
        properties={
            'cookies': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Cookies JSON字符串或数组'
            ),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'cookies_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        400: "参数错误"
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_x_cookies(request):
    """
    上传X.com cookies - 适用于Google登录用户
    
    用户在浏览器手动登录X.com后，导出cookies并上传
    """
    cookies_data = request.data.get('cookies')
    
    if not cookies_data:
        return Response(
            {'success': False, 'message': '请提供cookies数据'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        import json
        from pathlib import Path
        from django.conf import settings
        
        # 解析cookies
        if isinstance(cookies_data, str):
            cookies = json.loads(cookies_data)
        else:
            cookies = cookies_data
        
        if not isinstance(cookies, list):
            return Response(
                {'success': False, 'message': 'Cookies格式错误，应为数组'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证cookies格式
        required_fields = ['name', 'value', 'domain']
        for cookie in cookies:
            if not all(field in cookie for field in required_fields):
                return Response(
                    {'success': False, 'message': f'Cookie缺少必要字段：{required_fields}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 转换cookies格式以兼容Playwright
        # Cookie-Editor导出的sameSite值为 "no_restriction"/"unspecified"
        # Playwright要求为 "Strict"/"Lax"/"None"
        playwright_cookies = []
        for cookie in cookies:
            # 复制cookie
            new_cookie = cookie.copy()
            
            # 转换sameSite字段
            if 'sameSite' in new_cookie:
                same_site = new_cookie['sameSite']
                if same_site in ['no_restriction', 'unspecified']:
                    new_cookie['sameSite'] = 'None'
                elif same_site not in ['Strict', 'Lax', 'None']:
                    # 未知值，默认使用None
                    new_cookie['sameSite'] = 'None'
            else:
                # 如果没有sameSite字段，添加默认值
                new_cookie['sameSite'] = 'Lax'
            
            # 确保secure字段存在（sameSite=None时必须为True）
            if new_cookie.get('sameSite') == 'None' and not new_cookie.get('secure'):
                new_cookie['secure'] = True
            
            playwright_cookies.append(new_cookie)
        
        # 保存cookies
        cookies_file = Path(settings.BASE_DIR) / 'data' / 'x_cookies.json'
        cookies_file.parent.mkdir(exist_ok=True)
        
        with open(cookies_file, 'w') as f:
            json.dump(playwright_cookies, f, indent=2)
        
        logger.info(f"X.com cookies uploaded successfully, saved {len(cookies)} cookies")
        
        return Response({
            'success': True,
            'message': f'Cookies上传成功！已保存 {len(cookies)} 个cookies',
            'cookies_count': len(cookies),
            'next_steps': [
                '已自动启用认证爬虫',
                '现在可以获取最新推文'
            ]
        })
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format: {e}")
        return Response(
            {'success': False, 'message': f'JSON格式错误: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error uploading cookies: {e}", exc_info=True)
        return Response(
            {'success': False, 'message': f'上传失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_description="设置X.com账号认证，执行自动登录并保存cookies",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='X.com用户名/邮箱/手机号'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='X.com密码'),
            'headless': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否无头模式运行（默认True）', default=True),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'cookies_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
        400: "参数错误",
        500: "登录失败"
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def setup_x_authentication(request):
    """
    网页按钮调用：执行X.com自动登录
    
    接收用户名和密码，自动打开浏览器登录X.com，保存cookies到服务器
    """
    username = request.data.get('username')
    password = request.data.get('password')
    headless = request.data.get('headless', True)
    
    if not username or not password:
        return Response(
            {'success': False, 'message': '请提供用户名和密码'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        logger.info(f"Starting X.com authentication for user: {username}")
        
        # 导入认证设置函数
        from .authenticated_scraper import setup_authentication
        
        # 执行自动登录（在后端服务器上运行）
        success = setup_authentication(username, password, headless=headless)
        
        if success:
            # 检查cookies文件
            from pathlib import Path
            from django.conf import settings
            cookies_file = Path(settings.BASE_DIR) / 'data' / 'x_cookies.json'
            
            if cookies_file.exists():
                import json
                with open(cookies_file, 'r') as f:
                    cookies = json.load(f)
                
                logger.info(f"X.com authentication successful, saved {len(cookies)} cookies")
                
                return Response({
                    'success': True,
                    'message': f'X.com登录成功！已保存 {len(cookies)} 个cookies',
                    'cookies_count': len(cookies),
                    'next_steps': [
                        '已自动启用认证爬虫',
                        '现在可以获取最新推文',
                        '建议重启服务以应用更改'
                    ]
                })
            else:
                logger.error("Cookies file not found after authentication")
                return Response(
                    {'success': False, 'message': '登录完成但cookies文件未找到'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            logger.error("X.com authentication failed")
            return Response(
                {'success': False, 'message': '登录失败，请检查用户名和密码'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error during X.com authentication: {e}", exc_info=True)
        return Response(
            {'success': False, 'message': f'登录过程出错: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


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
            avatar_url=account_info.get('avatar_url') or 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png'
        )
        
        # 第一次添加账户时，自动获取10条最新推文（异步任务）
        # 如果Celery不可用，静默失败，不影响账户创建
        try:
            from .tasks import fetch_initial_tweets
            fetch_initial_tweets.delay(x_account.id)
            logger.info(f"Scheduled initial tweet fetch for @{username}")
        except Exception as e:
            logger.warning(f"Failed to schedule initial tweet fetch: {e}. Account created successfully.")
        
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


@swagger_auto_schema(
    method='delete',
    operation_description="删除指定的推文",
    responses={
        200: openapi.Response(
            description="删除成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        404: "推文不存在"
    }
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_tweet(request, tweet_id):
    """删除单个推文"""
    try:
        tweet = Tweet.objects.get(
            id=tweet_id,
            x_account__user=request.user
        )
        tweet_content = tweet.content[:50]
        tweet.delete()
        
        logger.info(f"Tweet {tweet_id} deleted by user {request.user.email}")
        return Response({
            'success': True,
            'message': f'推文已删除: {tweet_content}...'
        })
    except Tweet.DoesNotExist:
        return Response({
            'success': False,
            'message': '推文不存在或无权限删除'
        }, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='delete',
    operation_description="删除指定账户的所有推文",
    manual_parameters=[
        openapi.Parameter(
            'confirm',
            openapi.IN_QUERY,
            description="确认删除（必须传入 'yes'）",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="删除成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'deleted_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )
        ),
        400: "缺少确认参数",
        404: "账户不存在"
    }
)
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account_tweets(request, account_id):
    """删除指定账户的所有推文"""
    # 确认参数检查
    confirm = request.query_params.get('confirm')
    if confirm != 'yes':
        return Response({
            'success': False,
            'message': '请传入 confirm=yes 参数以确认删除'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 检查账户是否属于当前用户
        x_account = XAccount.objects.get(
            id=account_id,
            user=request.user
        )
        
        # 获取推文数量并删除
        tweet_count = Tweet.objects.filter(x_account=x_account).count()
        deleted_count, _ = Tweet.objects.filter(x_account=x_account).delete()
        
        logger.info(f"Deleted {deleted_count} tweets from account @{x_account.username} by user {request.user.email}")
        
        return Response({
            'success': True,
            'message': f'已删除 @{x_account.username} 的所有推文',
            'deleted_count': tweet_count
        })
    except XAccount.DoesNotExist:
        return Response({
            'success': False,
            'message': '账户不存在或无权限'
        }, status=status.HTTP_404_NOT_FOUND)


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


@swagger_auto_schema(
    method='post',
    operation_description="指定したアカウントの最新10条推文を即座に取得",
    responses={
        200: openapi.Response(
            description="取得成功",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'new_tweets': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )
        )
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fetch_latest_tweets(request, account_id):
    """アカウントの最新10条推文を即座に取得"""
    # ユーザーが所有するアカウントかチェック
    x_account = get_object_or_404(
        XAccount,
        id=account_id,
        user=request.user
    )
    
    # 監視サービスを使って最新推文を取得
    monitor_service = XMonitorService()
    result = monitor_service.monitor_account(x_account, max_tweets=10)
    
    if result.get('success'):
        return Response({
            'success': True,
            'message': f'{result.get("new_tweets", 0)}条の新しい推文を取得しました',
            'new_tweets': result.get('new_tweets', 0)
        })
    else:
        return Response({
            'success': False,
            'message': '推文の取得に失敗しました',
            'new_tweets': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="获取调试HTML文件（用于检查爬虫抓取的原始HTML）",
    manual_parameters=[
        openapi.Parameter('username', openapi.IN_PATH, description="X.com用户名", type=openapi.TYPE_STRING),
        openapi.Parameter('download', openapi.IN_QUERY, description="是否下载文件", type=openapi.TYPE_BOOLEAN, required=False),
    ],
    responses={
        200: "HTML内容或文件下载",
        404: "文件不存在"
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_debug_html(request, username):
    """
    获取调试HTML文件 - 查看爬虫抓取的原始HTML
    """
    import os
    from django.http import HttpResponse, FileResponse
    from pathlib import Path
    from django.conf import settings
    
    debug_file = Path(settings.BASE_DIR) / 'data' / f"debug_twitter_{username}.html"
    
    if not os.path.exists(debug_file):
        return Response({
            'success': False,
            'message': f'调试文件不存在: {username}',
            'hint': '请先执行一次推文抓取操作'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 检查是否需要下载
    download = request.query_params.get('download', 'false').lower() == 'true'
    
    if download:
        # 下载文件
        response = FileResponse(open(debug_file, 'rb'), content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="twitter_{username}_debug.html"'
        return response
    else:
        # 直接显示HTML内容
        with open(debug_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_custom_debug_html(request, filename):
    """
    获取自定义调试HTML文件（通过debug_scrape_url生成的）
    """
    import os
    from django.http import HttpResponse, FileResponse
    from pathlib import Path
    from django.conf import settings
    
    # 安全检查：只允许特定格式的文件名
    if not filename.startswith('debug_custom_') or not filename.endswith('.html'):
        return Response({
            'success': False,
            'message': '非法的文件名'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    debug_file = Path(settings.BASE_DIR) / 'data' / filename
    
    if not os.path.exists(debug_file):
        return Response({
            'success': False,
            'message': f'调试文件不存在: {filename}'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # 检查是否需要下载
    download = request.query_params.get('download', 'false').lower() == 'true'
    
    if download:
        # 下载文件
        response = FileResponse(open(debug_file, 'rb'), content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        # 直接显示HTML内容
        with open(debug_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')


@swagger_auto_schema(
    method='post',
    operation_description="调试抓取任意URL - 使用cookie登录后访问并保存HTML",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['url'],
        properties={
            'url': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='要抓取的URL（例如：https://x.com/username）'
            ),
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'html_preview': openapi.Schema(type=openapi.TYPE_STRING, description='HTML前1000字符预览'),
                'html_size': openapi.Schema(type=openapi.TYPE_INTEGER, description='HTML大小（字节）'),
                'debug_filename': openapi.Schema(type=openapi.TYPE_STRING, description='保存的文件名'),
            }
        ),
        400: "参数错误",
        500: "抓取失败"
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def debug_scrape_url(request):
    """
    调试抓取功能 - 使用cookie登录后访问任意URL并保存HTML
    """
    url = request.data.get('url', '').strip()
    
    if not url:
        return Response({
            'success': False,
            'message': '请提供要抓取的URL'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 简单验证URL格式
    if not url.startswith('http'):
        url = 'https://' + url
    
    try:
        from playwright.sync_api import sync_playwright
        import json
        import os
        import time
        from pathlib import Path
        from django.conf import settings
        
        logger.info(f"开始调试抓取URL: {url}")
        
        # 读取cookies
        cookies_file = Path(settings.BASE_DIR) / 'data' / 'x_cookies.json'
        if not os.path.exists(cookies_file):
            return Response({
                'success': False,
                'message': 'Cookie文件不存在，请先上传cookies'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        
        logger.info(f"已加载 {len(cookies)} 个cookies")
        
        # 启动浏览器
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            # 创建浏览器上下文，添加反检测和浏览器指纹
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                locale='ja-JP',
                timezone_id='Asia/Tokyo',
                device_scale_factor=1,
                has_touch=False,
                java_script_enabled=True,
                bypass_csp=True,
            )
            
            # 添加cookies
            context.add_cookies(cookies)
            logger.info("已添加cookies到浏览器上下文")
            
            # 注入反检测脚本
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                window.chrome = {
                    runtime: {}
                };
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['ja-JP', 'ja', 'en-US', 'en']
                });
            """)
            
            page = context.new_page()
            
            # 访问URL
            logger.info(f"正在访问: {url}")
            page.goto(url, wait_until='networkidle', timeout=90000)
            
            # 等待页面加载
            time.sleep(3)
            
            # 获取HTML内容
            html_content = page.content()
            html_size = len(html_content.encode('utf-8'))
            
            logger.info(f"已获取HTML内容，大小: {html_size} 字节")
            
            # 生成文件名（从URL提取）
            import re
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path_clean = re.sub(r'[^\w\-]', '_', parsed.path.strip('/'))
            if not path_clean:
                path_clean = parsed.netloc.replace('.', '_')
            
            timestamp = int(time.time())
            debug_filename = f"debug_custom_{path_clean}_{timestamp}.html"
            debug_filepath = Path(settings.BASE_DIR) / 'data' / debug_filename
            
            # 保存HTML
            with open(debug_filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML已保存到: {debug_filepath}")
            
            # 关闭浏览器
            browser.close()
        
        return Response({
            'success': True,
            'message': f'成功抓取URL并保存',
            'html_preview': html_content[:1000],
            'html_size': html_size,
            'debug_filename': debug_filename,
            'url': url
        })
        
    except Exception as e:
        logger.error(f"调试抓取失败: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': f'抓取失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)