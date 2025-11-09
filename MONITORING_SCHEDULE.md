# 监控计划安排功能

## 功能概述

现在每个 Twitter 账户都可以设置独立的监控间隔，系统会根据各账户的设置自动进行定时监控。

## 监控间隔选项

- **每 30 分钟** - 适合需要实时跟踪的重要账户
- **每 1 小时** - 适合活跃度较高的账户
- **每 4 小时** - 默认选项，适合一般账户（推荐）
- **每 12 小时** - 适合更新频率较低的账户

## 工作原理

### 1. 后端智能调度

系统每 30 分钟运行一次 `monitor_all_active_accounts` 任务，但不会盲目监控所有账户：

```python
# 检查逻辑
if account.last_checked is None:
    # 从未监控过，立即监控
    should_monitor = True
else:
    # 计算距离上次检查的时间（分钟）
    time_since_last_check = (now - account.last_checked).total_seconds() / 60

    # 如果超过了监控间隔，则监控
    if time_since_last_check >= account.monitoring_interval:
        should_monitor = True
```

**示例**：

- 账户 A 设置为"每 30 分钟" → 系统每 30 分钟检查一次
- 账户 B 设置为"每 4 小时" → 系统每 4 小时检查一次
- 账户 C 设置为"每 12 小时" → 系统每 12 小时检查一次

### 2. Celery Beat 配置

```python
CELERY_BEAT_SCHEDULE = {
    'monitor-all-accounts-every-30-minutes': {
        'task': 'x_monitor.tasks.monitor_all_active_accounts',
        'schedule': 1800.0,  # 30分ごと（最短间隔检查）
    },
}
```

**注意**：Beat 任务每 30 分钟运行一次，但实际监控由各账户的 `monitoring_interval` 控制。

### 3. 数据库模型

```python
class XAccount(models.Model):
    INTERVAL_CHOICES = [
        (30, '每30分钟'),
        (60, '每1小时'),
        (240, '每4小时'),
        (720, '每12小时'),
    ]

    monitoring_interval = models.IntegerField(
        choices=INTERVAL_CHOICES,
        default=240,
        help_text="监控间隔（分钟）"
    )
```

## 前端使用

### 在账户列表中修改监控间隔

1. 进入"アカウント管理"页面
2. 在"監視間隔"列中，使用下拉菜单选择间隔
3. 选择后会自动保存并生效

### 显示效果

表格列显示：

- **監視間隔**：下拉选择器，可直接修改
- **ステータス**：显示监视状态和最后检查时间

## API 接口

### 获取账户列表

```http
GET /api/v1/monitor/accounts/
```

响应包含 `monitoring_interval` 和 `monitoring_interval_display` 字段：

```json
{
  "data": [
    {
      "id": 1,
      "username": "skiinfomation",
      "monitoring_interval": 240,
      "monitoring_interval_display": "每4小时",
      "is_active": true,
      "last_checked": "2025-11-09T12:30:00Z"
    }
  ]
}
```

### 更新监控间隔

```http
PATCH /api/v1/monitor/accounts/{id}/
Content-Type: application/json

{
  "monitoring_interval": 60
}
```

## 最佳实践

### 选择合适的监控间隔

1. **每 30 分钟**：

   - 优点：最及时，几乎实时
   - 缺点：资源消耗较大，可能触发限流
   - 适用：新闻类、突发事件相关的重要账户

2. **每 1 小时**：

   - 优点：较为及时，资源消耗适中
   - 缺点：可能错过短时间内的更新
   - 适用：活跃账户、商业账户

3. **每 4 小时**（推荐默认）：

   - 优点：平衡性能和及时性
   - 缺点：延迟较高
   - 适用：大多数普通账户

4. **每 12 小时**：
   - 优点：资源消耗最小
   - 缺点：延迟最高
   - 适用：更新频率很低的账户

### 资源优化建议

- 不要将所有账户都设为"每 30 分钟"，会造成不必要的资源浪费
- 根据账户的实际更新频率选择合适的间隔
- 对于不活跃的账户，建议使用"每 12 小时"或直接停止监控

## 监控日志

系统会在监控日志中记录监控间隔信息：

```python
logger.info(f"Monitored @{account.username} (间隔: {account.get_monitoring_interval_display()}): {result}")
```

日志示例：

```
Monitored @skiinfomation (间隔: 每4小时): {'success': True, 'new_tweets': 3}
```

## 故障排除

### 账户没有按设定间隔监控

1. 检查账户是否处于激活状态（`is_active=True`）
2. 确认 Celery Beat 服务是否正常运行：
   ```bash
   celery -A auto_ski_info beat -l info
   ```
3. 查看 Celery Worker 日志确认任务执行情况

### 修改间隔后未生效

1. 前端修改会立即更新数据库
2. 但需要等待下一次 Beat 任务运行（最多 30 分钟）
3. 也可以手动触发"今すぐ監視"按钮立即执行

## 技术细节

### 数据库迁移

```bash
# 生成迁移文件
python manage.py makemigrations x_monitor

# 应用迁移
python manage.py migrate
```

迁移文件：`x_monitor/migrations/0005_xaccount_monitoring_interval.py`

### 缓存更新策略

前端使用 React Query 的 `setQueryData` 更新缓存，无需重新获取整个列表：

```javascript
queryClient.setQueryData("accounts", (oldData) => ({
  ...oldData,
  data: oldData.data.map((account) =>
    account.id === id ? { ...account, ...data } : account
  ),
}));
```

## 未来改进

可以考虑添加以下功能：

1. **自定义间隔**：允许用户输入任意分钟数
2. **智能调度**：根据账户活跃度自动调整间隔
3. **时段设置**：在特定时间段使用不同的监控间隔
4. **监控暂停**：允许临时暂停特定时段的监控
