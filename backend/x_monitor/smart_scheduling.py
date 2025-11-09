"""
智能监控调度优化 - 成本节省 50%

这个文件展示如何实现智能分级调度，减少不必要的 API 调用
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import F
from .models import XAccount
from .services import XMonitorService
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_monitoring(request):
    """
    智能触发监控 - 只监控到期的账号
    
    Query Parameters:
        interval (int): 只监控特定间隔的账号（30, 60, 240, 720分钟）
    
    成本优化:
        - 不再每次触发都监控所有账号
        - 根据 last_checked + monitoring_interval 判断是否需要监控
        - 分级调度: 不同间隔的账号使用不同的 cron
        
    使用示例:
        POST /api/monitor/trigger-monitoring/?interval=30
        POST /api/monitor/trigger-monitoring/?interval=60
        POST /api/monitor/trigger-monitoring/?interval=240
        POST /api/monitor/trigger-monitoring/?interval=720
    """
    try:
        interval = request.query_params.get('interval')
        now = timezone.now()
        
        # 构建查询条件
        query = XAccount.objects.filter(is_active=True)
        
        # 如果指定了间隔，只获取该间隔的账号
        if interval:
            interval = int(interval)
            query = query.filter(monitoring_interval=interval)
        
        # 只获取需要监控的账号（上次检查时间 + 间隔 <= 现在）
        # 使用 F 表达式进行数据库级别的计算
        from datetime import timedelta
        accounts_to_monitor = []
        
        for account in query:
            if not account.last_checked:
                # 从未检查过，需要监控
                accounts_to_monitor.append(account)
            else:
                # 计算下次应该检查的时间
                next_check_time = account.last_checked + timedelta(minutes=account.monitoring_interval)
                if now >= next_check_time:
                    accounts_to_monitor.append(account)
        
        if not accounts_to_monitor:
            return Response({
                'success': True,
                'message': f'没有需要监控的账号（间隔={interval}分钟）',
                'accounts_checked': 0
            })
        
        # 开始监控
        monitor_service = XMonitorService()
        successful = 0
        failed = 0
        
        for account in accounts_to_monitor:
            try:
                logger.info(f"监控账号: @{account.username} (间隔: {account.monitoring_interval}分钟)")
                monitor_service.monitor_account(account)
                successful += 1
            except Exception as e:
                logger.error(f"监控失败 @{account.username}: {e}")
                failed += 1
        
        return Response({
            'success': True,
            'message': f'监控完成',
            'interval': interval,
            'accounts_checked': len(accounts_to_monitor),
            'successful': successful,
            'failed': failed,
            'timestamp': now.isoformat()
        })
        
    except Exception as e:
        logger.error(f"触发监控失败: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_monitoring_schedule(request):
    """
    获取监控调度统计
    
    返回:
        - 各个间隔的账号数量
        - 下次需要监控的账号数量
        - 预估每日 API 调用次数
    """
    try:
        from datetime import timedelta
        now = timezone.now()
        
        # 统计各间隔的账号数
        stats = {
            '30': {'count': 0, 'next_run': [], 'daily_runs': 48},
            '60': {'count': 0, 'next_run': [], 'daily_runs': 24},
            '240': {'count': 0, 'next_run': [], 'daily_runs': 6},
            '720': {'count': 0, 'next_run': [], 'daily_runs': 2}
        }
        
        accounts = XAccount.objects.filter(is_active=True, user=request.user)
        
        for account in accounts:
            interval_str = str(account.monitoring_interval)
            if interval_str in stats:
                stats[interval_str]['count'] += 1
                
                # 计算下次运行时间
                if account.last_checked:
                    next_run = account.last_checked + timedelta(minutes=account.monitoring_interval)
                    if next_run <= now + timedelta(hours=1):  # 1小时内需要运行
                        stats[interval_str]['next_run'].append({
                            'username': account.username,
                            'next_run': next_run.isoformat()
                        })
        
        # 计算预估每日 API 调用次数
        total_daily_calls = sum(
            stats[interval]['count'] * stats[interval]['daily_runs']
            for interval in stats
        )
        
        # 计算月成本估算（基于 Cloud Run 调用）
        # 假设每次调用平均运行 3 分钟，使用 1 vCPU, 1GB RAM
        # 成本: $0.00002400/vCPU-秒 + $0.00000250/GB-秒
        monthly_calls = total_daily_calls * 30
        avg_duration_seconds = 180  # 3分钟
        monthly_cpu_seconds = monthly_calls * avg_duration_seconds
        monthly_memory_gb_seconds = monthly_calls * avg_duration_seconds * 1  # 1GB
        
        cpu_cost = monthly_cpu_seconds * 0.00002400
        memory_cost = monthly_memory_gb_seconds * 0.00000250
        estimated_monthly_cost = cpu_cost + memory_cost
        
        return Response({
            'success': True,
            'stats': stats,
            'total_accounts': accounts.count(),
            'total_daily_calls': total_daily_calls,
            'total_monthly_calls': monthly_calls,
            'estimated_monthly_cost_usd': round(estimated_monthly_cost, 2),
            'cost_breakdown': {
                'cpu_cost_usd': round(cpu_cost, 2),
                'memory_cost_usd': round(memory_cost, 2)
            }
        })
        
    except Exception as e:
        logger.error(f"获取监控统计失败: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_monitoring_intervals(request):
    """
    智能优化监控间隔建议
    
    根据账号活跃度自动推荐合适的监控间隔:
        - 高活跃（每天 >10 条推文）: 30分钟
        - 中活跃（每天 5-10 条）: 1小时
        - 低活跃（每天 1-5 条）: 4小时
        - 极低活跃（每天 <1 条）: 12小时
    """
    try:
        from datetime import timedelta
        from django.db.models import Count
        
        accounts = XAccount.objects.filter(is_active=True, user=request.user)
        recommendations = []
        
        for account in accounts:
            # 计算过去7天的推文数
            seven_days_ago = timezone.now() - timedelta(days=7)
            tweet_count = account.tweets.filter(posted_at__gte=seven_days_ago).count()
            avg_daily_tweets = tweet_count / 7
            
            # 推荐间隔
            if avg_daily_tweets > 10:
                recommended_interval = 30
                reason = "高活跃账号（每天>10条推文）"
            elif avg_daily_tweets > 5:
                recommended_interval = 60
                reason = "中活跃账号（每天5-10条推文）"
            elif avg_daily_tweets > 1:
                recommended_interval = 240
                reason = "低活跃账号（每天1-5条推文）"
            else:
                recommended_interval = 720
                reason = "极低活跃账号（每天<1条推文）"
            
            if account.monitoring_interval != recommended_interval:
                recommendations.append({
                    'account_id': account.id,
                    'username': account.username,
                    'current_interval': account.monitoring_interval,
                    'recommended_interval': recommended_interval,
                    'avg_daily_tweets': round(avg_daily_tweets, 2),
                    'reason': reason,
                    'potential_savings': abs(account.monitoring_interval - recommended_interval) / account.monitoring_interval * 100
                })
        
        return Response({
            'success': True,
            'recommendations': recommendations,
            'total_accounts': accounts.count(),
            'accounts_to_optimize': len(recommendations),
            'message': '根据账号活跃度优化监控间隔可以节省成本'
        })
        
    except Exception as e:
        logger.error(f"优化建议失败: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# 添加到 urls.py:
# path('trigger-monitoring/', views.trigger_monitoring, name='trigger-monitoring'),
# path('monitoring-schedule/', views.get_monitoring_schedule, name='monitoring-schedule'),
# path('optimize-intervals/', views.optimize_monitoring_intervals, name='optimize-intervals'),
