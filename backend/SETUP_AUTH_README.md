# 🚀 一键自动登录 X.com 获取 Cookies

## 📦 安装依赖（首次运行）

```bash
# 安装Python包
pip install playwright beautifulsoup4 lxml

# 安装浏览器（Chromium）
playwright install chromium
```

## ▶️ 运行（3 步完成）

```bash
# 步骤1: 进入backend目录
cd backend

# 步骤2: 运行脚本
python standalone_auth.py

# 步骤3: 按提示输入
用户名（邮箱/手机/用户名）: your_email@example.com
密码: ********
是否显示浏览器窗口？[Y/n]: y
```

## ✨ 脚本会自动完成

1. ✅ 打开浏览器访问 X.com 登录页
2. ✅ 自动填写用户名
3. ✅ 自动点击"Next"按钮
4. ✅ 自动填写密码
5. ✅ 自动点击"Log in"按钮
6. ✅ 等待登录完成
7. ✅ 保存 cookies 到 `backend/data/x_cookies.json`

## 🎯 如果遇到验证

脚本会自动检测并暂停：

```
⚠️ X.com要求额外验证（电话/邮箱）
请在浏览器中完成验证:
1. 查看浏览器窗口
2. 输入验证信息
3. 完成后回到这里

按Enter继续...
```

只需在浏览器中完成验证，然后回到终端按 Enter 即可。

## ✅ 成功示例

```bash
============================================================
X.com 自动登录
============================================================

用户名: myemail@example.com
密码: ********
模式: 显示浏览器

正在启动浏览器...
正在访问X.com登录页面...
页面加载完成，等待3秒...

等待用户名输入框...
✓ 找到用户名输入框
输入用户名: myemail@example.com
查找并点击'Next'按钮...
✓ 找到Next按钮（通过文本）
等待3秒...

等待密码输入框...
✓ 找到密码输入框
输入密码...
查找并点击'Log in'按钮...
✓ 找到Log in按钮（通过文本）

等待登录完成（8秒）...
当前URL: https://x.com/home

验证登录状态...
最终URL: https://x.com/home

保存cookies...

✓ Cookies已保存到: E:\...\backend\data\x_cookies.json
  共 23 个cookies

✓ 登录成功！

============================================================
✓ 认证设置完成！
============================================================

cookies已保存到: backend/data/x_cookies.json

下一步：
1. 在docker-compose.yml中设置环境变量：
   USE_AUTHENTICATED_SCRAPER: 'True'
2. 重启服务：
   docker-compose restart
3. 测试效果：
   docker-compose exec backend python test_authenticated_scraper.py
```

## 🔧 启用认证爬虫

编辑 `docker-compose.yml`，在所有服务的 environment 中添加：

```yaml
services:
  backend:
    environment:
      USE_AUTHENTICATED_SCRAPER: "True" # 添加这行
      # ... 其他配置

  celery:
    environment:
      USE_AUTHENTICATED_SCRAPER: "True" # 添加这行

  celery-beat:
    environment:
      USE_AUTHENTICATED_SCRAPER: "True" # 添加这行
```

重启服务：

```bash
docker-compose restart
```

## ✅ 测试效果

```bash
docker-compose exec backend python test_authenticated_scraper.py
```

预期看到：

```
============================================================
结果: 获取到 25 条推文
============================================================

✓ 成功！找到 3 条今天的推文
```

## ❓ 常见问题

### Q: 提示"ModuleNotFoundError: No module named 'playwright'"

A: 运行 `pip install playwright beautifulsoup4 lxml`

### Q: 提示"Executable doesn't exist"

A: 运行 `playwright install chromium`

### Q: 登录失败

A: 检查：

1. 用户名和密码是否正确
2. 网络是否正常
3. 查看 `backend/data/` 目录下的截图
4. 尝试显示浏览器（选择 Y）查看具体问题

### Q: 需要两步验证怎么办

A: 脚本会暂停让你完成：

1. 在浏览器窗口输入验证码
2. 完成验证
3. 回到终端按 Enter

## 🔒 安全提示

- ✅ 建议使用专门的爬虫账号
- ⚠️ cookies 文件包含登录凭证，不要分享
- 🔐 已加入.gitignore，不会提交到 Git

## 📊 效果对比

| 项目             | 登录前 | 登录后    |
| ---------------- | ------ | --------- |
| 可见推文         | 4-6 条 | 20-100+条 |
| 最新推文         | ❌     | ✅        |
| "最新 10 条"按钮 | 返回 0 | ✅ 正常   |

## 🎉 完成！

现在你可以在前端点击"最新 10 条"按钮，应该能看到获取到新推文了！
