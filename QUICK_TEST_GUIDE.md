# 快速测试指南

## 1. 启动应用

```powershell
# 确保在项目根目录
cd E:\workspace\project_013_autoscrapy\auto-ski-info-subscribe

# 启动所有服务
docker-compose -f docker-compose.dev.yml up -d

# 检查服务状态
docker-compose -f docker-compose.dev.yml ps
```

## 2. 访问应用

打开浏览器访问：

- 前端: http://localhost:3000
- 登录页: http://localhost:3000/login

## 3. 登录

使用以下凭据之一登录：

```
管理员: admin / admin@123
测试用户: testuser / test123
```

## 4. 测试推文页面

### 4.1 访问推文页面

登录后，点击左侧菜单的 "推文监控" 或直接访问：
http://localhost:3000/tweets

### 4.2 添加监控账户（如果还没有）

1. 进入 "账户管理" 页面
2. 点击 "添加账户"
3. 输入 Twitter/X 用户名（例如: `elonmusk`, `github`）
4. 点击确认

### 4.3 测试新功能

#### ✅ 账户选择

- 在下拉列表中选择不同的账户
- 确认推文列表随账户切换更新

#### ✅ 智能推荐开关

- 点击 "智能推荐" 开关
- 开启后应该只显示 AI 认为相关的推文
- 关闭后显示所有推文

#### ✅ 日期范围选择

- 点击日期选择器
- 选择开始和结束日期（例如: 最近 7 天）
- 确认只显示该日期范围内的推文
- 点击 "X" 清除日期范围限制

#### ✅ 手动刷新

- 点击 "刷新推文" 按钮
- 按钮应显示加载动画
- 等待几秒后推文列表更新

#### ✅ 统计信息

检查顶部三个统计卡片：

- **总推文数**: 该账户的所有推文数量
- **今日推文**: 今天发布的推文数量
- **AI 推荐**: 被 AI 标记为相关的推文数量

#### ✅ X 风格推文卡片

每条推文应该显示：

- X logo（蓝色）
- 用户头像
- 用户昵称和用户名
- 推文时间（刚刚/X 分钟前/X 小时前）
- 推文内容（hashtag 和 @mention 高亮）
- 图片网格（如果有）
- 互动数据（转发、点赞、回复）
- AI 推荐星标（如果 ai_relevant=true）
- AI 摘要卡片（如果有 ai_summary）
- "查看原推文" 链接

## 5. 检查数据库

```powershell
# 进入后端容器
docker exec -it auto-ski-info-subscribe-backend-1 bash

# 打开 Django shell
python manage.py shell

# 检查账户设置
from x_monitor.models import XAccount
accounts = XAccount.objects.all()
for acc in accounts:
    print(f"{acc.username}: AI={acc.ai_filter_enabled}, Dates={acc.fetch_from_date} to {acc.fetch_to_date}")

# 检查推文
from x_monitor.models import Tweet
tweets = Tweet.objects.filter(x_account__username='elonmusk')[:5]
for t in tweets:
    print(f"{t.posted_at}: {t.content[:50]}... AI_relevant={t.ai_relevant}")
```

## 6. 查看日志

```powershell
# 后端日志
docker logs auto-ski-info-subscribe-backend-1 --tail 50

# Celery Worker 日志
docker logs auto-ski-info-subscribe-celery-1 --tail 50

# Celery Beat 日志
docker logs auto-ski-info-subscribe-celery-beat-1 --tail 50

# 前端日志
docker logs auto-ski-info-subscribe-frontend-1 --tail 50
```

## 7. 测试 API（可选）

### 获取账户列表

```powershell
# 先获取 token
$token = "your-auth-token"

# 获取账户
curl -X GET http://localhost:8000/api/monitor/accounts/ `
  -H "Authorization: Token $token"
```

### 更新账户设置

```powershell
curl -X PATCH http://localhost:8000/api/monitor/accounts/1/ `
  -H "Authorization: Token $token" `
  -H "Content-Type: application/json" `
  -d '{
    "ai_filter_enabled": true,
    "fetch_from_date": "2025-01-01",
    "fetch_to_date": "2025-01-31"
  }'
```

### 手动触发爬虫

```powershell
curl -X POST http://localhost:8000/api/monitor/accounts/1/monitor/ `
  -H "Authorization: Token $token"
```

## 8. 常见问题排查

### 问题: 推文列表为空

**解决方案**:

1. 确认选择了账户
2. 点击 "刷新推文" 按钮
3. 检查日期范围是否过滤掉了所有推文
4. 尝试关闭 AI 推荐开关

### 问题: AI 推荐不工作

**解决方案**:

1. 确认后端 Celery 服务运行正常
2. 检查推文是否已进行 AI 分析
3. 查看后端日志确认 AI 服务状态

### 问题: 刷新按钮没反应

**解决方案**:

1. 检查网络控制台是否有错误
2. 确认 Celery Worker 运行正常
3. 查看后端日志确认 API 调用

### 问题: 图片不显示

**解决方案**:

1. 检查推文是否包含 media_urls
2. 确认图片 URL 有效
3. 检查 CORS 设置

## 9. 调试工具

### VS Code 调试

1. 打开 VS Code
2. 按 F5 或点击 "Run and Debug"
3. 选择 "Backend (debugpy)" 配置
4. 在代码中设置断点

### 浏览器开发者工具

1. 按 F12 打开开发者工具
2. 查看 Console 控制台错误
3. 查看 Network 网络请求
4. 查看 React DevTools 组件状态

## 10. 成功标准

确认以下所有项目：

- [ ] 成功登录系统
- [ ] 可以看到推文监控页面
- [ ] 统计卡片显示正确数据
- [ ] 可以选择不同账户
- [ ] AI 推荐开关工作正常
- [ ] 日期范围选择工作正常
- [ ] 刷新按钮触发爬虫任务
- [ ] TweetCard 正确显示推文
- [ ] 分页功能正常
- [ ] 无控制台错误

**如果以上所有项目都通过，说明前端集成测试成功！** ✅

---

需要帮助？查看详细文档：

- `FRONTEND_INTEGRATION_COMPLETE.md` - 完整集成文档
- `DOCKER_DEBUG.md` - Docker 调试指南
- `START_HERE.md` - 项目启动指南
