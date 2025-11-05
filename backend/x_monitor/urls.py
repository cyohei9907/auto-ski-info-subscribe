from django.urls import path
from . import views

urlpatterns = [
    # X Account管理
    path('accounts/', views.XAccountListCreateView.as_view(), name='x-account-list'),
    path('accounts/<int:pk>/', views.XAccountDetailView.as_view(), name='x-account-detail'),
    path('accounts/<int:account_id>/monitor/', views.monitor_account_now, name='monitor-account-now'),
    
    # ツイート関連
    path('tweets/', views.TweetListView.as_view(), name='tweet-list'),
    path('tweets/<int:tweet_id>/analyze/', views.analyze_tweet, name='analyze-tweet'),
    
    # ログと通知
    path('logs/', views.MonitoringLogListView.as_view(), name='monitoring-log-list'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
]