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