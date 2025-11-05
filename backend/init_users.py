"""
初始化数据库并创建默认管理员用户
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

def create_initial_users():
    """创建初始用户数据"""
    
    # 检查是否已经有用户
    if User.objects.exists():
        print("✅ 数据库中已存在用户，跳过初始化")
        return
    
    print("🔧 开始创建初始用户...")
    
    # 创建管理员用户
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin@123',
        first_name='Admin',
        last_name='User'
    )
    print(f"✅ 创建管理员用户: {admin_user.username}")
    
    # 为管理员创建 Profile
    UserProfile.objects.create(
        user=admin_user,
        timezone='Asia/Tokyo',
        notification_enabled=True
    )
    print("✅ 创建管理员 Profile")
    
    # 创建测试用户
    test_user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='test123',
        first_name='Test',
        last_name='User'
    )
    print(f"✅ 创建测试用户: {test_user.username}")
    
    # 为测试用户创建 Profile
    UserProfile.objects.create(
        user=test_user,
        timezone='Asia/Tokyo',
        notification_enabled=True
    )
    print("✅ 创建测试用户 Profile")
    
    print("\n" + "="*60)
    print("🎉 初始用户创建完成！")
    print("="*60)
    print("\n📝 登录信息：")
    print("\n【管理员账户】")
    print("  用户名: admin")
    print("  密码: admin@123")
    print("  邮箱: admin@example.com")
    print("  权限: 超级管理员（可访问 /admin）")
    print("\n【测试账户】")
    print("  用户名: testuser")
    print("  密码: test123")
    print("  邮箱: test@example.com")
    print("  权限: 普通用户")
    print("\n" + "="*60)
    print("💡 提示：生产环境请立即修改默认密码！")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        create_initial_users()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
