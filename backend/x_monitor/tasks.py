from celery import shared_task
from django.utils import timezone
from .models import XAccount
from .services import XMonitorService
import logging

logger = logging.getLogger(__name__)


@shared_task
def monitor_all_active_accounts():
    """すべてのアクティブなアカウントを監視するタスク"""
    active_accounts = XAccount.objects.filter(is_active=True)
    monitor_service = XMonitorService()
    
    results = []
    for account in active_accounts:
        try:
            result = monitor_service.monitor_account(account)
            results.append({
                'account': account.username,
                'result': result
            })
            logger.info(f"Monitored @{account.username}: {result}")
        except Exception as e:
            logger.error(f"Failed to monitor @{account.username}: {e}")
            results.append({
                'account': account.username,
                'error': str(e)
            })
    
    return results


@shared_task
def monitor_single_account(account_id):
    """単一のアカウントを監視するタスク"""
    try:
        account = XAccount.objects.get(id=account_id, is_active=True)
        monitor_service = XMonitorService()
        result = monitor_service.monitor_account(account)
        logger.info(f"Monitored @{account.username}: {result}")
        return result
    except XAccount.DoesNotExist:
        logger.error(f"Account with id {account_id} not found or inactive")
        return {'error': 'Account not found or inactive'}
    except Exception as e:
        logger.error(f"Failed to monitor account {account_id}: {e}")
        return {'error': str(e)}


@shared_task
def monitor_today_tweets():
    """すべてのアクティブなアカウントの当日ツイートを監視するタスク"""
    active_accounts = XAccount.objects.filter(is_active=True)
    monitor_service = XMonitorService()
    
    results = []
    for account in active_accounts:
        try:
            # 当日のツイートのみを取得
            result = monitor_service.monitor_account(account, today_only=True)
            results.append({
                'account': account.username,
                'result': result
            })
            logger.info(f"Monitored today's tweets for @{account.username}: {result}")
        except Exception as e:
            logger.error(f"Failed to monitor today's tweets for @{account.username}: {e}")
            results.append({
                'account': account.username,
                'error': str(e)
            })
    
    return results


@shared_task
def fetch_initial_tweets(account_id):
    """第一次添加账户时，获取10条最新推文"""
    try:
        account = XAccount.objects.get(id=account_id)
        monitor_service = XMonitorService()
        
        logger.info(f"Fetching initial 10 tweets for @{account.username}")
        result = monitor_service.monitor_account(account, max_tweets=10)
        
        # 如果启用了AI过滤，自动分析所有新推文
        if account.ai_filter_enabled and result.get('new_tweets', 0) > 0:
            analyze_tweets_for_recommendation.delay(account.id)
        
        logger.info(f"Initial tweets fetched for @{account.username}: {result}")
        return result
        
    except XAccount.DoesNotExist:
        logger.error(f"Account with id {account_id} not found")
        return {'error': 'Account not found'}
    except Exception as e:
        logger.error(f"Failed to fetch initial tweets for account {account_id}: {e}")
        return {'error': str(e)}


@shared_task
def analyze_tweets_for_recommendation(account_id):
    """使用AI分析推文并生成推荐"""
    from .models import Tweet, RecommendedTweet
    from ai_service.services import AIService
    
    try:
        account = XAccount.objects.get(id=account_id)
        
        # 获取该账户所有未分析的推文
        unanalyzed_tweets = Tweet.objects.filter(
            x_account=account,
            ai_analyzed=False
        )
        
        ai_service = AIService()
        recommended_count = 0
        
        for tweet in unanalyzed_tweets:
            try:
                # 使用AI判断是否推荐
                analysis = ai_service.analyze_tweet_relevance(tweet.content)
                
                tweet.ai_analyzed = True
                tweet.ai_relevant = analysis.get('is_relevant', False)
                tweet.ai_summary = analysis.get('summary', '')
                tweet.save()
                
                # 如果AI判断为相关，创建推荐记录
                if tweet.ai_relevant:
                    RecommendedTweet.objects.get_or_create(
                        user=account.user,
                        tweet=tweet,
                        defaults={
                            'ai_reason': analysis.get('reason', ''),
                            'relevance_score': analysis.get('score', 0.0)
                        }
                    )
                    recommended_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to analyze tweet {tweet.tweet_id}: {e}")
                continue
        
        logger.info(f"Analyzed tweets for @{account.username}, {recommended_count} recommended")
        return {
            'account': account.username,
            'analyzed': unanalyzed_tweets.count(),
            'recommended': recommended_count
        }
        
    except XAccount.DoesNotExist:
        logger.error(f"Account with id {account_id} not found")
        return {'error': 'Account not found'}
    except Exception as e:
        logger.error(f"Failed to analyze tweets for account {account_id}: {e}")
        return {'error': str(e)}