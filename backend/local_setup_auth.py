"""
Windows本地运行认证设置脚本
适用于Docker环境没有图形界面的情况

运行方法：
cd backend
python local_setup_auth.py
"""
import os
import sys
import django

# Django setup
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')

# 临时设置以便本地运行
os.environ.setdefault('USE_CLOUD_SQL', 'False')
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('SECRET_KEY', 'local-dev-key')

django.setup()

from x_monitor.authenticated_scraper import setup_authentication

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Windows本地 - X.com自动登录认证")
    print("="*60)
    print("\n这个脚本会：")
    print("1. 自动打开浏览器并登录X.com")
    print("2. 自动填写你的账号密码")
    print("3. 保存cookies到 backend/data/x_cookies.json")
    print("4. Docker会自动使用这个文件\n")
    
    print("=" * 60)
    print("\n请输入你的X.com账号信息：")
    print("（密码不会显示，输入后按Enter）\n")
    
    # 获取账号密码
    username = input("用户名（邮箱/手机/用户名）: ").strip()
    
    import getpass
    password = getpass.getpass("密码: ")
    
    if not username or not password:
        print("\n✗ 用户名或密码不能为空！")
        exit(1)
    
    # 询问是否显示浏览器
    show_browser = input("\n是否显示浏览器窗口？[Y/n]: ").strip().lower()
    headless = show_browser == 'n'
    
    print("\n开始登录...")
    
    try:
        success = setup_authentication(
            username=username,
            password=password,
            headless=headless
        )
        
        if success:
            print("\n" + "="*60)
            print("✓ 认证设置完成！")
            print("="*60)
            print("\ncookies已保存到: backend/data/x_cookies.json")
            print("\n如果使用Docker，这个文件会自动挂载到容器中")
            print("\n下一步：")
            print("1. 在docker-compose.yml中设置环境变量：")
            print("   USE_AUTHENTICATED_SCRAPER: 'True'")
            print("2. 重启服务：")
            print("   docker-compose restart")
            print("3. 测试效果：")
            print("   docker-compose exec backend python test_authenticated_scraper.py\n")
        else:
            print("\n✗ 登录失败，请检查账号密码或网络连接")
            
    except Exception as e:
        print(f"\n✗ 设置失败: {e}")
        import traceback
        traceback.print_exc()
