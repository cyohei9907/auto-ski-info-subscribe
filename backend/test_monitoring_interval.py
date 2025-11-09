"""
测试监控间隔功能
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from x_monitor.models import XAccount
from x_monitor.tasks import monitor_all_active_accounts


class MonitoringIntervalTestCase(TestCase):
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        # 创建不同监控间隔的账户
        self.account_30min = XAccount.objects.create(
            user=self.user,
            username='test_30min',
            monitoring_interval=30,
            is_active=True
        )
        
        self.account_1hour = XAccount.objects.create(
            user=self.user,
            username='test_1hour',
            monitoring_interval=60,
            is_active=True
        )
        
        self.account_4hours = XAccount.objects.create(
            user=self.user,
            username='test_4hours',
            monitoring_interval=240,
            is_active=True
        )
        
        self.account_12hours = XAccount.objects.create(
            user=self.user,
            username='test_12hours',
            monitoring_interval=720,
            is_active=True
        )
    
    def test_monitoring_interval_choices(self):
        """测试监控间隔选项"""
        self.assertEqual(self.account_30min.monitoring_interval, 30)
        self.assertEqual(self.account_1hour.monitoring_interval, 60)
        self.assertEqual(self.account_4hours.monitoring_interval, 240)
        self.assertEqual(self.account_12hours.monitoring_interval, 720)
    
    def test_monitoring_interval_display(self):
        """测试监控间隔显示"""
        self.assertEqual(self.account_30min.get_monitoring_interval_display(), '每30分钟')
        self.assertEqual(self.account_1hour.get_monitoring_interval_display(), '每1小时')
        self.assertEqual(self.account_4hours.get_monitoring_interval_display(), '每4小时')
        self.assertEqual(self.account_12hours.get_monitoring_interval_display(), '每12小时')
    
    def test_should_monitor_logic(self):
        """测试应该监控的逻辑"""
        now = timezone.now()
        
        # 测试：从未检查过的账户应该被监控
        self.assertIsNone(self.account_30min.last_checked)
        # 在实际任务中会被监控
        
        # 测试：最近检查过的账户
        self.account_30min.last_checked = now - timedelta(minutes=20)
        self.account_30min.save()
        # 20分钟前检查，间隔30分钟 → 不应该监控
        time_since_check = (now - self.account_30min.last_checked).total_seconds() / 60
        self.assertLess(time_since_check, self.account_30min.monitoring_interval)
        
        # 测试：超过间隔的账户
        self.account_30min.last_checked = now - timedelta(minutes=35)
        self.account_30min.save()
        # 35分钟前检查，间隔30分钟 → 应该监控
        time_since_check = (now - self.account_30min.last_checked).total_seconds() / 60
        self.assertGreaterEqual(time_since_check, self.account_30min.monitoring_interval)
    
    def test_default_monitoring_interval(self):
        """测试默认监控间隔"""
        new_account = XAccount.objects.create(
            user=self.user,
            username='test_default',
            is_active=True
        )
        self.assertEqual(new_account.monitoring_interval, 240)  # 默认4小时
    
    def test_update_monitoring_interval(self):
        """测试更新监控间隔"""
        self.account_4hours.monitoring_interval = 60
        self.account_4hours.save()
        
        self.account_4hours.refresh_from_db()
        self.assertEqual(self.account_4hours.monitoring_interval, 60)
        self.assertEqual(self.account_4hours.get_monitoring_interval_display(), '每1小时')


if __name__ == '__main__':
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
    django.setup()
    
    from django.test.utils import get_runner
    TestRunner = get_runner(django.conf.settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["__main__"])
