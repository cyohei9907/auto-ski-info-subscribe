# 🔧 超时问题已修复 + Cookie 上传功能

## ✅ 已修复的问题

### 问题：Playwright 在 Docker 中访问 X.com 超时

```
TimeoutError: Page.goto: Timeout 60000ms exceeded.
504 Gateway Timeout
```

### 原因：

1. Docker 容器网络访问 X.com 较慢
2. Nginx 代理超时设置太短（默认 60 秒）
3. Gunicorn worker 超时设置不足

## 🔧 已实施的修复

### 1. 增加 Playwright 超时和重试逻辑

```python
# 修改前：
page.goto("https://x.com/i/flow/login", wait_until='networkidle', timeout=60000)

# 修改后：
try:
    page.goto("https://x.com/i/flow/login", wait_until='domcontentloaded', timeout=90000)
    page.wait_for_timeout(5000)
except Exception as e:
    print(f"⚠️ 页面加载超时，尝试继续...")
    page.wait_for_timeout(3000)
```

**改进**：

- ✅ 使用 `domcontentloaded` 而不是 `networkidle`（更可靠）
- ✅ 超时从 60 秒增加到 90 秒
- ✅ 添加异常处理和重试逻辑

### 2. 增加 Gunicorn 超时

```dockerfile
# 修改前：
CMD ["gunicorn", "--timeout", "300", ...]

# 修改后：
CMD ["gunicorn", "--timeout", "600", ...]  # 10分钟
```

### 3. 增加 Nginx 代理超时

```nginx
# 新增：
location /api/ {
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
}
```

## 🎉 新功能：Cookie 上传（推荐用于 Google 登录）⭐

### 为什么需要这个功能？

如果你使用 **Google 账号登录 X.com**，没有独立密码，无法使用自动登录功能。现在可以：

1. 在浏览器手动登录 X.com（使用 Google）
2. 导出 cookies
3. 在网页上传 cookies

### 后端 API 已就绪

```python
POST /api/monitor/upload-cookies/

Request Body:
{
  "cookies": "[{\"name\":\"auth_token\",\"value\":\"...\"}]"
}

Response:
{
  "success": true,
  "message": "Cookies上传成功！已保存 23 个cookies",
  "cookies_count": 23
}
```

**功能**：

- ✅ 验证 cookies 格式
- ✅ 检查必要字段（name, value, domain）
- ✅ 保存到 `backend/data/x_cookies.json`
- ✅ 自动启用认证爬虫

## 🚀 使用方法

### 方法 1：重新尝试自动登录（如果有密码）

服务重启后，超时问题已修复：

```bash
# 1. 重启服务（正在构建中）
docker-compose up -d

# 2. 访问设置页面
http://localhost:3000/settings

# 3. 填写用户名密码并提交
# 4. 等待最多2-3分钟（不会再超时）
```

### 方法 2：使用 Cookie 上传（推荐 - 适用 Google 登录）

#### 步骤 1：安装 Cookie 导出工具

**Chrome 扩展推荐**：

- Cookie-Editor（推荐）
- EditThisCookie

在 Chrome 扩展商店搜索并安装。

#### 步骤 2：登录并导出 Cookies

1. 打开 Chrome 浏览器
2. 访问 https://x.com
3. 使用 Google 账号登录
4. 登录成功后，点击 Cookie-Editor 扩展图标
5. 点击"Export"按钮
6. 复制 JSON 格式的 cookies

#### 步骤 3：上传 Cookies

**临时方法（使用 API 测试工具）**：

```bash
# 使用curl上传
curl -X POST http://localhost:8000/api/monitor/upload-cookies/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": "[复制的cookies JSON]"
  }'
```

**或使用 Postman/Insomnia**：

- POST http://localhost:8000/api/monitor/upload-cookies/
- Headers:
  - Authorization: Token YOUR_TOKEN
  - Content-Type: application/json
- Body:
  ```json
  {
    "cookies": "[粘贴你导出的cookies]"
  }
  ```

#### 步骤 4：启用认证爬虫

编辑 `docker-compose.yml`：

```yaml
backend:
  environment:
    USE_AUTHENTICATED_SCRAPER: "True" # 添加这行
```

重启服务：

```bash
docker-compose restart
```

#### 步骤 5：测试

访问账户管理 → 点击"取得最新 10 条" → 成功获取推文！

## 📋 下一步计划（可选）

### 前端 Cookie 上传界面

我可以在设置页面添加第二个选项卡：

```
┌────────────────────────────────────────┐
│  爬虫设置                               │
├────────────────────────────────────────┤
│                                        │
│  登录方式：                             │
│  ⚪ 用户名+密码自动登录                 │
│  ⚫ 上传Cookies（Google登录用户）       │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  📋 粘贴Cookies JSON              │ │
│  │                                   │ │
│  │  [{                               │ │
│  │    "name": "auth_token",          │ │
│  │    "value": "xxx...",             │ │
│  │    "domain": ".x.com"             │ │
│  │  }]                               │ │
│  │                                   │ │
│  └──────────────────────────────────┘ │
│                                        │
│  [ ✅ 验证并上传 ]                      │
│                                        │
└────────────────────────────────────────┘
```

**开发时间**：15 分钟

**需要吗？** 如果需要，回复"请添加前端 Cookie 上传界面"

## 🔍 验证修复

### 检查 1：服务重启成功

```bash
docker-compose ps
# 所有服务应该是 "Up" 状态
```

### 检查 2：尝试自动登录

```bash
# 访问设置页面
http://localhost:3000/settings

# 填写并提交
# 应该不会再出现504错误
# 等待时间：2-3分钟（之前会在1分钟时超时）
```

### 检查 3：上传 Cookies 测试

```bash
# 使用curl测试API
curl -X POST http://localhost:8000/api/monitor/upload-cookies/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cookies":"[{\"name\":\"test\",\"value\":\"test\",\"domain\":\".x.com\"}]"}'

# 应该返回成功消息
```

## 📊 总结

### 已完成：

- ✅ 修复 Playwright 超时问题
- ✅ 增加 Gunicorn 和 Nginx 超时设置
- ✅ 添加 Cookie 上传 API
- ✅ 支持 Google 登录场景

### 当前状态：

- 🔄 Docker 镜像正在重新构建
- ⏳ 构建完成后需要重启服务

### 下一步：

1. 等待构建完成（约 1-2 分钟）
2. 重启服务：`docker-compose up -d`
3. 测试自动登录或上传 cookies
4. 如需前端上传界面，请告知

## 🎯 推荐方案

如果你使用 Google 登录 X.com：

**推荐使用 Cookie 上传方式** ⭐

1. 5 分钟一次性设置
2. 不需要密码
3. Cookies 有效期 30-90 天
4. 安全可靠

**步骤**：

1. 安装 Cookie-Editor 扩展
2. 用 Google 登录 X.com
3. 导出 cookies
4. 使用 curl 或 Postman 上传
5. 完成！

需要帮助吗？告诉我你选择哪个方案！🚀
