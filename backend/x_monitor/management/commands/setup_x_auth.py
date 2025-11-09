"""
Django管理命令：设置X.com认证

使用方法：
1. 在容器内运行: docker-compose exec backend python manage.py setup_x_auth
2. 或在本地运行: python manage.py setup_x_auth
3. 浏览器窗口会打开，手动登录X.com
4. 登录完成后按Enter，cookies会自动保存
"""
from django.core.management.base import BaseCommand
from x_monitor.authenticated_scraper import setup_authentication


class Command(BaseCommand):
    help = '设置X.com认证（保存登录cookies）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='X.com用户名（邮箱/手机/用户名）',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='X.com密码',
        )
        parser.add_argument(
            '--headless',
            action='store_true',
            help='在无头模式下运行（不显示浏览器窗口）',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        password = options.get('password')
        headless = options.get('headless', False)
        
        self.stdout.write(self.style.WARNING(
            '\n' + '='*60 + '\n'
            'X.com 认证设置\n'
            '='*60 + '\n'
        ))
        
        self.stdout.write(self.style.SUCCESS(
            '说明：\n'
            '1. 浏览器窗口将打开（或已在运行）\n'
            '2. 请手动登录您的X.com账号\n'
            '3. 登录成功后，等待页面完全加载\n'
            '4. 按Enter键，cookies将自动保存\n'
            '5. 之后爬虫将使用您的账号访问完整时间线\n'
        ))
        
        try:
            success = setup_authentication(
                username=username,
                password=password,
                headless=headless
            )
            
            if success:
                self.stdout.write(self.style.SUCCESS(
                    '\n✓ 认证设置完成！\n'
                    '\n下一步：\n'
                    '1. 在docker-compose.yml中设置环境变量:\n'
                    '   USE_AUTHENTICATED_SCRAPER: "True"\n'
                    '2. 重启服务: docker-compose restart\n'
                    '3. 现在爬虫将使用登录状态访问完整时间线\n'
                ))
            else:
                self.stdout.write(self.style.ERROR('\n✗ 登录失败\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'\n✗ 认证设置失败: {e}\n'
                '请检查网络连接和浏览器环境\n'
            ))
            raise
