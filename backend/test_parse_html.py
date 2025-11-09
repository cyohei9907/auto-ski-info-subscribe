from bs4 import BeautifulSoup
import re
from datetime import datetime

# 读取HTML
html_file = 'data/debug_custom_skiinfomation_1762597246.html'
with open(html_file, encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# 查找所有推文
articles = soup.find_all('article', {'data-testid': 'tweet'})
print(f'Found {len(articles)} tweet articles\n')

# 解析每个推文
for i, article in enumerate(articles):
    print(f'\n=== Article {i+1} ===')
    
    # 推文文本
    tweet_text_elem = article.find('div', {'data-testid': 'tweetText'})
    tweet_text = tweet_text_elem.get_text() if tweet_text_elem else ""
    print(f'Text: {tweet_text[:100]}...' if len(tweet_text) > 100 else f'Text: {tweet_text}')
    
    # 推文ID
    tweet_link = article.find('a', href=re.compile(r'/status/\d+'))
    tweet_id = None
    if tweet_link and 'href' in tweet_link.attrs:
        match = re.search(r'/status/(\d+)', tweet_link['href'])
        if match:
            tweet_id = match.group(1)
    print(f'Tweet ID: {tweet_id}')
    
    # 时间
    time_elem = article.find('time')
    if time_elem:
        datetime_attr = time_elem.get('datetime')
        print(f'Time element found: datetime="{datetime_attr}"')
        if datetime_attr:
            try:
                posted_at = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                print(f'Parsed datetime: {posted_at}')
            except Exception as e:
                print(f'Error parsing datetime: {e}')
        else:
            print('Time element has no datetime attribute')
    else:
        print('No time element found')
    
    print('-' * 50)
