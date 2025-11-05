# 推文监控功能改进总结

## ✅ 已完成的后端改进

### 1. 数据库模型更新 (`x_monitor/models.py`)

#### XAccount 模型新增字段:

- `ai_filter_enabled`: 智能推荐开关(默认 False)
- `fetch_from_date`: 开始拉取推文的日期
- `fetch_to_date`: 结束拉取推文的日期

#### Tweet 模型新增字段:

- `ai_analyzed`: 是否已进行 AI 分析
- `ai_relevant`: AI 判断是否相关
- `ai_summary`: AI 生成的摘要

### 2. 序列化器更新 (`x_monitor/serializers.py`)

#### XAccountSerializer:

- 添加 `ai_filter_enabled`, `fetch_from_date`, `fetch_to_date` 字段

#### TweetSerializer:

- 添加用户头像 `x_account_avatar`
- 添加显示名称 `x_account_display_name`
- 添加 AI 相关字段 `ai_analyzed`, `ai_relevant`, `ai_summary`
- 添加推文 URL `tweet_url`

### 3. 数据库迁移

- 已生成并应用迁移文件 `0002_rename_analyzed_at_aianalysis_processed_at_and_more.py`

## ✅ 已创建的前端组件

### 1. TweetCard 组件 (`components/TweetCard.js`)

**功能特性**:

- ✅ X 风格的推文卡片设计
- ✅ 显示用户头像、用户名、显示名称
- ✅ 显示 X (Twitter) 认证图标
- ✅ 格式化时间显示(刚刚、X 分钟前、X 小时前等)
- ✅ Hashtag 和 @mention 高亮显示
- ✅ 媒体图片网格展示(支持 1-4 张图片)
- ✅ 互动数据显示(回复、转发、点赞)
- ✅ AI 推荐标签显示
- ✅ AI 摘要卡片展示
- ✅ 点击查看原推链接
- ✅ 响应式设计

**样式文件** (`components/TweetCard.css`):

- X 风格的视觉设计
- 悬停效果
- 媒体网格布局
- 移动端适配

## 📋 需要完成的工作

### 后端 API 端点

需要在 `x_monitor/views.py` 中添加或更新以下端点:

```python
# 1. 获取推文列表(支持过滤)
GET /api/monitor/tweets/
Query Params:
  - account_id: 账户ID
  - ai_filter: 是否只显示AI推荐(true/false)
  - from_date: 开始日期(YYYY-MM-DD)
  - to_date: 结束日期(YYYY-MM-DD)

# 2. 更新账户设置
PATCH /api/monitor/accounts/{id}/
Body:
  - ai_filter_enabled: boolean
  - fetch_from_date: date
  - fetch_to_date: date

# 3. 手动触发监控
POST /api/monitor/accounts/{id}/monitor/
```

### 前端页面更新

需要更新 `pages/TweetsPage.js`:

1. **集成 TweetCard 组件**

   ```javascript
   import TweetCard from "../components/TweetCard";
   ```

2. **添加智能推荐开关**

   ```javascript
   <Switch
     checked={aiFilterEnabled}
     onChange={handleAiFilterToggle}
     checkedChildren="开启"
     unCheckedChildren="关闭"
   />
   ```

3. **添加日期范围选择器**

   ```javascript
   <RangePicker
     value={dateRange}
     onChange={handleDateRangeChange}
     format="YYYY-MM-DD"
   />
   ```

4. **统计信息展示**
   - 总推文数
   - 今日推文数
   - AI 推荐数

### AI 分析服务

需要在 `ai_service/services.py` 中实现:

```python
class TweetAnalysisService:
    def analyze_tweet(self, tweet: Tweet) -> dict:
        """
        分析推文内容
        - 仅在 ai_filter_enabled=True 时调用
        - 判断推文是否与滑雪相关
        - 生成摘要
        - 更新 Tweet.ai_analyzed, ai_relevant, ai_summary
        """
        pass
```

### Celery 任务更新

在 `x_monitor/tasks.py` 中更新任务:

```python
@shared_task
def monitor_account_with_ai(account_id):
    """监控账户并可选进行AI分析"""
    account = XAccount.objects.get(id=account_id)

    # 1. 爬取推文
    monitor_service.monitor_account(account)

    # 2. 如果开启AI过滤,对未分析的推文进行分析
    if account.ai_filter_enabled:
        unanalyzed_tweets = account.tweets.filter(ai_analyzed=False)
        for tweet in unanalyzed_tweets:
            ai_service.analyze_tweet(tweet)
```

## 🎯 使用流程

### 1. 添加监控账户

```
用户 -> 账户页面 -> 添加 @username
```

### 2. 配置监控设置

```
用户 -> 推文页面 -> 选择账户 -> 设置选项:
  - 开启/关闭智能推荐
  - 设置日期范围
```

### 3. 查看推文

```
推文页面 -> X 风格的推文卡片列表:
  - 显示用户头像
  - 显示推文内容
  - 显示互动数据
  - AI推荐标签(如果开启)
  - AI摘要(如果已分析)
```

### 4. 自动化流程

```
Celery Beat (定时任务):
  每小时 -> 爬取所有账户推文

账户配置 ai_filter_enabled=True时:
  爬取完成 -> 自动AI分析 -> 标记相关推文 -> 生成摘要

前端显示:
  只显示 ai_relevant=True 的推文(当开关开启时)
```

## 🔧 测试步骤

### 1. 测试数据库迁移

```bash
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
```

### 2. 测试 API 端点

```bash
# 创建测试账户
POST /api/monitor/accounts/
{
  "username": "niseko_official"
}

# 更新设置
PATCH /api/monitor/accounts/1/
{
  "ai_filter_enabled": true,
  "fetch_from_date": "2025-11-01",
  "fetch_to_date": "2025-11-05"
}

# 获取推文
GET /api/monitor/tweets/?account_id=1&ai_filter=true
```

### 3. 测试前端界面

```bash
# 访问推文页面
http://localhost:3000/tweets

# 验证功能:
- 账户选择下拉框
- 智能推荐开关
- 日期范围选择
- 推文卡片显示
- AI推荐标签
- 互动数据
```

## 📝 注意事项

1. **AI 分析默认关闭**: 新添加的账户 `ai_filter_enabled` 默认为 `False`
2. **按需分析**: 只有当用户主动开启智能推荐时,才会对推文进行 AI 分析
3. **日期过滤**: 前端可以按日期范围过滤显示的推文
4. **性能考虑**: AI 分析应该异步进行,不阻塞爬取流程
5. **成本控制**: AI API 调用需要计费,默认关闭可以控制成本

## 🚀 下一步工作

1. 完成 `x_monitor/views.py` 的 API 端点实现
2. 集成 TweetCard 到 TweetsPage
3. 实现 AI 分析服务
4. 更新 Celery 任务支持条件 AI 分析
5. 添加单元测试
6. 更新 API 文档
