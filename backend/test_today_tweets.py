"""
测试获取当日推文功能
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
django.setup()

from x_monitor.services import XScraperClient
from django.utils import timezone

def test_today_tweets(username):
    """测试获取指定用户的当日推文"""
    print(f"\n{'='*60}")
    print(f"测试获取 @{username} 的当日推文")
    print(f"{'='*60}\n")
    
    scraper = XScraperClient()
    
    # 获取当日推文
    print("📥 正在获取当日推文...")
    today_tweets = scraper.get_today_tweets(username)
    
    print(f"\n✅ 找到 {len(today_tweets)} 条当日推文\n")
    
    # 显示推文详情
    today = timezone.now().date()
    print(f"📅 日期: {today}\n")
    
    for i, tweet in enumerate(today_tweets, 1):
        print(f"{'='*60}")
        print(f"推文 #{i}")
        print(f"{'='*60}")
        print(f"🆔 ID: {tweet['id']}")
        print(f"📝 内容: {tweet['text'][:100]}...")
        print(f"🕐 时间: {tweet['created_at']}")
        print(f"💬 回复: {tweet['reply_count']}")
        print(f"🔁 转发: {tweet['retweet_count']}")
        print(f"❤️  点赞: {tweet['like_count']}")
        if tweet['hashtags']:
            print(f"🏷️  标签: {', '.join(['#' + tag for tag in tweet['hashtags']])}")
        print()
    
    # 同时获取最近推文进行对比
    print(f"\n{'='*60}")
    print("📥 对比: 获取最近20条推文")
    print(f"{'='*60}\n")
    
    recent_tweets = scraper.get_recent_tweets(username, max_results=20)
    print(f"✅ 找到 {len(recent_tweets)} 条最近推文")
    
    # 统计不同日期的推文数量
    date_counts = {}
    for tweet in recent_tweets:
        date = tweet['created_at'].date()
        date_counts[date] = date_counts.get(date, 0) + 1
    
    print("\n📊 推文日期分布:")
    for date in sorted(date_counts.keys(), reverse=True):
        marker = "👉" if date == today else "  "
        print(f"{marker} {date}: {date_counts[date]} 条推文")
    
    print(f"\n{'='*60}\n")

if __name__ == '__main__':
    # 默认测试用户名，可以修改为实际的滑雪场博主
    test_username = input("请输入要测试的 X (Twitter) 用户名 (不带@): ").strip()
    
    if not test_username:
        print("❌ 用户名不能为空")
        sys.exit(1)
    
    try:
        test_today_tweets(test_username)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
