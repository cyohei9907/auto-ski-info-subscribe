"""
独立的X.com自动登录脚本
不依赖Django，可直接在Windows本地运行

使用方法：
pip install playwright beautifulsoup4 lxml
playwright install chromium
python standalone_auth.py
"""
import os
import json
import getpass
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def auto_login_x(username: str, password: str, headless: bool = False):
    """
    自动登录X.com并保存cookies
    
    参数：
        username: X.com用户名（邮箱/手机/用户名）
        password: X.com密码
        headless: 是否无头模式
    
    返回：
        True: 登录成功
        False: 登录失败
    """
    # Cookies保存路径
    cookies_file = Path(__file__).parent / 'data' / 'x_cookies.json'
    cookies_file.parent.mkdir(exist_ok=True)
    
    print("\n" + "="*60)
    print("X.com 自动登录")
    print("="*60)
    print(f"\n用户名: {username}")
    print("密码: " + "*" * len(password))
    print(f"模式: {'无头模式' if headless else '显示浏览器'}\n")
    
    try:
        with sync_playwright() as p:
            # 启动浏览器
            print("正在启动浏览器...")
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # 创建上下文
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US'
            )
            
            page = context.new_page()
            
            # 访问登录页
            print("正在访问X.com登录页面...")
            page.goto("https://x.com/i/flow/login", wait_until='networkidle', timeout=60000)
            print("页面加载完成，等待3秒...")
            page.wait_for_timeout(3000)
            
            # 输入用户名
            print("\n等待用户名输入框...")
            try:
                # 尝试多个选择器
                username_input = page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
                print("✓ 找到用户名输入框")
            except PlaywrightTimeoutError:
                print("⚠️ 未找到标准输入框，尝试备用选择器...")
                try:
                    username_input = page.wait_for_selector('input[name="text"]', timeout=5000)
                    print("✓ 找到备用输入框")
                except PlaywrightTimeoutError:
                    print("✗ 无法找到用户名输入框")
                    # 保存截图
                    screenshot_path = cookies_file.parent / 'login_error.png'
                    page.screenshot(path=str(screenshot_path))
                    print(f"已保存截图: {screenshot_path}")
                    browser.close()
                    return False
            
            print(f"输入用户名: {username}")
            username_input.fill(username)
            page.wait_for_timeout(1000)
            
            # 点击"Next"按钮
            print("查找并点击'Next'按钮...")
            try:
                # 尝试多种方式找到Next按钮
                next_button = page.locator('xpath=//span[contains(text(), "Next")]').first
                if next_button.is_visible():
                    print("✓ 找到Next按钮（通过文本）")
                    next_button.click()
                else:
                    # 尝试通过role查找
                    next_button = page.get_by_role("button", name="Next")
                    print("✓ 找到Next按钮（通过role）")
                    next_button.click()
            except Exception as e:
                print(f"⚠️ 点击Next按钮出错: {e}")
                # 尝试按Enter键
                print("尝试按Enter键...")
                page.keyboard.press("Enter")
            
            print("等待3秒...")
            page.wait_for_timeout(3000)
            
            # 检查是否需要额外验证
            page_content = page.content().lower()
            if 'phone' in page_content or 'verification' in page_content:
                print("\n" + "="*60)
                print("⚠️ X.com要求额外验证（电话/邮箱）")
                print("="*60)
                print("这通常发生在新环境登录时")
                print("\n请在浏览器中完成验证:")
                print("1. 查看浏览器窗口")
                print("2. 输入验证信息")
                print("3. 完成后回到这里")
                input("\n按Enter继续...")
                page.wait_for_timeout(2000)
            
            # 输入密码
            print("\n等待密码输入框...")
            try:
                password_input = page.wait_for_selector('input[name="password"]', timeout=10000)
                print("✓ 找到密码输入框")
            except PlaywrightTimeoutError:
                print("✗ 无法找到密码输入框")
                screenshot_path = cookies_file.parent / 'password_error.png'
                page.screenshot(path=str(screenshot_path))
                print(f"已保存截图: {screenshot_path}")
                browser.close()
                return False
            
            print("输入密码...")
            password_input.fill(password)
            page.wait_for_timeout(1000)
            
            # 点击"Log in"按钮
            print("查找并点击'Log in'按钮...")
            try:
                login_button = page.locator('xpath=//span[contains(text(), "Log in")]').first
                if login_button.is_visible():
                    print("✓ 找到Log in按钮（通过文本）")
                    login_button.click()
                else:
                    login_button = page.get_by_role("button", name="Log in")
                    print("✓ 找到Log in按钮（通过role）")
                    login_button.click()
            except Exception as e:
                print(f"⚠️ 点击Log in按钮出错: {e}")
                print("尝试按Enter键...")
                page.keyboard.press("Enter")
            
            # 等待登录完成
            print("\n等待登录完成（8秒）...")
            page.wait_for_timeout(8000)
            
            # 检查当前URL
            current_url = page.url
            print(f"当前URL: {current_url}")
            
            # 检查是否需要两步验证
            if "login" in current_url or "flow" in current_url:
                page_text = page.content().lower()
                if "verification" in page_text or "authenticate" in page_text or "code" in page_text:
                    print("\n" + "="*60)
                    print("⚠️ 需要两步验证")
                    print("="*60)
                    print("请在浏览器中:")
                    print("1. 输入验证码")
                    print("2. 完成验证")
                    input("\n完成后按Enter继续...")
                    page.wait_for_timeout(5000)
            
            # 验证登录状态
            print("\n验证登录状态...")
            try:
                page.goto("https://x.com/home", wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(5000)
            except:
                print("⚠️ 导航到home页面超时，继续尝试...")
            
            final_url = page.url
            print(f"最终URL: {final_url}")
            
            if "login" in final_url or "flow" in final_url:
                print("\n✗ 登录验证失败")
                print("可能的原因：")
                print("1. 用户名或密码错误")
                print("2. 账号需要额外验证")
                print("3. X.com安全检测")
                screenshot_path = cookies_file.parent / 'login_failed.png'
                page.screenshot(path=str(screenshot_path))
                print(f"已保存截图: {screenshot_path}")
                browser.close()
                return False
            
            # 保存cookies
            print("\n保存cookies...")
            cookies = context.cookies()
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Cookies已保存到: {cookies_file}")
            print(f"  共 {len(cookies)} 个cookies")
            print("\n✓ 登录成功！")
            
            browser.close()
            return True
            
    except Exception as e:
        print(f"\n✗ 登录过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("X.com 自动登录认证工具")
    print("="*60)
    print("\n这个工具会：")
    print("1. 自动打开浏览器并登录X.com")
    print("2. 自动填写你的账号密码")
    print("3. 处理验证流程（如需要）")
    print("4. 保存cookies到 backend/data/x_cookies.json")
    print("\n" + "="*60)
    
    # 获取账号信息
    print("\n请输入你的X.com账号信息：")
    print("（密码输入时不会显示）\n")
    
    username = input("用户名（邮箱/手机/用户名）: ").strip()
    if not username:
        print("\n✗ 用户名不能为空！")
        return
    
    password = getpass.getpass("密码: ")
    if not password:
        print("\n✗ 密码不能为空！")
        return
    
    # 询问是否显示浏览器
    show_browser = input("\n是否显示浏览器窗口？[Y/n]: ").strip().lower()
    headless = show_browser == 'n'
    
    print("\n开始登录...")
    print("=" * 60)
    
    # 执行登录
    success = auto_login_x(username, password, headless)
    
    if success:
        print("\n" + "="*60)
        print("✓ 认证设置完成！")
        print("="*60)
        print("\ncookies已保存到: backend/data/x_cookies.json")
        print("\n下一步：")
        print("1. 在docker-compose.yml中设置环境变量：")
        print("   USE_AUTHENTICATED_SCRAPER: 'True'")
        print("2. 重启服务：")
        print("   docker-compose restart")
        print("3. 测试效果：")
        print("   docker-compose exec backend python test_authenticated_scraper.py")
        print("\n" + "="*60)
    else:
        print("\n" + "="*60)
        print("✗ 登录失败")
        print("="*60)
        print("\n请检查：")
        print("1. 用户名和密码是否正确")
        print("2. 网络连接是否正常")
        print("3. 查看 backend/data/ 目录下的截图了解详情")
        print("\n可以重新运行此脚本再试一次")
        print("=" * 60)


if __name__ == "__main__":
    main()
