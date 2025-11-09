# X.com 登录爬虫使用指南

## 概述

使用您的 X.com 账号登录进行爬虫，可以访问完整的时间线和最新推文，不再受限于游客模式的 4-6 条置顶推文。

## 优势

- ✅ 访问完整时间线（不只是置顶推文）
- ✅ 获取最新推文（包括今天的推文）
- ✅ 更稳定可靠（不会被反爬虫机制限制）
- ✅ 支持滚动加载更多推文
- ✅ 一次登录，长期使用（cookies 自动保存和重用）

## 设置步骤

### 步骤 1：运行认证设置命令

在 Docker 容器中运行：

```bash
docker-compose exec backend python manage.py setup_x_auth
```

或者如果 Docker 环境没有图形界面，可以在本地运行（需要先安装依赖）：

```bash
cd backend
python manage.py setup_x_auth
```

### 步骤 2：手动登录

1. 浏览器窗口会自动打开，显示 X.com 登录页面
2. 使用您的 X.com 账号和密码登录
3. 如果有两步验证，完成验证流程
4. 登录成功后，等待页面完全加载（约 5-10 秒）
5. 回到终端，按 **Enter** 键

### 步骤 3：验证

命令会自动：

- 保存您的登录 cookies 到 `backend/data/x_cookies.json`
- 验证登录状态
- 显示成功消息

输出示例：

```
✓ Cookies已保存到: /app/data/x_cookies.json
  共 23 个cookies
✓ 登录验证成功！
```

### 步骤 4：启用认证爬虫

编辑 `docker-compose.yml`，在 backend、celery 和 celery-beat 的 environment 中添加：

```yaml
environment:
  USE_AUTHENTICATED_SCRAPER: "True"
  # ... 其他环境变量
```

### 步骤 5：重启服务

```bash
docker-compose restart
```

## 验证效果

运行测试脚本查看效果：

```bash
docker-compose exec backend python -c "
from x_monitor.services import XMonitorService
service = XMonitorService()
from x_monitor.models import XAccount
account = XAccount.objects.first()
if account:
    result = service.monitor_account(account, max_tweets=10)
    print(f'获取到 {result[\"new_tweets\"]} 条新推文')
"
```

或者在前端点击 **「最新 10 条」** 按钮测试。

## 文件说明

### 生成的文件

- **backend/data/x_cookies.json**: 保存的登录 cookies
  - 包含认证令牌和会话信息
  - cookies 通常有效期为 30-90 天
  - 不要提交到 Git（已在.gitignore 中）

### 相关代码文件

- **backend/x_monitor/authenticated_scraper.py**: 认证爬虫实现
- **backend/x_monitor/management/commands/setup_x_auth.py**: 认证设置命令
- **backend/x_monitor/services.py**: 爬虫服务（自动选择认证或游客模式）

## 常见问题

### Q: Cookies 多久失效？

A: 通常 30-90 天。失效后重新运行 `setup_x_auth` 即可。

### Q: Docker 环境没有图形界面怎么办？

A: 两个方案：

1. 在本地 Windows/Mac 运行 `python manage.py setup_x_auth`，然后复制 `backend/data/x_cookies.json` 到 Docker volume
2. 使用 `--headless` 参数（需要配置 X11 转发）

### Q: 登录后报错怎么办？

A: 检查：

1. X.com 是否正常访问
2. 账号是否被锁定或需要验证
3. 浏览器 cookies 是否正确保存
4. 重新运行 `setup_x_auth`

### Q: 如何确认正在使用认证爬虫？

A: 查看日志：

```bash
docker-compose logs backend | grep "authenticated scraper"
```

应该看到：

```
Using authenticated X.com scraper (requires cookies, can access full timeline)
XMonitorService initialized with authenticated scraper
```

### Q: 可以切换回游客模式吗？

A: 可以，在 `docker-compose.yml` 中设置：

```yaml
USE_AUTHENTICATED_SCRAPER: "False"
```

然后重启服务。

### Q: Cookies 文件会被提交到 Git 吗？

A: 不会，`x_cookies.json` 已加入 `.gitignore`，不用担心泄露。

### Q: 需要多个账号怎么办？

A: 当前版本仅支持单一账号。如需多账号，可以：

1. 为不同环境使用不同 cookies 文件
2. 手动切换 cookies 文件内容

## 安全建议

1. ✅ **不要分享 cookies 文件** - 包含您的登录凭证
2. ✅ **定期更新 cookies** - 重新运行 setup_x_auth 保持新鲜
3. ✅ **使用专用账号** - 建议使用专门的爬虫账号，而非主账号
4. ✅ **监控账号状态** - 检查是否有异常登录通知
5. ✅ **备份 cookies** - 保存一份副本以防文件丢失

## 性能对比

| 模式         | 可见推文数 | 时间线完整性 | 最新推文    | 稳定性      |
| ------------ | ---------- | ------------ | ----------- | ----------- |
| **游客模式** | 4-6 条     | ❌ 仅置顶    | ❌ 无法获取 | ⚠️ 易被限制 |
| **认证模式** | 20-100 条  | ✅ 完整      | ✅ 实时获取 | ✅ 稳定可靠 |

## 下一步

设置完成后，可以：

1. 测试「最新 10 条」按钮
2. 检查数据库中的推文时间戳
3. 验证 6 小时内的推文是否正确获取
4. 配置定时任务自动监控

## 技术细节

### Cookie 存储格式

```json
[
  {
    "name": "auth_token",
    "value": "...",
    "domain": ".x.com",
    "path": "/",
    "expires": 1234567890.123,
    "httpOnly": true,
    "secure": true,
    "sameSite": "None"
  },
  ...
]
```

### 认证流程

1. 加载保存的 cookies → `context.add_cookies(cookies)`
2. 访问 `https://x.com/{username}` → 已登录状态
3. 滚动加载完整时间线 → 获取所有可见推文
4. 解析推文数据 → 保存到数据库

### 与游客模式的区别

| 功能     | 游客模式               | 认证模式               |
| -------- | ---------------------- | ---------------------- |
| URL      | `https://x.com/{user}` | `https://x.com/{user}` |
| Cookies  | 无                     | 有（auth_token 等）    |
| 页面行为 | 显示置顶推文           | 显示完整时间线         |
| 滚动加载 | 不工作                 | 正常工作               |
| 推文数量 | 4-6 条                 | 20-100+条              |

## 故障排除

### 日志分析

```bash
# 查看爬虫初始化日志
docker-compose logs backend | grep "scraper"

# 查看获取推文日志
docker-compose logs backend | grep "Fetching.*tweets"

# 查看错误日志
docker-compose logs backend | grep "ERROR"
```

### 重新设置认证

如果遇到问题，可以完全重置：

```bash
# 1. 删除旧cookies
docker-compose exec backend rm -f /app/data/x_cookies.json

# 2. 重新运行设置
docker-compose exec backend python manage.py setup_x_auth

# 3. 重启服务
docker-compose restart
```

## 支持

如有问题，请检查：

1. 日志文件：`docker-compose logs backend`
2. Cookies 文件：`backend/data/x_cookies.json` 是否存在
3. 环境变量：`USE_AUTHENTICATED_SCRAPER` 是否设置为 `"True"`
