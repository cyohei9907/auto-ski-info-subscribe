"""
临时解决方案：使用views.py中成功的scraping逻辑
因为authenticated_scraper被X.com的反自动化机制阻止
"""
import logging
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from django.conf import settings

logger = logging.getLogger(__name__)


def scrape_with_working_method(username: str, max_tweets: int = 20):
    """
    使用views.py中证明有效的方法抓取推文
    这个方法能成功获取推文（528KB HTML with tweets）
    """
    url = f"https://x.com/{username}"
    
    # 读取cookies
    cookie_file = Path(settings.BASE_DIR) / 'data' / 'x_cookies.json'
    if not cookie_file.exists():
        logger.error(f"Cookie文件不存在: {cookie_file}")
        return []
    
    with open(cookie_file, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    
    logger.info(f"使用working scraper抓取 @{username} 的推文...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 使用与debug_scrape_url完全相同的配置
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='ja-JP',
            timezone_id='Asia/Tokyo',
            device_scale_factor=1,
            has_touch=False,
            java_script_enabled=True,
            bypass_csp=True,
        )
        
        # 添加cookies
        context.add_cookies(cookies)
        
        # 反检测脚本
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = context.new_page()
        
        try:
            # 访问URL
            logger.info(f"访问: {url}")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=60000)
                logger.info("页面 DOM 加载完成")
            except Exception as e:
                logger.warning(f"domcontentloaded 超时，尝试 load: {e}")
                try:
                    page.goto(url, wait_until='load', timeout=60000)
                    logger.info("页面 load 完成")
                except Exception as e2:
                    logger.warning(f"load 也超时: {e2}")
            
            # 关键：等待5秒让React渲染（debug_scrape_url的成功做法）
            logger.info("等待页面渲染...")
            time.sleep(5)
            
            # 尝试等待推文元素
            try:
                page.wait_for_selector('article, [data-testid="tweet"]', timeout=10000)
                logger.info("检测到推文元素")
            except:
                logger.warning("未检测到推文元素，但继续解析")
            
            # 首先提取账户头像（从页面头部，不是从推文卡片）
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'lxml')
            
            account_avatar_url = None
            # 尝试从页面头部的用户信息中提取头像
            profile_images = soup.find_all('img', {'alt': lambda x: x and username.lower() in str(x).lower()})
            if profile_images:
                for img in profile_images:
                    src = img.get('src', '')
                    if src and 'profile_images' in src:
                        account_avatar_url = src.replace('_normal', '_400x400')
                        logger.info(f"从页面头部找到账户头像: {account_avatar_url[:80]}...")
                        break
            
            # 如果从页面头部找不到，尝试从第一条原创推文获取
            if not account_avatar_url:
                logger.info("页面头部未找到账户头像，将从第一条推文获取")
            
            # 使用滚动加载收集推文（因为Twitter使用虚拟滚动，DOM会复用节点）
            tweets = []
            collected_tweet_ids = set()  # 用于去重
            consecutive_non_original = 0  # 连续遇到的转发/回复数
            max_consecutive_non_original = 5
            first_original_tweet_processed = False
            scroll_attempts = 0
            max_scroll_attempts = 5
            no_new_tweets_count = 0
            
            logger.info("开始滚动收集推文...")
            while scroll_attempts < max_scroll_attempts and len(tweets) < max_tweets and no_new_tweets_count < 2:
                # 获取当前页面的HTML并解析
                html_content = page.content()
                soup = BeautifulSoup(html_content, 'lxml')
                articles = soup.find_all('article', {'data-testid': 'tweet'})
                
                logger.info(f"滚动 #{scroll_attempts + 1}: 找到 {len(articles)} 个推文DOM节点")
                
                new_tweets_in_this_scroll = 0
                
                # 处理当前可见的推文
                for article in articles:
                    try:
                        # 推文ID
                        tweet_link = article.find('a', href=lambda x: x and '/status/' in x)
                        if not tweet_link:
                            continue
                        
                        tweet_id = tweet_link['href'].split('/status/')[-1].split('?')[0]
                        
                        # 去重：跳过已经处理过的推文
                        if tweet_id in collected_tweet_ids:
                            continue
                        
                        # 标记为已处理
                        collected_tweet_ids.add(tweet_id)
                        
                        # 检查是否是转发（Retweet）
                        is_retweet = False
                        retweet_indicator = article.find('span', string=lambda x: x and ('Retweeted' in x or '转推了' in x or 'リツイート' in x))
                        if retweet_indicator:
                            is_retweet = True
                            logger.info(f"推文 {tweet_id} 是转发，跳过")
                        
                        # 检查是否是回复（Reply）
                        is_reply = False
                        reply_indicator = article.find('div', {'data-testid': 'reply'}) or \
                                         article.find('span', string=lambda x: x and ('Replying to' in x or '返信先:' in x or '回复' in x))
                        if reply_indicator:
                            is_reply = True
                            logger.info(f"推文 {tweet_id} 是回复，跳过")
                        
                        # 如果是转发或回复，增加计数器
                        if is_retweet or is_reply:
                            consecutive_non_original += 1
                            logger.info(f"连续非原创推文数: {consecutive_non_original}/{max_consecutive_non_original}")
                            
                            # 如果连续5条都是转发/回复，停止抓取
                            if consecutive_non_original >= max_consecutive_non_original:
                                logger.info(f"连续 {max_consecutive_non_original} 条转发/回复，停止抓取")
                                break
                            continue
                        
                        # 重置计数器（遇到原创推文）
                        consecutive_non_original = 0
                        
                        # 如果已经收集够了，跳出文章循环
                        if len(tweets) >= max_tweets:
                            logger.info(f"已收集 {len(tweets)} 条原创推文，停止处理")
                            break
                        
                        # 推文文本
                        text_elem = article.find('[data-testid="tweetText"]')
                        if text_elem:
                            text = text_elem.get_text(separator='\n', strip=True)
                        else:
                            # 尝试其他选择器
                            text_elem = article.find('div', {'lang': True})  # 尝试查找带lang属性的div
                            if text_elem:
                                text = text_elem.get_text(separator='\n', strip=True)
                                logger.info(f"推文 {tweet_id} 使用备用选择器找到文本")
                            else:
                                text = ''
                                logger.warning(f"推文 {tweet_id} 没有找到文本元素")
                        
                        # 时间
                        time_elem = article.find('time')
                        if not time_elem:
                            logger.warning(f"推文 {tweet_id} 没有找到 <time> 元素")
                            continue
                        
                        if not time_elem.get('datetime'):
                            # 尝试从文本中获取相对时间（如 "2h"、"47m"）
                            time_text = time_elem.get_text(strip=True)
                            logger.warning(f"推文 {tweet_id} 没有 datetime 属性，只有文本: '{time_text}'")
                            
                            # 尝试解析相对时间
                            from datetime import timedelta
                            from django.utils import timezone as django_timezone
                            
                            published_at = None
                            if 'm' in time_text:  # 分钟前
                                try:
                                    minutes = int(''.join(filter(str.isdigit, time_text)))
                                    published_at = (django_timezone.now() - timedelta(minutes=minutes)).isoformat()
                                    logger.info(f"解析相对时间 '{time_text}' -> {minutes}分钟前")
                                except:
                                    pass
                            elif 'h' in time_text:  # 小时前
                                try:
                                    hours = int(''.join(filter(str.isdigit, time_text)))
                                    published_at = (django_timezone.now() - timedelta(hours=hours)).isoformat()
                                    logger.info(f"解析相对时间 '{time_text}' -> {hours}小时前")
                                except:
                                    pass
                            
                            if not published_at:
                                logger.warning(f"无法解析相对时间 '{time_text}'，跳过推文 {tweet_id}")
                                continue
                        else:
                            published_at = time_elem['datetime']
                        
                        # 提取hashtags和mentions
                        hashtags = []
                        mentions = []
                        if text_elem:
                            for hashtag in text_elem.find_all('a', href=lambda x: x and '/hashtag/' in x):
                                hashtags.append(hashtag.get_text().strip())
                            for mention in text_elem.find_all('a', href=lambda x: x and x.startswith('/')):
                                mention_text = mention.get_text().strip()
                                if mention_text.startswith('@'):
                                    mentions.append(mention_text)
                        
                        # 互动数据（默认为0，因为不容易从HTML提取）
                        retweet_count = 0
                        like_count = 0
                        reply_count = 0
                        
                        # 媒体URL（如果有）
                        media_urls = []
                        # 查找所有图片，排除头像（头像URL包含 profile_images）
                        all_imgs = article.find_all('img')
                        for img in all_imgs:
                            src = img.get('src', '')
                            if src and 'pbs.twimg.com/media/' in src:
                                # 只取推文媒体图片（不是头像）
                                media_urls.append(src)
                        
                        # 提取用户头像URL（仅在账户头像未找到且这是第一条原创推文时）
                        if not account_avatar_url and not first_original_tweet_processed:
                            for img in all_imgs:
                                src = img.get('src', '')
                                if src and 'profile_images' in src:
                                    account_avatar_url = src.replace('_normal', '_400x400')
                                    logger.info(f"从第一条原创推文获取账户头像: {account_avatar_url[:80]}...")
                                    break
                            first_original_tweet_processed = True
                        
                        tweets.append({
                            'id': tweet_id,
                            'text': text,
                            'created_at': published_at,
                            'hashtags': hashtags,
                            'mentions': mentions,
                            'retweet_count': retweet_count,
                            'like_count': like_count,
                            'reply_count': reply_count,
                            'media_urls': media_urls,
                            'avatar_url': account_avatar_url,
                            'html': str(article),
                            'published_at': published_at
                        })
                        
                        new_tweets_in_this_scroll += 1
                        logger.info(f"收集推文 {tweet_id}: {text[:50]}...")
                        
                    except Exception as e:
                        logger.warning(f"解析推文失败: {e}")
                        continue
                
                # 检查本次滚动是否收集到新推文
                if new_tweets_in_this_scroll > 0:
                    logger.info(f"本次滚动收集到 {new_tweets_in_this_scroll} 条新原创推文")
                    no_new_tweets_count = 0
                else:
                    no_new_tweets_count += 1
                    logger.info(f"本次滚动没有收集到新推文 (连续 {no_new_tweets_count} 次)")
                
                # 检查是否已经收集够了
                if len(tweets) >= max_tweets:
                    logger.info(f"已收集 {len(tweets)} 条原创推文，停止滚动")
                    break
                
                # 检查是否触发连续非原创停止条件
                if consecutive_non_original >= max_consecutive_non_original:
                    logger.info(f"连续 {max_consecutive_non_original} 条非原创推文，停止滚动")
                    break
                
                # 滚动到页面底部，加载更多推文
                scroll_attempts += 1
                if scroll_attempts < max_scroll_attempts:
                    logger.info(f"向下滚动加载更多推文...")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(3)  # 等待新内容加载（增加到3秒确保加载完成）
            
            logger.info(f"成功解析 {len(tweets)} 条原创推文（已过滤转发和回复）")
            return tweets
            
        finally:
            browser.close()
