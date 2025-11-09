#!/usr/bin/env python
"""检查推文HTML中的图片元素"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

username = "skiinfomation"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 设置为False以便观察
    page = browser.new_page()
    
    # 访问账户页面
    url = f"https://x.com/{username}"
    logger.info(f"访问: {url}")
    page.goto(url, wait_until='domcontentloaded', timeout=30000)
    
    # 等待推文加载
    page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
    logger.info("页面加载完成")
    
    # 获取HTML
    html = page.content()
    soup = BeautifulSoup(html, 'lxml')
    
    # 查找第一个推文
    article = soup.find('article', {'data-testid': 'tweet'})
    if article:
        print("=" * 80)
        print("第一条推文的结构分析:")
        print("=" * 80)
        
        # 查找所有图片
        all_imgs = article.find_all('img')
        print(f"\n找到 {len(all_imgs)} 个 <img> 标签:")
        for i, img in enumerate(all_imgs, 1):
            print(f"\n图片 {i}:")
            print(f"  src: {img.get('src', '(无)')[:100]}")
            print(f"  alt: {img.get('alt', '(无)')}")
            print(f"  class: {img.get('class', '(无)')}")
            print(f"  父元素: {img.parent.name if img.parent else '(无)'}")
            if img.parent:
                print(f"  父元素class: {img.parent.get('class', '(无)')}")
        
        # 查找视频
        videos = article.find_all('video')
        print(f"\n找到 {len(videos)} 个 <video> 标签")
        
        # 查找媒体容器
        media_containers = article.find_all('div', {'data-testid': lambda x: x and 'media' in x.lower()})
        print(f"\n找到 {len(media_containers)} 个媒体容器 (data-testid包含'media')")
        
        # 查找用户头像
        print("\n" + "=" * 80)
        print("用户头像:")
        print("=" * 80)
        avatar_imgs = soup.find_all('img', {'alt': lambda x: x and username in x.lower()})
        print(f"找到 {len(avatar_imgs)} 个可能的头像图片")
        for i, img in enumerate(avatar_imgs, 1):
            print(f"\n头像候选 {i}:")
            print(f"  src: {img.get('src', '(无)')}")
            print(f"  alt: {img.get('alt', '(无)')}")
    
    browser.close()
