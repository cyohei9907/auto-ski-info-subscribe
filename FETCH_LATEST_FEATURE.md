# 立即获取最新 10 条推文功能

## 功能说明

在账户管理页面，每个账户都有一个 **"最新 10 条"** 按钮，点击后会立即从 X/Twitter 获取该账户最近 6 小时内发布的最新 10 条推文。

## 使用方法

1. 打开前端页面：http://localhost:3000
2. 进入 "アカウント管理" (账户管理) 页面
3. 找到要获取推文的账户
4. 点击 **"最新 10 条"** 按钮
5. 系统会：
   - 立即启动爬虫获取最新推文
   - 只获取最近 6 小时内的推文
   - 保存到数据库
   - 显示获取到的推文数量

## 功能特点

### 后端 API

- **端点**: `POST /api/monitor/accounts/{account_id}/fetch-latest/`
- **功能**:
  - 使用爬虫实时抓取最新 10 条推文
  - 自动过滤 6 小时前的旧推文
  - 只保存新推文（避免重复）
  - 返回新获取的推文数量

### 前端界面

- 在账户列表的操作列添加了蓝色的 **"最新 10 条"** 按钮
- 点击后显示加载状态
- 完成后显示获取结果通知
- 自动刷新账户列表数据

## 技术实现

### 1. 后端 (views.py)

```python
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fetch_latest_tweets(request, account_id):
    """立即获取账户的最新10条推文"""
    x_account = get_object_or_404(XAccount, id=account_id, user=request.user)
    monitor_service = XMonitorService()
    result = monitor_service.monitor_account(x_account, max_tweets=10)
    return Response({
        'success': True,
        'message': f'{result.get("new_tweets", 0)}条の新しい推文を取得しました',
        'new_tweets': result.get('new_tweets', 0)
    })
```

### 2. 前端 (AccountsPage.js)

```javascript
const fetchLatestMutation = useMutation(monitorAPI.fetchLatestTweets, {
  onSuccess: (response) => {
    const newTweets = response.data?.new_tweets || 0;
    message.success(`${newTweets}条の新しい推文を取得しました`);
    queryClient.invalidateQueries("accounts");
  },
  onError: () => {
    message.error("推文の取得に失敗しました");
  },
});
```

### 3. 爬虫优化

- 禁用字体和样式表加载（保留图片和视频）
- 最小化滚动次数
- 6 小时时间过滤
- 随机延迟防检测

## 注意事项

1. **时间过滤**: 只获取最近 6 小时内的推文
2. **去重机制**: 已存在的推文不会重复保存
3. **性能优化**: 页面加载已优化，但仍需等待 15-30 秒（防检测延迟）
4. **速率限制**: 建议不要频繁点击，避免被 X/Twitter 检测

## 测试

访问前端页面测试：

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- Admin: http://localhost:8000/admin
