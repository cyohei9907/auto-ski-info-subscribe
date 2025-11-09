# X.com 自动登录爬虫 - 快速开始

## 🚀 3 分钟快速设置

### 方法 1: 直接运行脚本（推荐）

```bash
# 在Windows本地运行
cd backend
python local_setup_auth.py
```

**脚本会：**

1. ✅ 提示你输入 X.com 用户名和密码
2. ✅ 自动打开浏览器并登录
3. ✅ 自动保存 cookies 到 `backend/data/x_cookies.json`
4. ✅ 完成！

### 方法 2: 使用环境变量

```bash
# 1. 创建配置文件
cp .env.x.example .env.x

# 2. 编辑 .env.x，填写你的账号密码
X_USERNAME=your_email@example.com
X_PASSWORD=your_password

# 3. 加载环境变量并运行
# Windows PowerShell:
Get-Content .env.x | ForEach-Object { $var = $_.Split('='); [Environment]::SetEnvironmentVariable($var[0], $var[1]) }
cd backend
python local_setup_auth.py

# 或者直接在Docker中运行：
docker-compose exec -e X_USERNAME=your_email -e X_PASSWORD=your_pass backend python manage.py setup_x_auth
```

## 📝 示例输出

```
============================================================
Windows本地 - X.com自动登录认证
============================================================

这个脚本会：
1. 自动打开浏览器并登录X.com
2. 自动填写你的账号密码
3. 保存cookies到 backend/data/x_cookies.json
4. Docker会自动使用这个文件

============================================================

请输入你的X.com账号信息：
（密码不会显示，输入后按Enter）

用户名（邮箱/手机/用户名）: myemail@example.com
密码: ********

是否显示浏览器窗口？[Y/n]: y

开始登录...

============================================================
X.com 自动登录认证设置
============================================================

用户名: myemail@example.com
密码: ********
模式: 显示浏览器

正在访问X.com登录页面...
等待登录表单加载...
输入用户名: myemail@example.com
点击下一步...
等待密码输入框...
输入密码...
点击登录...

等待登录完成...
当前URL: https://x.com/home

验证登录状态...

保存cookies...

✓ Cookies已保存到: E:\workspace\...\backend\data\x_cookies.json
  共 23 个cookies

✓ 登录成功！

下一步：
1. 在docker-compose.yml中设置: USE_AUTHENTICATED_SCRAPER: 'True'
2. 重启服务: docker-compose restart
3. 测试: docker-compose exec backend python test_authenticated_scraper.py

============================================================
✓ 认证设置完成！
============================================================
```

## ⚙️ 启用认证爬虫

编辑 `docker-compose.yml`：

```yaml
services:
  backend:
    environment:
      USE_AUTHENTICATED_SCRAPER: "True" # 添加这行
      # ... 其他配置

  celery:
    environment:
      USE_AUTHENTICATED_SCRAPER: "True" # 添加这行
      # ... 其他配置

  celery-beat:
    environment:
      USE_AUTHENTICATED_SCRAPER: "True" # 添加这行
      # ... 其他配置
```

重启服务：

```bash
docker-compose restart
```

## ✅ 测试效果

```bash
# 测试认证爬虫
docker-compose exec backend python test_authenticated_scraper.py

# 预期输出：
# ============================================================
# 结果: 获取到 25 条推文
# ============================================================
#
# 最近的推文：
#
# 1. [2025-11-06 22:30:00+00:00] (ID: 1854321...)
#    今日の雪情報です...
#    💬 5 🔄 12 ❤️ 34
#
# ✓ 成功！找到 3 条今天的推文
```

## ❓ 常见问题

### Q: 需要两步验证怎么办？

A: 脚本会自动检测并提示：

```
⚠️ 需要两步验证
请在浏览器中完成验证，完成后按Enter...
```

在浏览器中输入验证码，然后回到终端按 Enter 即可。

### Q: 显示"未找到用户名输入框"？

A: X.com 有时会更改页面结构。如果遇到此问题：

1. 确保网络连接正常
2. 尝试显示浏览器窗口（选择 Y）以查看实际情况
3. 如果页面加载异常，等待几秒后重试

### Q: 登录失败？

**可能原因**：

- ❌ 用户名或密码错误
- ❌ 账号被锁定或需要验证
- ❌ X.com 检测到自动化行为
- ❌ 网络问题

**解决方案**：

1. 检查账号密码是否正确
2. 在浏览器中手动登录一次确认账号正常
3. 使用显示浏览器模式（选择 Y）查看具体错误
4. 如果遇到额外验证，脚本会暂停让你完成

### Q: "需要额外验证（电话/邮箱）"？

A: 这是 X.com 的安全机制，在新环境登录时触发：

```
⚠️ X.com要求额外验证（电话/邮箱）
这通常发生在新环境登录时

请在浏览器中完成验证，然后按Enter继续...
```

按照提示在浏览器中完成验证即可。

### Q: Cookies 多久过期？

A: 通常 30-90 天。过期后重新运行 `python backend/local_setup_auth.py` 即可。

## 🔒 安全提示

1. ⚠️ **不要提交包含密码的文件到 Git**

   - `.env.x` 已加入 `.gitignore`
   - `x_cookies.json` 已加入 `.gitignore`

2. ✅ **建议使用专用账号**

   - 创建一个专门用于爬虫的 X 账号
   - 不要使用主账号

3. 🔐 **保护 cookies 文件**
   - `backend/data/x_cookies.json` 包含登录凭证
   - 不要分享或上传此文件

## 📊 效果对比

| 项目             | 登录前      | 登录后      |
| ---------------- | ----------- | ----------- |
| 可见推文数       | 4-6 条      | 20-100+条   |
| 最新推文         | ❌ 无法获取 | ✅ 实时获取 |
| "最新 10 条"按钮 | 返回 0 条   | ✅ 正常工作 |
| 2025-11-06 推文  | ❌ 看不到   | ✅ 可以看到 |

## 🎯 下一步

1. ✅ 运行 `python backend/local_setup_auth.py` 完成登录
2. ✅ 修改 `docker-compose.yml` 启用认证爬虫
3. ✅ 重启服务并测试
4. ✅ 在前端点击"最新 10 条"按钮验证效果

## 🆘 需要帮助？

如果遇到问题，请提供：

1. 完整的错误输出
2. 是否显示了浏览器窗口
3. 浏览器中看到的页面内容
4. X.com 账号是否正常（能否手动登录）
