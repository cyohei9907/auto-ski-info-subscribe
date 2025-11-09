import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from x_monitor.models import XAccount
from x_monitor.services import XMonitorService

# 获取skiinfomation账号
try:
    account = XAccount.objects.get(username='skiinfomation')
    print(f"Found account: {account.username} (ID: {account.id})")
    
    # 调用monitor_account方法（这是"获取10条最新推特"实际调用的）
    print("\n开始调用 monitor_account...")
    service = XMonitorService()
    result = service.monitor_account(account, max_tweets=10)
    
    print("\n=== 结果 ===")
    print(f"Success: {result.get('success')}")
    print(f"New tweets: {result.get('new_tweets')}")
    print(f"Execution time: {result.get('execution_time')} seconds")
    
except XAccount.DoesNotExist:
    print("Account 'skiinfomation' not found in database")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
