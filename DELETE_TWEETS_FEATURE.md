# 推文删除功能说明

## 功能概述

为系统添加了完整的推文删除功能，包括：

1. **单条推文删除** - 在每条推文卡片上添加删除按钮
2. **批量删除** - 删除指定账户的所有推文

## 后端 API

### 1. 删除单条推文

**端点**: `DELETE /api/monitor/tweets/{tweet_id}/delete/`

**权限**: 需要登录，只能删除自己监控账户的推文

**响应**:

```json
{
  "success": true,
  "message": "推文已删除: 推文内容前50字..."
}
```

**错误响应**:

```json
{
  "success": false,
  "message": "推文不存在或无权限删除"
}
```

### 2. 批量删除账户推文

**端点**: `DELETE /api/monitor/accounts/{account_id}/tweets/delete/?confirm=yes`

**权限**: 需要登录，只能删除自己的账户推文

**参数**:

- `confirm` (必需): 必须传入 `yes` 以确认批量删除操作

**响应**:

```json
{
  "success": true,
  "message": "已删除 @username 的所有推文",
  "deleted_count": 42
}
```

**错误响应**:

```json
// 缺少确认参数
{
  "success": false,
  "message": "请传入 confirm=yes 参数以确认删除"
}

// 账户不存在或无权限
{
  "success": false,
  "message": "账户不存在或无权限"
}
```

## 前端 UI

### 推文卡片上的删除按钮

每条推文卡片的右下角都有一个"删除"按钮：

**特点**:

- 🔴 红色文字和图标，醒目警示
- 点击后弹出确认对话框
- 确认框显示: "确定要删除这条推文吗？"
- 删除成功后自动从列表中移除
- 显示成功消息: "推文已删除"

### 批量删除按钮

在推文页面的控制面板中，当有推文数据时显示"删除所有推文"按钮：

**特点**:

- 🔴 危险按钮样式（红色边框）
- 显示删除图标
- 点击后弹出确认对话框
- 确认框显示账户名和推文数量
- 提示"此操作不可恢复！"
- 删除成功后显示删除数量
- 自动清空列表并重新加载

**确认对话框示例**:

```
批量删除推文
确定要删除 @skiinfomation 的所有 156 条推文吗？此操作不可恢复！
[取消] [确认删除]
```

## 代码实现

### Backend - views.py

```python
@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_tweet(request, tweet_id):
    """删除单个推文"""
    try:
        tweet = Tweet.objects.get(
            id=tweet_id,
            x_account__user=request.user
        )
        tweet_content = tweet.content[:50]
        tweet.delete()

        logger.info(f"Tweet {tweet_id} deleted by user {request.user.email}")
        return Response({
            'success': True,
            'message': f'推文已删除: {tweet_content}...'
        })
    except Tweet.DoesNotExist:
        return Response({
            'success': False,
            'message': '推文不存在或无权限删除'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_account_tweets(request, account_id):
    """删除指定账户的所有推文"""
    confirm = request.query_params.get('confirm')
    if confirm != 'yes':
        return Response({
            'success': False,
            'message': '请传入 confirm=yes 参数以确认删除'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        x_account = XAccount.objects.get(
            id=account_id,
            user=request.user
        )

        tweet_count = Tweet.objects.filter(x_account=x_account).count()
        deleted_count, _ = Tweet.objects.filter(x_account=x_account).delete()

        logger.info(f"Deleted {deleted_count} tweets from account @{x_account.username}")

        return Response({
            'success': True,
            'message': f'已删除 @{x_account.username} 的所有推文',
            'deleted_count': tweet_count
        })
    except XAccount.DoesNotExist:
        return Response({
            'success': False,
            'message': '账户不存在或无权限'
        }, status=status.HTTP_404_NOT_FOUND)
```

### Backend - urls.py

```python
urlpatterns = [
    # ... 其他路由
    path('tweets/<int:tweet_id>/delete/', views.delete_tweet, name='delete-tweet'),
    path('accounts/<int:account_id>/tweets/delete/', views.delete_account_tweets, name='delete-account-tweets'),
]
```

### Frontend - api.js

```javascript
export const monitorAPI = {
  // ... 其他API
  deleteTweet: (id) => api.delete(`/monitor/tweets/${id}/delete/`),
  deleteAccountTweets: (accountId) =>
    api.delete(`/monitor/accounts/${accountId}/tweets/delete/?confirm=yes`),
};
```

### Frontend - TweetCard.js

```javascript
const handleDelete = async () => {
  try {
    await monitorAPI.deleteTweet(id);
    message.success("推文已删除");
    if (onDelete) {
      onDelete(id);
    }
  } catch (error) {
    message.error(
      "删除失败: " + (error.response?.data?.message || error.message)
    );
  }
};

// 在卡片底部添加删除按钮
<Popconfirm
  title="确认删除"
  description="确定要删除这条推文吗？"
  onConfirm={handleDelete}
  okText="删除"
  cancelText="取消"
  okButtonProps={{ danger: true }}
>
  <Button type="text" danger icon={<DeleteOutlined />} size="small">
    删除
  </Button>
</Popconfirm>;
```

### Frontend - TweetsPage.js

```javascript
const handleDeleteTweet = (tweetId) => {
  // 从列表中移除已删除的推文
  setTweets(tweets.filter((t) => t.id !== tweetId));
  // 重新加载统计信息
  loadTweets();
};

const handleDeleteAllTweets = async () => {
  if (!selectedAccount) return;

  try {
    const response = await monitorAPI.deleteAccountTweets(selectedAccount);
    message.success(`已删除 ${response.data.deleted_count} 条推文`);
    setTweets([]);
    loadTweets();
  } catch (error) {
    message.error("批量删除失败: " + error.message);
  }
};

// 在控制面板添加批量删除按钮
{
  selectedAccount && tweets.length > 0 && (
    <Popconfirm
      title="批量删除推文"
      description={`确定要删除 @${selectedAccountData?.username} 的所有 ${tweets.length} 条推文吗？此操作不可恢复！`}
      onConfirm={handleDeleteAllTweets}
      okText="确认删除"
      cancelText="取消"
      okButtonProps={{ danger: true }}
    >
      <Button danger icon={<DeleteOutlined />}>
        删除所有推文
      </Button>
    </Popconfirm>
  );
}
```

## 安全特性

1. **权限验证**

   - 所有删除操作都需要登录认证
   - 用户只能删除自己监控账户的推文
   - 后端验证 `x_account__user=request.user`

2. **二次确认**

   - 单条删除：弹出确认对话框
   - 批量删除：需要确认对话框 + confirm 参数
   - 确认框明确显示将要删除的内容

3. **操作日志**

   - 删除操作会记录到后端日志
   - 包含用户邮箱、推文 ID、账户名等信息

4. **错误处理**
   - 推文不存在或无权限时返回 404
   - 缺少确认参数时返回 400
   - 前端显示友好的错误提示

## 使用流程

### 删除单条推文

1. 访问 http://localhost:3000/tweets
2. 选择要查看的账户
3. 在推文卡片右下角找到"删除"按钮
4. 点击按钮，弹出确认对话框
5. 点击"删除"确认
6. 推文从列表中消失，显示成功消息

### 批量删除推文

1. 访问 http://localhost:3000/tweets
2. 选择要清空的账户
3. 在控制面板找到"删除所有推文"按钮（红色危险按钮）
4. 点击按钮，弹出确认对话框（显示账户名和推文数量）
5. 仔细阅读警告："此操作不可恢复！"
6. 点击"确认删除"
7. 所有推文被删除，显示删除数量，列表清空

## 技术细节

### 数据库操作

- 单条删除: `tweet.delete()`
- 批量删除: `Tweet.objects.filter(x_account=x_account).delete()`
- Django 的级联删除会自动处理相关的 AI 分析数据

### 前端状态管理

- 删除后立即从`tweets`状态中移除对应项
- 调用`loadTweets()`重新获取完整数据和统计信息
- 使用`message.success()`显示操作反馈

### API 设计

- RESTful 风格：使用 DELETE 方法
- 批量操作需要额外的`confirm`参数防止误操作
- 返回删除数量方便用户了解操作结果

## 测试建议

1. **单条删除测试**

   - 删除第一条推文
   - 删除中间的推文
   - 删除最后一条推文
   - 验证删除后列表正确更新

2. **批量删除测试**

   - 删除少量推文的账户（< 10 条）
   - 删除大量推文的账户（> 100 条）
   - 验证删除后统计数据正确

3. **权限测试**

   - 尝试删除其他用户的推文（应失败）
   - 登出状态下尝试删除（应返回 401）

4. **边界测试**
   - 删除不存在的推文 ID
   - 批量删除时不传 confirm 参数
   - 对空账户执行批量删除

## 已修改文件清单

### Backend

- ✅ `backend/x_monitor/views.py` - 添加删除 API
- ✅ `backend/x_monitor/urls.py` - 添加路由

### Frontend

- ✅ `frontend/src/services/api.js` - 添加 API 调用
- ✅ `frontend/src/components/TweetCard.js` - 添加删除按钮
- ✅ `frontend/src/pages/TweetsPage.js` - 添加批量删除和回调

## 部署状态

✅ Backend 已重启
✅ Frontend 已重新构建并重启
✅ 功能已上线，可以测试

访问 http://localhost:3000/tweets 开始使用删除功能！

## 注意事项

⚠️ **重要警告**：

- 删除操作不可恢复
- 批量删除会删除该账户的所有历史推文
- 建议在删除前确认是否需要导出数据
- 删除推文不会影响 X.com 上的原始推文，只删除本地数据库中的副本

## 未来改进建议

1. **软删除** - 添加 deleted_at 字段实现软删除
2. **回收站** - 删除后保留 30 天，可恢复
3. **选择性删除** - 添加多选框，批量删除选中的推文
4. **导出功能** - 删除前可导出为 CSV/JSON
5. **删除历史** - 记录删除操作历史
6. **撤销功能** - 删除后短时间内可撤销

---

功能开发完成时间：2025-11-07 00:34 JST
开发人员：GitHub Copilot
