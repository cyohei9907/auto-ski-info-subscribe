from django.urls import path
from . import views
from . import smart_scheduling

urlpatterns = [
    # X.com 认证设置
    path('setup-auth/', views.setup_x_authentication, name='setup-x-auth'),
    path('upload-cookies/', views.upload_x_cookies, name='upload-x-cookies'),
    
    # X Account管理
    path('accounts/', views.XAccountListCreateView.as_view(), name='x-account-list'),
    path('accounts/<int:pk>/', views.XAccountDetailView.as_view(), name='x-account-detail'),
    path('accounts/<int:account_id>/monitor/', views.monitor_account_now, name='monitor-account-now'),
    path('accounts/<int:account_id>/fetch-latest/', views.fetch_latest_tweets, name='fetch-latest-tweets'),
    
    # ツイート関連
    path('tweets/', views.TweetListView.as_view(), name='tweet-list'),
    path('tweets/<int:tweet_id>/analyze/', views.analyze_tweet, name='analyze-tweet'),
    path('tweets/<int:tweet_id>/delete/', views.delete_tweet, name='delete-tweet'),
    path('accounts/<int:account_id>/tweets/delete/', views.delete_account_tweets, name='delete-account-tweets'),
    
    # ログと通知
    path('logs/', views.MonitoringLogListView.as_view(), name='monitoring-log-list'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    
    # AI推荐规则管理
    path('ai/rules/', views.AIPromptRuleListCreateView.as_view(), name='ai-rule-list'),
    path('ai/rules/<int:pk>/', views.AIPromptRuleDetailView.as_view(), name='ai-rule-detail'),
    path('ai/rules/<int:rule_id>/apply/', views.apply_ai_rule, name='apply-ai-rule'),
    
    # AI推荐推文
    path('ai/recommended/', views.RecommendedTweetListView.as_view(), name='recommended-tweet-list'),
    path('ai/recommended/<int:tweet_id>/read/', views.mark_recommended_tweet_read, name='mark-recommended-read'),
    
    # 智能监控调度（成本优化）
    path('trigger-monitoring/', smart_scheduling.trigger_monitoring, name='trigger-monitoring'),
    path('monitoring-schedule/', smart_scheduling.get_monitoring_schedule, name='monitoring-schedule'),
    path('optimize-intervals/', smart_scheduling.optimize_monitoring_intervals, name='optimize-intervals'),
]