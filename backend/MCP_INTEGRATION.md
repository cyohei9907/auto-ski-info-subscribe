# MCP (Model Context Protocol) 服务集成

## 📌 概述

本系统已集成 **MCP (Model Context Protocol)** 服务，将 AI 分析后的推文数据作为标准化资源暴露出来，可被其他支持 MCP 协议的服务访问和使用。

## 🎯 核心功能

- ✅ **标准化资源格式**：遵循 MCP 协议规范，提供统一的资源表示
- ✅ **AI 增强元数据**：每个推文资源包含完整的 AI 分析结果
- ✅ **多维度筛选**：支持按情感、重要性、话题、账号等维度过滤
- ✅ **搜索功能**：全文搜索推文内容、摘要和话题
- ✅ **分页支持**：高效处理大量资源数据
- ✅ **公开访问**：MCP 资源端点无需认证（可配置）

## 📡 MCP 资源端点

### 基础 URL

```
http://localhost:8000/api/mcp/
```

### 推文资源 (Tweets)

#### 1. 列出所有推文资源

```http
GET /api/mcp/tweets/
```

**查询参数**：

- `limit` - 每页数量 (默认: 20, 最大: 100)
- `page` - 页码
- `sentiment` - 按情感筛选 (positive/negative/neutral)
- `min_importance` - 最低重要性分数 (0.0-1.0)
- `account` - 按账号用户名筛选
- `days` - 筛选最近 N 天的推文

**响应示例**：

```json
{
  "mcp_version": "1.0",
  "resource_type": "tweet",
  "count": 150,
  "next": "http://localhost:8000/api/mcp/tweets/?page=2",
  "previous": null,
  "results": [
    {
      "uri": "mcp://tweets/1234567890",
      "name": "Tweet from @username",
      "description": "AI生成的推文摘要...",
      "mimeType": "application/json",
      "text": "推文原始内容...",
      "metadata": {
        "author": "username",
        "author_name": "User Display Name",
        "author_avatar": "https://...",
        "tweet_id": "1234567890",
        "tweet_url": "https://twitter.com/username/status/1234567890",
        "posted_at": "2025-11-10T12:00:00Z",
        "created_at": "2025-11-10T12:05:00Z",
        "engagement": {
          "retweets": 10,
          "likes": 50,
          "replies": 5
        },
        "is_retweet": false,
        "has_media": true,
        "media_urls": ["https://..."],
        "hashtags": ["スキー", "雪"],
        "mentions": ["@another_user"],
        "ai_analysis": {
          "sentiment": "positive",
          "summary": "今日のゲレンデは最高の雪質で楽しめました",
          "topics": ["スキー", "雪質", "ゲレンデ"],
          "importance_score": 0.85,
          "processed_at": "2025-11-10T12:06:00Z"
        },
        "ai_relevant": true,
        "ai_analyzed": true
      }
    }
  ]
}
```

#### 2. 获取特定推文资源

```http
GET /api/mcp/tweets/{tweet_id}/
```

**示例**：

```bash
curl http://localhost:8000/api/mcp/tweets/1234567890/
```

#### 3. 只获取 AI 相关推文

```http
GET /api/mcp/tweets/relevant/
```

返回所有被 AI 标记为相关的推文（`ai_relevant=True`）。

#### 4. 搜索推文

```http
GET /api/mcp/tweets/search/?q={query}
```

**查询参数**：

- `q` - 搜索关键词（搜索内容和摘要）
- `topics` - 按话题筛选（逗号分隔）
- `hashtags` - 按标签筛选（逗号分隔）

**示例**：

```bash
# 搜索包含"スキー"的推文
curl "http://localhost:8000/api/mcp/tweets/search/?q=スキー"

# 按话题筛选
curl "http://localhost:8000/api/mcp/tweets/search/?topics=雪質,天気"

# 按标签筛选
curl "http://localhost:8000/api/mcp/tweets/search/?hashtags=スキー,snowboarding"
```

#### 5. 按情感筛选

```http
GET /api/mcp/tweets/by_sentiment/?sentiment={sentiment}
```

**sentiment 取值**：

- `positive` - 积极情感
- `negative` - 消极情感
- `neutral` - 中性情感

**示例**：

```bash
curl "http://localhost:8000/api/mcp/tweets/by_sentiment/?sentiment=positive"
```

### 账号资源 (Accounts)

#### 1. 列出所有监控账号

```http
GET /api/mcp/accounts/
```

**响应示例**：

```json
{
  "count": 5,
  "results": [
    {
      "uri": "mcp://accounts/username",
      "name": "X Account @username",
      "description": "User Display Name",
      "mimeType": "application/json",
      "metadata": {
        "username": "username",
        "display_name": "User Display Name",
        "x_user_id": "12345",
        "avatar_url": "https://...",
        "is_active": true,
        "monitoring_interval": 240,
        "ai_filter_enabled": true,
        "total_tweets": 150,
        "analyzed_tweets": 145,
        "relevant_tweets": 80,
        "last_checked": "2025-11-10T12:00:00Z",
        "created_at": "2025-11-01T10:00:00Z"
      }
    }
  ]
}
```

#### 2. 获取特定账号的推文

```http
GET /api/mcp/accounts/{username}/tweets/
```

返回指定账号的所有已分析推文。

**示例**：

```bash
curl http://localhost:8000/api/mcp/accounts/ski_info_jp/tweets/
```

## 🔌 MCP 客户端使用示例

### Python 示例

```python
import requests

# 获取所有 AI 相关推文
response = requests.get('http://localhost:8000/api/mcp/tweets/relevant/')
data = response.json()

for tweet in data['results']:
    print(f"URI: {tweet['uri']}")
    print(f"作者: @{tweet['metadata']['author']}")
    print(f"内容: {tweet['text'][:100]}...")

    ai = tweet['metadata'].get('ai_analysis', {})
    print(f"情感: {ai.get('sentiment')}")
    print(f"重要性: {ai.get('importance_score')}")
    print(f"摘要: {ai.get('summary')}")
    print(f"话题: {', '.join(ai.get('topics', []))}")
    print("-" * 80)
```

### JavaScript 示例

```javascript
// 搜索相关推文
async function searchTweets(query) {
  const response = await fetch(
    `http://localhost:8000/api/mcp/tweets/search/?q=${encodeURIComponent(
      query
    )}`
  );
  const data = await response.json();

  data.results.forEach((tweet) => {
    console.log(`URI: ${tweet.uri}`);
    console.log(`作者: @${tweet.metadata.author}`);
    console.log(`摘要: ${tweet.metadata.ai_analysis?.summary}`);
    console.log(`话题: ${tweet.metadata.ai_analysis?.topics?.join(", ")}`);
    console.log("-".repeat(80));
  });
}

// 使用示例
searchTweets("スキー場");
```

### cURL 示例

```bash
# 获取最重要的推文（importance >= 0.8）
curl "http://localhost:8000/api/mcp/tweets/?min_importance=0.8&limit=10"

# 获取最近3天的积极情感推文
curl "http://localhost:8000/api/mcp/tweets/?sentiment=positive&days=3"

# 按账号筛选
curl "http://localhost:8000/api/mcp/tweets/?account=ski_resort_official"
```

## 🏗️ MCP 资源结构

### 标准字段

每个 MCP 资源都包含以下标准字段：

| 字段          | 类型   | 说明                       |
| ------------- | ------ | -------------------------- |
| `uri`         | string | MCP 资源唯一标识符         |
| `name`        | string | 资源名称                   |
| `description` | string | 资源描述（通常是 AI 摘要） |
| `mimeType`    | string | 资源 MIME 类型             |
| `text`        | string | 资源文本内容（推文原文）   |
| `metadata`    | object | 扩展元数据                 |

### AI 分析元数据

`metadata.ai_analysis` 对象包含：

| 字段               | 类型   | 说明                                 |
| ------------------ | ------ | ------------------------------------ |
| `sentiment`        | string | 情感倾向 (positive/negative/neutral) |
| `summary`          | string | AI 生成的推文摘要                    |
| `topics`           | array  | 提取的主题标签                       |
| `importance_score` | float  | 重要性评分 (0.0-1.0)                 |
| `processed_at`     | string | AI 分析时间 (ISO 8601)               |

## 🔧 配置选项

### 启用/禁用 MCP 服务

MCP 服务默认启用。如需禁用，可在 `settings.py` 中移除 `mcp_service` 应用。

### 访问权限控制

默认配置下，MCP 端点允许匿名访问。如需要认证，修改 `mcp_service/views.py`：

```python
class MCPTweetResourceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]  # 需要认证
    # ...
```

### 自定义分页大小

修改 `mcp_service/views.py` 中的 `MCPResourcePagination`：

```python
class MCPResourcePagination(PageNumberPagination):
    page_size = 50  # 默认每页数量
    page_size_query_param = 'limit'
    max_page_size = 200  # 最大每页数量
```

## 🧪 测试 MCP 服务

运行测试脚本：

```bash
cd backend
python test_mcp_service.py
```

测试脚本会执行以下测试：

1. ✅ 列出所有推文资源
2. ✅ 获取特定推文资源
3. ✅ 列出 AI 相关推文
4. ✅ 搜索推文
5. ✅ 按情感筛选
6. ✅ 列出账号资源
7. ✅ 获取账号推文

## 📊 使用场景

### 1. 与 LLM 集成

将推文资源作为上下文提供给大语言模型：

```python
import openai

# 获取相关推文
response = requests.get('http://localhost:8000/api/mcp/tweets/relevant/?limit=5')
tweets = response.json()['results']

# 构建上下文
context = "\n\n".join([
    f"推文 {i+1}:\n{tweet['text']}\n摘要: {tweet['metadata']['ai_analysis']['summary']}"
    for i, tweet in enumerate(tweets)
])

# 向 LLM 提问
completion = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "你是一个滑雪场信息助手"},
        {"role": "user", "content": f"根据以下推文，总结今日滑雪场状况:\n\n{context}"}
    ]
)
```

### 2. 构建推荐系统

基于 AI 分析结果推荐相关推文：

```python
# 获取高重要性的积极推文
response = requests.get(
    'http://localhost:8000/api/mcp/tweets/',
    params={
        'sentiment': 'positive',
        'min_importance': 0.7,
        'days': 1
    }
)

recommendations = response.json()['results']
```

### 3. 数据分析和可视化

导出推文数据进行分析：

```python
import pandas as pd

response = requests.get('http://localhost:8000/api/mcp/tweets/?limit=100')
tweets = response.json()['results']

# 转换为 DataFrame
df = pd.DataFrame([
    {
        'author': t['metadata']['author'],
        'sentiment': t['metadata']['ai_analysis']['sentiment'],
        'importance': t['metadata']['ai_analysis']['importance_score'],
        'topics': ','.join(t['metadata']['ai_analysis']['topics']),
        'posted_at': t['metadata']['posted_at']
    }
    for t in tweets
])

# 情感分布统计
print(df['sentiment'].value_counts())

# 平均重要性
print(f"平均重要性: {df['importance'].mean():.2f}")
```

## 🔒 安全建议

1. **生产环境部署**：

   - 使用 HTTPS
   - 配置适当的 CORS 策略
   - 考虑添加认证和速率限制

2. **数据隐私**：

   - 确保只暴露公开推文
   - 遵守推特服务条款
   - 不暴露用户敏感信息

3. **性能优化**：
   - 使用缓存（Redis）
   - 配置合理的分页大小
   - 考虑 CDN 加速

## 📚 参考资料

- [Model Context Protocol 规范](https://spec.modelcontextprotocol.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [项目主 README](../README.md)

---

**最后更新**: 2025-11-10  
**MCP 版本**: 1.0
