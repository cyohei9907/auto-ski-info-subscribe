# Cookie 上传功能故障修复说明

## 问题描述

用户上传了 X.com cookies 后，点击"取得最新 10 条"按钮仍然返回 0 条推文。

## 根本原因

虽然 cookies 已成功上传到 `/app/data/x_cookies.json`，但系统仍在使用**guest 模式**的 scraper，因为关键的环境变量 `USE_AUTHENTICATED_SCRAPER` 没有在 `docker-compose.yml` 中设置。

## 解决方案

### 修改内容

在 `docker-compose.yml` 中为以下 3 个服务添加环境变量：

1. **backend 服务**
2. **celery 服务**
3. **celery-beat 服务**

添加的环境变量：

```yaml
USE_AUTHENTICATED_SCRAPER: "True"
```

同时将 Gunicorn timeout 从 300 秒 增加到 600 秒，以支持长时间的 Playwright 操作。

### 修改后的配置

#### Backend 服务

```yaml
backend:
  environment:
    USE_CLOUD_SQL: "False"
    DEBUG: "True"
    SECRET_KEY: "django-insecure-local-dev-key"
    ALLOWED_HOSTS: "localhost,127.0.0.1,backend"
    REDIS_URL: "redis://redis:6379/0"
    USE_AUTHENTICATED_SCRAPER: "True" # ✅ 新增
    GEMINI_API_KEY: ${GEMINI_API_KEY:-}
  command: >
    sh -c "mkdir -p /app/data &&
           python manage.py migrate &&
           python manage.py collectstatic --noinput &&
           gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 600 auto_ski_info.wsgi:application"
    # timeout 改为 600 ✅
```

#### Celery 服务

```yaml
celery:
  environment:
    USE_CLOUD_SQL: "False"
    DEBUG: "True"
    REDIS_URL: "redis://redis:6379/0"
    USE_AUTHENTICATED_SCRAPER: "True" # ✅ 新增
    GEMINI_API_KEY: ${GEMINI_API_KEY:-}
```

#### Celery-beat 服务

```yaml
celery-beat:
  environment:
    USE_CLOUD_SQL: "False"
    DEBUG: "True"
    REDIS_URL: "redis://redis:6379/0"
    USE_AUTHENTICATED_SCRAPER: "True" # ✅ 新增
    GEMINI_API_KEY: ${GEMINI_API_KEY:-}
```

## 工作原理

### 代码逻辑（services.py）

```python
# 根据配置选择爬虫实现
USE_AUTHENTICATED = getattr(settings, 'USE_AUTHENTICATED_SCRAPER', False)
if USE_AUTHENTICATED:
    logger.info("Using authenticated X.com scraper (requires cookies, can access full timeline)")
    from .authenticated_scraper import AuthenticatedXScraperClient
    SCRAPER_AVAILABLE = True
else:
    logger.info("Using guest X.com scraper (limited to visible tweets)")
    SCRAPER_AVAILABLE = False

class XMonitorService:
    def __init__(self):
        if USE_AUTHENTICATED and SCRAPER_AVAILABLE:
            self.scraper_client = AuthenticatedXScraperClient()  # ✅ 使用认证爬虫
        else:
            self.scraper_client = XScraperClient()  # ❌ guest模式（只能看到4-6条固定推文）
```

### AuthenticatedXScraperClient 行为

1. 从 `/app/data/x_cookies.json` 加载 cookies
2. 创建 Playwright 浏览器上下文
3. 将 cookies 添加到浏览器
4. 访问 `https://x.com/@username` 时会携带认证信息
5. 可以访问完整的用户时间线（不受 guest 模式限制）

## 应用修改

```bash
# 1. 停止所有容器
docker-compose down

# 2. 启动所有容器（会读取新的环境变量）
docker-compose up -d

# 3. 验证配置生效
docker-compose exec backend env | grep USE_AUTHENTICATED_SCRAPER
# 输出应为: USE_AUTHENTICATED_SCRAPER=True

# 4. 检查日志确认使用authenticated scraper
docker-compose logs backend | grep "authenticated scraper"
# 输出应包含: "Using authenticated X.com scraper (requires cookies, can access full timeline)"
```

## 验证结果

### ✅ 环境变量已设置

```bash
$ docker-compose exec backend env | grep USE_AUTHENTICATED_SCRAPER
USE_AUTHENTICATED_SCRAPER=True
```

### ✅ Backend 日志显示使用 authenticated scraper

```
INFO 2025-11-07 00:12:43,102 services 8 140174134729600 Using authenticated X.com scraper (requires cookies, can access full timeline)
```

### ✅ Cookies 文件存在

```bash
$ docker-compose exec backend ls -lh /app/data/x_cookies.json
-rw-r--r-- 1 root root 3.0K Nov 6 15:09 /app/data/x_cookies.json
```

## 测试步骤

1. 访问 http://localhost:3000/accounts
2. 选择要监控的账户（如 @skiinfomation）
3. 点击"取得最新 10 条"按钮
4. **预期结果**：应该能获取到 10 条（或更多）最新推文
5. 如果还是 0 条，检查：
   - Cookies 是否有效（可能已过期）
   - 检查 backend 日志查看详细错误信息：`docker-compose logs backend -f`

## 注意事项

1. **Cookies 有效期**：X.com 的 cookies 通常有效期为 30-90 天，过期后需要重新上传
2. **Playwright 超时**：authenticated_scraper.py 中设置了 90 秒超时，如果网络慢可能需要调整
3. **账户状态**：如果 X.com 账户被限制或锁定，即使有 cookies 也无法获取数据
4. **Rate Limiting**：频繁请求可能触发 X.com 的限流，建议在每次请求间添加 15-30 秒延迟（代码中已实现）

## 相关文件

- `docker-compose.yml` - 环境变量配置
- `backend/x_monitor/services.py` - Scraper 选择逻辑
- `backend/x_monitor/authenticated_scraper.py` - 认证爬虫实现
- `backend/data/x_cookies.json` - 保存的 cookies（由用户上传或自动登录生成）
- `frontend/src/pages/SettingsPage.js` - Cookie 上传界面

## 修复完成时间

2025-11-07 00:13 JST

## 修复人员

GitHub Copilot
