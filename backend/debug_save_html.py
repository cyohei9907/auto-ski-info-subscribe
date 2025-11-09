#!/usr/bin/env python
"""保存当前HTML用于调试"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from playwright.sync_api import sync_playwright
import time

def save_current_html():
    """保存当前页面HTML"""
    username = 'skiinfomation'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 不使用无头模式，可以看到浏览器
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            bypass_csp=True,
        )
        
        # 加载cookies
        from django.conf import settings
        cookies_path = settings.BASE_DIR / 'data' / 'twitter_cookies.json'
        if cookies_path.exists():
            import json
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
                print(f"✓ 已加载 {len(cookies)} 个cookies")
        
        page = context.new_page()
        
        url = f"https://x.com/{username}"
        print(f"访问: {url}")
        page.goto(url, wait_until='domcontentloaded')
        print("页面加载完成，等待5秒...")
        time.sleep(5)
        
        # 保存HTML
        html = page.content()
        output_file = os.path.join(os.path.dirname(__file__), 'data', f'debug_current_{username}.html')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✓ HTML已保存到: {output_file}")
        print(f"  大小: {len(html)} bytes")
        
        # 查找所有 <time> 元素
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')
        articles = soup.find_all('article', {'data-testid': 'tweet'})
        
        print(f"\n找到 {len(articles)} 个推文 article:")
        for i, article in enumerate(articles[:10], 1):
            time_elem = article.find('time')
            if time_elem:
                datetime_attr = time_elem.get('datetime', 'NO DATETIME')
                time_text = time_elem.get_text(strip=True)
                print(f"  {i}. datetime='{datetime_attr}', text='{time_text}'")
            else:
                print(f"  {i}. ❌ 没有 <time> 元素")
        
        browser.close()

if __name__ == '__main__':
    save_current_html()
