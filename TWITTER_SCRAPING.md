# X (Twitter) 当日推文监控功能

## 概述

本项目新增了专门获取博主当日推文的功能,可以精确监控滑雪场相关博主每天发布的最新信息。

## 功能特性

### 1. 当日推文获取 (`get_today_tweets`)

新增方法可以自动过滤并获取指定博主当天发布的所有推文。

**位置**: `backend/x_monitor/services.py`

```python
def get_today_tweets(self, username: str) -> List[Dict]:
    """当日のツイートのみを取得"""
```

**功能**:

- 自动获取最近 50 条推文
- 按日期过滤,只返回当天发布的推文
- 记录日志便于追踪

### 2. 改进的监控方法 (`monitor_account`)

支持可选参数来指定是否只获取当日推文。

```python
def monitor_account(self, x_account: XAccount, today_only: bool = False) -> dict:
```

**参数**:

- `x_account`: 要监控的 X 账户
- `today_only`: True 时只获取当日推文,False 时获取最近 20 条

### 3. 新增 Celery 定时任务

#### `monitor_today_tweets` 任务

专门用于监控所有活跃账户的当日推文。

**位置**: `backend/x_monitor/tasks.py`

```python
@shared_task
def monitor_today_tweets():
    """すべてのアクティブなアカウントの当日ツイートを監視するタスク"""
```

#### 定时调度配置

在 `settings.py` 中配置了自动调度:

```python
CELERY_BEAT_SCHEDULE = {
    'monitor-all-accounts-hourly': {
        'task': 'x_monitor.tasks.monitor_all_active_accounts',
        'schedule': 3600.0,  # 每小时执行一次
    },
    'monitor-today-tweets-morning': {
        'task': 'x_monitor.tasks.monitor_today_tweets',
        'schedule': crontab(hour=9, minute=0),  # 每天9:00
    },
    'monitor-today-tweets-noon': {
        'task': 'x_monitor.tasks.monitor_today_tweets',
        'schedule': crontab(hour=12, minute=0),  # 每天12:00
    },
    'monitor-today-tweets-evening': {
        'task': 'x_monitor.tasks.monitor_today_tweets',
        'schedule': crontab(hour=18, minute=0),  # 每天18:00
    },
}
```

**调度说明**:

- 每小时监控所有活跃账户(获取最近 20 条推文)
- 每天 9:00、12:00、18:00 专门获取当日推文
- 可根据需要调整时间

## 测试脚本

提供了独立的测试脚本来验证当日推文获取功能。

**位置**: `backend/test_today_tweets.py`

### 使用方法

```bash
# 在 Docker 容器中运行
docker-compose -f docker-compose.dev.yml exec backend python test_today_tweets.py

# 输入要测试的用户名(不带@)
请输入要测试的 X (Twitter) 用户名 (不带@): elonmusk
```

### 测试输出示例

```
============================================================
测试获取 @elonmusk 的当日推文
============================================================

📥 正在获取当日推文...

✅ 找到 5 条当日推文

📅 日期: 2025-11-05

============================================================
推文 #1
============================================================
🆔 ID: 1234567890
📝 内容: Example tweet content...
🕐 时间: 2025-11-05 08:30:00+00:00
💬 回复: 150
🔁 转发: 320
❤️  点赞: 1500
🏷️  标签: #example, #test

...

============================================================
📥 对比: 获取最近20条推文
============================================================

✅ 找到 20 条最近推文

📊 推文日期分布:
👉 2025-11-05: 5 条推文
   2025-11-04: 8 条推文
   2025-11-03: 7 条推文
```

## 手动触发任务

### 触发当日推文监控

```python
# Django shell 中
from x_monitor.tasks import monitor_today_tweets
result = monitor_today_tweets.delay()
```

### 触发单个账户监控(仅当日推文)

```python
from x_monitor.tasks import monitor_single_account
from x_monitor.models import XAccount

account = XAccount.objects.get(username='example_user')
monitor_service = XMonitorService()
result = monitor_service.monitor_account(account, today_only=True)
```

## 数据库查询

### 查询当日推文

```python
from django.utils import timezone
from x_monitor.models import Tweet

today = timezone.now().date()
today_tweets = Tweet.objects.filter(
    posted_at__date=today,
    x_account__username='example_user'
).order_by('-posted_at')
```

### 查询某账户的统计信息

```python
from x_monitor.models import XAccount

account = XAccount.objects.get(username='example_user')
total_tweets = account.tweets.count()
today_tweets = account.tweets.filter(posted_at__date=timezone.now().date()).count()

print(f"总推文数: {total_tweets}")
print(f"今日推文数: {today_tweets}")
```

## API 端点

如需通过 API 访问当日推文,可以扩展现有的视图:

```python
# 在 x_monitor/views.py 中添加
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_today_tweets(request, username):
    """获取指定用户的当日推文"""
    today = timezone.now().date()
    tweets = Tweet.objects.filter(
        x_account__username=username,
        posted_at__date=today
    ).order_by('-posted_at')

    serializer = TweetSerializer(tweets, many=True)
    return Response(serializer.data)
```

## 注意事项

1. **频率限制**: Twitter/X 对爬取有频率限制,建议合理设置调度间隔
2. **Headless 浏览器**: 使用 Playwright 进行爬取,确保 Chromium 已正确安装
3. **时区处理**: 所有时间使用 Django 的 timezone,默认为 Asia/Tokyo
4. **错误处理**: 爬取失败会记录到 MonitoringLog,便于排查问题

## 未来改进

- [ ] 支持按关键词过滤推文
- [ ] 支持图片和视频附件下载
- [ ] 添加推文内容的 AI 分析
- [ ] 支持 Email/Slack 通知新推文
- [ ] 优化大量账户的并发爬取性能
