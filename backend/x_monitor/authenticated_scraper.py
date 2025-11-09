"""
X.com 登录爬虫 - 使用用户账号登录以访问完整时间线

使用说明：
1. 首次使用需要手动登录：
   python manage.py shell
   from x_monitor.authenticated_scraper import setup_authentication
   setup_authentication()  # 会打开浏览器窗口，手动登录后cookies会自动保存

2. 在 docker-compose.yml 中设置环境变量：
   USE_AUTHENTICATED_SCRAPER: "True"

3. 后续爬虫会自动使用保存的cookies进行认证访问
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from django.conf import settings
from django.utils import timezone as django_timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import re
import random
import time

logger = logging.getLogger(__name__)


class AuthenticatedXScraperClient:
    """使用登录凭证的X.com爬虫客户端"""
    
    def __init__(self):
        self.base_url = "https://x.com"
        self.cookies_file = Path(settings.BASE_DIR) / 'data' / 'x_cookies.json'
        self.cookies_file.parent.mkdir(exist_ok=True)
        
    def _add_random_delay(self):
        """添加15-30秒的随机延迟"""
        delay = random.uniform(15, 30)
        logger.info(f"Waiting {delay:.1f} seconds before next request...")
        time.sleep(delay)
    
    def _load_cookies(self) -> Optional[List[Dict]]:
        """加载保存的cookies"""
        if not self.cookies_file.exists():
            logger.warning(f"Cookies file not found: {self.cookies_file}")
            return None
        
        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            logger.info(f"Loaded {len(cookies)} cookies from {self.cookies_file}")
            return cookies
        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return None
    
    def _save_cookies(self, cookies: List[Dict]):
        """保存cookies到文件"""
        try:
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"Saved {len(cookies)} cookies to {self.cookies_file}")
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
    
    def _create_authenticated_context(self, playwright):
        """创建带认证的浏览器上下文，伪装成真实的Windows Chrome浏览器"""
        browser = playwright.chromium.launch(
            headless=True,  # 改回headless模式
            args=[
                '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )
        
        # 模拟真实的Windows 10 Chrome浏览器
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},  # 常见的桌面分辨率
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',  # 最新Chrome版本
            locale='ja-JP',  # 日本地区
            timezone_id='Asia/Tokyo',  # 东京时区
            bypass_csp=True,  # 添加bypass_csp（debug_scrape_url有这个）
            java_script_enabled=True,
            extra_http_headers={
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            },
            # 模拟屏幕和设备信息
            screen={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
        )
        
        # 注入脚本隐藏 WebDriver 特征
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 伪装Chrome运行环境
            window.chrome = {
                runtime: {}
            };
            
            // 覆盖权限查询
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        # 加载cookies
        cookies = self._load_cookies()
        if cookies:
            context.add_cookies(cookies)
            logger.info("Added cookies to browser context")
        else:
            logger.warning("No cookies available, scraper will access as guest")
        
        return browser, context
    
    def _extract_tweet_id(self, tweet_url: str) -> Optional[str]:
        """从URL中提取tweet ID"""
        match = re.search(r'/status/(\d+)', tweet_url)
        return match.group(1) if match else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        try:
            self._add_random_delay()
            
            with sync_playwright() as p:
                browser, context = self._create_authenticated_context(p)
                page = context.new_page()
                
                url = f"{self.base_url}/{username}"
                page.goto(url, wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(2000)
                
                html = page.content()
                soup = BeautifulSoup(html, 'lxml')
                
                # 显示名称
                display_name = username
                name_selectors = [
                    'div[data-testid="UserName"] span',
                    'div[data-testid="UserDescription"] span',
                    'h2[role="heading"] span'
                ]
                for selector in name_selectors:
                    elem = soup.select_one(selector)
                    if elem and elem.get_text().strip():
                        display_name = elem.get_text().strip()
                        break
                
                # 头像
                avatar_url = None
                avatar_selectors = [
                    'div[data-testid="UserAvatar-Container-"] img',
                    'a[href*="/photo"] img',
                    'img[alt*="{}"]'.format(username)
                ]
                for selector in avatar_selectors:
                    elem = soup.select_one(selector)
                    if elem and elem.get('src'):
                        avatar_url = elem.get('src')
                        break
                
                browser.close()
                
                return {
                    'id': username,
                    'username': username,
                    'name': display_name,
                    'profile_image_url': avatar_url
                }
                
        except Exception as e:
            logger.error(f"Error scraping user {username}: {e}")
            return None
    
    def get_recent_tweets(self, username: str, max_results: int = 20) -> List[Dict]:
        """获取最近的推文（登录状态下可以获取完整时间线）"""
        try:
            self._add_random_delay()
            
            logger.info(f"Fetching up to {max_results} tweets for @{username} (authenticated)")
            
            with sync_playwright() as p:
                browser, context = self._create_authenticated_context(p)
                page = context.new_page()
                
                # 访问用户的推文页面（帖子标签页）
                # 注意：X.com 的用户主页默认可能显示算法排序的推文
                # 但是当我们滚动到顶部后，应该能看到最新的推文
                url = f"{self.base_url}/{username}"
                logger.info(f"Navigating to {url} to fetch latest tweets")
                
                try:
                    # 使用domcontentloaded代替networkidle，更可靠
                    page.goto(url, wait_until='domcontentloaded', timeout=90000)
                    logger.info("Page loaded, waiting for React to render tweets...")
                    
                    # 关键修复：等待直到页面大小增长（说明React渲染完成）
                    max_wait = 15  # 最多等15秒
                    for i in range(max_wait):
                        page.wait_for_timeout(1000)  # 每次等1秒
                        html_size = len(page.content())
                        logger.info(f"Wait {i+1}s: HTML size = {html_size} bytes")
                        
                        # 如果HTML超过400KB，说明内容加载了
                        if html_size > 400000:
                            logger.info(f"Content loaded (size: {html_size} bytes)")
                            break
                    
                    logger.info("Checking for tweets...")
                    
                    # 检查是否需要登录（检测登录按钮）
                    try:
                        login_button = page.query_selector('a[href="/login"]')
                        if login_button:
                            logger.error("⚠️ Cookie认证失败！页面显示需要登录。Cookie可能已过期或无效。")
                            raise Exception("Cookie认证失败，页面要求登录。请重新上传有效的cookie。")
                    except:
                        pass  # 没有登录按钮说明已登录，继续执行
                    
                    # 等待推文出现
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)  # 缩短到10秒
                    logger.info("Tweets detected!")
                    
                    # 滚动到页面顶部，确保从最新推文开始
                    logger.info("Scrolling to top to ensure latest tweets...")
                    page.evaluate('window.scrollTo(0, 0)')
                    page.wait_for_timeout(2000)
                    
                except PlaywrightTimeoutError as e:
                    logger.error(f"Timeout waiting for page: {e}")
                    logger.info("Waiting additional time for page to load...")
                    # 即使超时，也多等待一些时间让页面加载
                    page.wait_for_timeout(10000)  # 额外等待10秒
                    
                    # 尝试滚动页面，触发动态加载
                    logger.info("Trying to scroll to trigger content loading...")
                    for _ in range(3):
                        page.evaluate('window.scrollBy(0, 500)')
                        page.wait_for_timeout(1000)
                    
                    # 检查是否有推文加载出来
                    tweet_count = page.evaluate('document.querySelectorAll(\'article[data-testid="tweet"]\').length')
                    logger.info(f"After additional waiting and scrolling: {tweet_count} tweets visible")
                    
                    if tweet_count == 0:
                        logger.warning("Still no tweets found, saving debug HTML...")
                        # 保存HTML用于调试
                        debug_html = page.content()
                        import os as os_module
                        from django.conf import settings as django_settings
                        debug_file_path = os_module.path.join(django_settings.BASE_DIR, 'data', f"debug_failed_{username}_{int(time.time())}.html")
                        with open(debug_file_path, 'w', encoding='utf-8') as f:
                            f.write(debug_html)
                        logger.warning(f"Debug HTML saved to: {debug_file_path}")
                
                # 滚动加载更多推文
                logger.info("Scrolling to load more tweets...")
                for scroll_count in range(10):
                    prev_height = page.evaluate('document.body.scrollHeight')
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    page.wait_for_timeout(2000)
                    
                    tweet_count = page.evaluate('document.querySelectorAll(\'article[data-testid="tweet"]\').length')
                    new_height = page.evaluate('document.body.scrollHeight')
                    logger.info(f"After scroll {scroll_count + 1}: {tweet_count} tweets visible, height: {prev_height} -> {new_height}")
                    
                    if new_height == prev_height:
                        logger.info("Reached bottom of page")
                        break
                    
                    if tweet_count >= max_results * 2:
                        logger.info(f"Loaded sufficient tweets ({tweet_count})")
                        break
                
                # 获取HTML
                html = page.content()
                
                # 保存HTML以供调试（仅开发环境）
                import os
                from pathlib import Path
                from django.conf import settings
                debug_file = Path(settings.BASE_DIR) / 'data' / f"debug_twitter_{username}.html"
                try:
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html)
                    logger.info(f"Saved HTML to {debug_file} for debugging")
                except Exception as e:
                    logger.warning(f"Failed to save debug HTML: {e}")
                
                soup = BeautifulSoup(html, 'lxml')
                browser.close()
                
                # 解析推文
                tweets = []
                tweet_articles = soup.find_all('article', {'data-testid': 'tweet'})
                logger.info(f"Found {len(tweet_articles)} tweet articles on page")
                
                for article in tweet_articles[:max_results]:
                    try:
                        # 推文文本
                        tweet_text_elem = article.find('div', {'data-testid': 'tweetText'})
                        tweet_text = tweet_text_elem.get_text() if tweet_text_elem else ""
                        
                        # 推文ID
                        tweet_link = article.find('a', href=re.compile(r'/status/\d+'))
                        tweet_id = None
                        if tweet_link and 'href' in tweet_link.attrs:
                            tweet_id = self._extract_tweet_id(tweet_link['href'])
                        
                        if not tweet_id:
                            continue
                        
                        # 时间
                        time_elem = article.find('time')
                        posted_at = None
                        if time_elem and 'datetime' in time_elem.attrs:
                            posted_at = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                            logger.info(f"Tweet {tweet_id} posted at: {posted_at}")
                        
                        if not posted_at:
                            # 检查是否是置顶推文
                            pinned_label = article.find('span', string=re.compile(r'Pinned|固定'))
                            is_pinned = pinned_label is not None
                            logger.warning(f"Tweet {tweet_id} has no timestamp (is_pinned: {is_pinned}), text preview: {tweet_text[:100]}")
                            continue
                        
                        # Hashtags和Mentions
                        hashtags = [tag.get_text()[1:] for tag in article.find_all('a', href=re.compile(r'/hashtag/'))]
                        mentions = [mention.get_text()[1:] for mention in article.find_all('a', href=re.compile(r'/[^/]+$')) if mention.get_text().startswith('@')]
                        
                        # 媒体URL
                        media_urls = []
                        for img in article.find_all('img', src=re.compile(r'pbs\.twimg\.com')):
                            media_urls.append(img.get('src'))
                        
                        # Engagement指标
                        reply_count = 0
                        retweet_count = 0
                        like_count = 0
                        
                        reply_elem = article.find('button', {'data-testid': 'reply'})
                        if reply_elem:
                            reply_text = reply_elem.get_text()
                            reply_match = re.search(r'\d+', reply_text)
                            reply_count = int(reply_match.group()) if reply_match else 0
                        
                        retweet_elem = article.find('button', {'data-testid': 'retweet'})
                        if retweet_elem:
                            retweet_text = retweet_elem.get_text()
                            retweet_match = re.search(r'\d+', retweet_text)
                            retweet_count = int(retweet_match.group()) if retweet_match else 0
                        
                        like_elem = article.find('button', {'data-testid': 'like'})
                        if like_elem:
                            like_text = like_elem.get_text()
                            like_match = re.search(r'\d+', like_text)
                            like_count = int(like_match.group()) if like_match else 0
                        
                        tweets.append({
                            'id': tweet_id,
                            'text': tweet_text,
                            'created_at': posted_at,
                            'hashtags': hashtags,
                            'mentions': mentions,
                            'media_urls': media_urls,
                            'reply_count': reply_count,
                            'retweet_count': retweet_count,
                            'like_count': like_count
                        })
                        
                        logger.debug(f"Parsed tweet {tweet_id} from {posted_at}")
                        
                    except Exception as e:
                        logger.warning(f"Error parsing tweet: {e}")
                        continue
                
                # 按时间降序排序（最新的在前面）
                tweets.sort(key=lambda x: x['created_at'], reverse=True)
                logger.info(f"Successfully scraped {len(tweets)} tweets (authenticated), sorted by time")
                
                # 只返回请求的数量，确保是最新的
                result_tweets = tweets[:max_results]
                if result_tweets:
                    logger.info(f"Returning {len(result_tweets)} most recent tweets, from {result_tweets[0]['created_at']} to {result_tweets[-1]['created_at']}")
                
                return result_tweets
                
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []


def setup_authentication(username: str = None, password: str = None, headless: bool = False):
    """
    设置认证：自动登录X.com并保存cookies
    
    参数：
        username: X.com用户名（邮箱/手机/用户名）
        password: X.com密码
        headless: 是否无头模式（True=不显示浏览器）
    
    使用方法：
    python manage.py shell
    >>> from x_monitor.authenticated_scraper import setup_authentication
    >>> setup_authentication(username='your_email@example.com', password='your_password')
    """
    cookies_file = Path(settings.BASE_DIR) / 'data' / 'x_cookies.json'
    cookies_file.parent.mkdir(exist_ok=True)
    
    # 如果没有提供账号密码，从环境变量或提示输入
    if not username:
        username = os.environ.get('X_USERNAME')
        if not username:
            username = input("请输入X.com用户名（邮箱/手机/用户名）: ")
    
    if not password:
        password = os.environ.get('X_PASSWORD')
        if not password:
            import getpass
            password = getpass.getpass("请输入X.com密码: ")
    
    print("\n" + "="*60)
    print("X.com 自动登录认证设置")
    print("="*60)
    print(f"\n用户名: {username}")
    print("密码: " + "*" * len(password))
    print(f"模式: {'无头模式' if headless else '显示浏览器'}\n")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US'
            )
            page = context.new_page()
            
            print("正在访问X.com登录页面...")
            # 使用domcontentloaded而不是networkidle，更可靠
            try:
                page.goto("https://x.com/i/flow/login", wait_until='domcontentloaded', timeout=90000)
                print("页面已加载，等待5秒...")
                page.wait_for_timeout(5000)
            except Exception as e:
                print(f"⚠️ 页面加载超时或失败: {e}")
                print("尝试继续...")
                page.wait_for_timeout(3000)
            
            print("等待登录表单加载...")
            # 等待用户名输入框
            try:
                username_input = page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
            except:
                print("⚠️ 未找到用户名输入框，尝试其他选择器...")
                username_input = page.wait_for_selector('input[name="text"]', timeout=10000)
            
            print(f"输入用户名: {username}")
            username_input.fill(username)
            page.wait_for_timeout(1000)
            
            # 点击"Next"按钮
            print("点击下一步...")
            next_button = page.locator('xpath=//span[text()="Next"]').first
            next_button.click()
            page.wait_for_timeout(3000)
            
            # 检查是否需要额外验证（电话/邮箱确认）
            page_content = page.content()
            if 'Enter your phone number' in page_content or 'verification' in page_content.lower():
                print("\n⚠️ X.com要求额外验证（电话/邮箱）")
                print("这通常发生在新环境登录时")
                print("\n请在浏览器中完成验证，然后按Enter继续...")
                input()
                page.wait_for_timeout(3000)
            
            # 输入密码
            print("等待密码输入框...")
            password_input = page.wait_for_selector('input[name="password"]', timeout=10000)
            
            print("输入密码...")
            password_input.fill(password)
            page.wait_for_timeout(1000)
            
            # 点击"Log in"按钮
            print("点击登录...")
            login_button = page.locator('xpath=//span[text()="Log in"]').first
            login_button.click()
            
            # 等待登录完成
            print("\n等待登录完成...")
            page.wait_for_timeout(8000)
            
            # 检查是否登录成功
            current_url = page.url
            print(f"当前URL: {current_url}")
            
            if "login" in current_url or "error" in current_url:
                # 可能需要两步验证
                page_text = page.content()
                if "verification" in page_text.lower() or "authenticate" in page_text.lower():
                    print("\n⚠️ 需要两步验证")
                    print("请在浏览器中完成验证，完成后按Enter...")
                    input()
                    page.wait_for_timeout(5000)
                else:
                    print("\n✗ 登录失败！")
                    print("可能的原因：")
                    print("1. 用户名或密码错误")
                    print("2. 账号被锁定或需要验证")
                    print("3. X.com检测到自动化行为")
                    browser.close()
                    return False
            
            # 导航到home验证登录状态
            print("\n验证登录状态...")
            page.goto("https://x.com/home", wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(5000)
            
            final_url = page.url
            if "login" in final_url:
                print("\n✗ 登录验证失败")
                browser.close()
                return False
            
            # 保存cookies
            print("\n保存cookies...")
            cookies = context.cookies()
            with open(cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            
            print(f"\n✓ Cookies已保存到: {cookies_file}")
            print(f"  共 {len(cookies)} 个cookies")
            print("\n✓ 登录成功！")
            print("\n下一步：")
            print("1. 在docker-compose.yml中设置: USE_AUTHENTICATED_SCRAPER: 'True'")
            print("2. 重启服务: docker-compose restart")
            print("3. 测试: docker-compose exec backend python test_authenticated_scraper.py")
            
            browser.close()
            return True
            
    except Exception as e:
        print(f"\n✗ 登录过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
