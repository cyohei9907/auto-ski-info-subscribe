# Cookie 上传功能完整修复方案

## 问题总结

用户上传 X.com cookies 后，点击"取得最新 10 条"仍返回 0 条推文，遇到以下错误：

### 错误 1: sameSite 字段格式不兼容

```
ERROR: BrowserContext.add_cookies: cookies[0].sameSite: expected one of (Strict|Lax|None)
```

**原因**：Cookie-Editor 导出的 cookies 包含 `"sameSite": "no_restriction"` 值，但 Playwright 只接受 `Strict`、`Lax` 或 `None`。

### 错误 2: Playwright 超时

```
ERROR: Page.goto: Timeout 60000ms exceeded
```

**原因**：使用`wait_until='networkidle'`策略在 Docker 环境中不稳定，60 秒超时不够。

### 错误 3: 环境变量未设置

系统仍在使用 guest 模式 scraper，未启用 authenticated scraper。

## 完整解决方案

### 1. 修复 views.py - 转换 cookies 格式

**文件**：`backend/x_monitor/views.py`

在保存 cookies 前，将 Cookie-Editor 格式转换为 Playwright 兼容格式：

```python
# 转换cookies格式以兼容Playwright
playwright_cookies = []
for cookie in cookies:
    new_cookie = cookie.copy()

    # 转换sameSite字段
    if 'sameSite' in new_cookie:
        same_site = new_cookie['sameSite']
        if same_site in ['no_restriction', 'unspecified']:
            new_cookie['sameSite'] = 'None'
        elif same_site not in ['Strict', 'Lax', 'None']:
            new_cookie['sameSite'] = 'None'
    else:
        new_cookie['sameSite'] = 'Lax'

    # 确保secure字段存在（sameSite=None时必须为True）
    if new_cookie.get('sameSite') == 'None' and not new_cookie.get('secure'):
        new_cookie['secure'] = True

    playwright_cookies.append(new_cookie)

# 保存转换后的cookies
with open(cookies_file, 'w') as f:
    json.dump(playwright_cookies, f, indent=2)
```

### 2. 修复 existing cookies 文件

**一次性修复脚本**（在容器内执行）：

```python
import json
from pathlib import Path

cookies_file = Path('/app/data/x_cookies.json')
with open(cookies_file, 'r') as f:
    cookies = json.load(f)

# 修复sameSite字段
for cookie in cookies:
    if 'sameSite' in cookie:
        same_site = cookie['sameSite']
        if same_site == 'no_restriction':
            cookie['sameSite'] = 'None'
        elif same_site is None or same_site == 'null':
            cookie['sameSite'] = 'Lax'
        elif same_site == 'lax':
            cookie['sameSite'] = 'Lax'
    else:
        cookie['sameSite'] = 'Lax'

    if cookie.get('sameSite') == 'None' and not cookie.get('secure'):
        cookie['secure'] = True

with open(cookies_file, 'w') as f:
    json.dump(cookies, f, indent=2)

print(f'Fixed {len(cookies)} cookies')
```

**执行方式**：

```powershell
@"
[上面的Python代码]
"@ | docker-compose exec -T backend python
```

### 3. 修复 authenticated_scraper.py - 提高可靠性

**文件**：`backend/x_monitor/authenticated_scraper.py`

```python
# 修改前（不稳定）
page.goto(url, wait_until='networkidle', timeout=60000)

# 修改后（更可靠）
page.goto(url, wait_until='domcontentloaded', timeout=90000)
logger.info("Page loaded, waiting for tweets...")

page.wait_for_selector('article[data-testid="tweet"]', timeout=45000)
logger.info("Tweets detected, waiting for dynamic content...")
page.wait_for_timeout(3000)

# 添加超时容错
except PlaywrightTimeoutError as e:
    logger.error(f"Timeout waiting for page: {e}")
    logger.info("Trying to continue with current page state...")
    page.wait_for_timeout(2000)
    # 不立即返回，尝试继续处理
```

**改进点**：

- ✅ `networkidle` → `domcontentloaded`（更快，更可靠）
- ✅ 超时时间：60 秒 → 90 秒
- ✅ 添加 tweet selector 等待（45 秒）
- ✅ 超时后不立即失败，尝试继续

### 4. docker-compose.yml - 启用 authenticated scraper

**文件**：`docker-compose.yml`

```yaml
backend:
  environment:
    USE_AUTHENTICATED_SCRAPER: "True" # ✅ 新增
  command: >
    gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 600 auto_ski_info.wsgi:application
    # timeout 从 300 → 600秒

celery:
  environment:
    USE_AUTHENTICATED_SCRAPER: "True" # ✅ 新增

celery-beat:
  environment:
    USE_AUTHENTICATED_SCRAPER: "True" # ✅ 新增
```

## 应用所有修复

### 步骤 1: 停止所有服务

```bash
docker-compose down
```

### 步骤 2: 启动所有服务

```bash
docker-compose up -d
```

### 步骤 3: 修复现有 cookies 文件

```powershell
# 执行上面的Python修复脚本
@"
import json
from pathlib import Path
# [完整代码见上]
"@ | docker-compose exec -T backend python
```

### 步骤 4: 验证配置

```bash
# 检查环境变量
docker-compose exec backend env | grep USE_AUTHENTICATED_SCRAPER
# 应输出: USE_AUTHENTICATED_SCRAPER=True

# 检查日志
docker-compose logs backend | grep "authenticated scraper"
# 应包含: "Using authenticated X.com scraper (requires cookies, can access full timeline)"

# 检查cookies文件
docker-compose exec backend cat /app/data/x_cookies.json | grep sameSite
# 所有值应为 "Lax" 或 "None"，不应有 "no_restriction"
```

## 测试流程

### 方式 1: 使用现有 cookies（已修复）

1. 访问 http://localhost:3000/accounts
2. 点击任意账户的"取得最新 10 条"按钮
3. 等待 2-3 分钟（包括 15-30 秒随机延迟 + 页面加载）
4. **预期**：成功获取 10 条推文

### 方式 2: 重新上传 cookies

1. 在浏览器登录 X.com（Google 账号）
2. 使用 Cookie-Editor 导出 cookies
3. 访问 http://localhost:3000/settings
4. 切换到"上传 Cookies"标签页
5. 粘贴 JSON 并上传
6. **现在会自动转换格式**
7. 返回账户页面测试

## 注意事项

### Playwright 在 Docker 中的超时问题

Docker 环境网络延迟较高，建议：

- ✅ 使用 `domcontentloaded` 而非 `networkidle`
- ✅ 超时设置 90 秒+
- ✅ 在 selector 等待失败时有降级策略

### Cookies 有效期

- X.com cookies 通常有效期 **30-90 天**
- 如果长时间未使用，可能需要重新登录
- 定期检查是否返回 0 条推文（可能是 cookies 过期）

### Rate Limiting

- 代码已实现 **15-30 秒随机延迟**
- 避免频繁点击"取得最新 10 条"
- 定时任务已考虑延迟

## 故障排查

### 如果仍然获取 0 条推文

1. **检查 cookies 是否有效**

```bash
docker-compose exec backend cat /app/data/x_cookies.json | grep auth_token
```

应该看到 `auth_token` cookie 存在且有长 value。

2. **检查日志详细错误**

```bash
docker-compose logs backend -f
```

查看是否有 Playwright 错误或网络错误。

3. **手动测试 cookies**
   在浏览器开发者工具中，手动添加导出的 cookies 并访问 https://x.com，看是否能以登录状态访问。

4. **检查 X.com 账户状态**
   如果 X 账户被限制或锁定，即使 cookies 有效也无法获取数据。

5. **Docker 网络问题**

```bash
# 测试容器能否访问x.com
docker-compose exec backend curl -I https://x.com
```

## 相关文件清单

- ✅ `backend/x_monitor/views.py` - Cookie 上传 API（格式转换）
- ✅ `backend/x_monitor/authenticated_scraper.py` - 认证爬虫（超时优化）
- ✅ `backend/x_monitor/services.py` - Scraper 选择逻辑
- ✅ `docker-compose.yml` - 环境变量配置
- ✅ `backend/data/x_cookies.json` - Cookies 存储（已修复）
- ✅ `frontend/src/pages/SettingsPage.js` - Cookie 上传界面
- ✅ `frontend/src/services/api.js` - API 调用

## 修复完成时间

2025-11-07 00:24 JST

## 状态

🟢 **所有问题已修复，可以测试**

## 下一步

请访问 http://localhost:3000/accounts 测试"取得最新 10 条"功能！
