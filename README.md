# Auto Ski Info Subscribe

**X (Twitter) 推文监控系统** - 基于 Cookie 认证的自动抓取与 AI 分析

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)

## 📋 项目简介

自动化监控 X (Twitter) 特定账号的推文，通过 AI 进行内容分析和分类，支持通过 MCP (Model Context Protocol) 协议将数据暴露给其他服务使用。

### 🎯 核心特性

- **🔐 Cookie 认证** - 使用您自己的 X 账号 Cookie，无需申请官方 API
- **📡 自动监控** - 定时抓取指定账号的最新推文
- **🤖 AI 分析** - 集成 Google Gemini AI 进行情感分析、内容摘要和主题提取
- **🔌 MCP 协议** - 通过 MCP 协议暴露推文资源给其他服务
- **🎨 Web 界面** - React 前端提供账号管理和推文浏览
- **☁️ 云端部署** - 支持 Docker 和 Google Cloud Run 部署

## 🏗️ 技术栈

**前端**
- React 18 + Ant Design
- React Query + React Router

**后端**
- Django 4.2 + Django REST Framework
- Playwright (无头浏览器爬虫)
- Celery + Redis (定时任务)
- Google Gemini AI (内容分析)

**部署**
- Docker + Docker Compose
- Nginx (反向代理)
- Google Cloud Run (可选)

## 🚀 快速开始

### 前置要求

- Docker & Docker Compose
- X (Twitter) 账号 Cookie
- Google Gemini API Key (可选，用于 AI 分析)

### 1. 获取 X Cookie

登录 [X (Twitter)](https://twitter.com)，按 `F12` 打开开发者工具：

1. 进入 `Application` → `Cookies` → `https://twitter.com`
2. 复制以下 Cookie 值：
   - `auth_token` - 认证令牌（必需）
   - `ct0` - CSRF 令牌（必需）

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑 backend/.env，填入您的配置
```

**必需配置**:
```ini
# X Cookie 认证
X_COOKIE_AUTH_TOKEN=your_auth_token_value
X_COOKIE_CT0=your_ct0_value

# AI 服务（可选）
AI_API_KEY_GOOGLE=your_gemini_api_key

# Django 配置
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. 启动服务

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/auto-ski-info-subscribe.git
cd auto-ski-info-subscribe

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 4. 访问应用

- **前端界面**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/swagger/
- **管理后台**: http://localhost:8000/admin/
  - 默认用户: `admin`
  - 默认密码: `admin@123`

## 📖 使用说明

### 添加监控账号

1. 访问前端界面并登录
2. 进入"账号管理"页面
3. 点击"添加账号"，填写：
   - X 用户名（如 `@example` 填写 `example`）
   - 显示名称（可选）
   - 启用监控

### 查看推文

- 系统每 15 分钟自动抓取已启用账号的推文
- 在"推文列表"页面查看所有收集的数据
- 支持按账号、情感、时间筛选

### MCP 资源接口

推文数据通过 MCP 协议暴露：

```http
# 获取单条推文
GET /api/mcp/tweets/{tweet_id}

# 获取账号推文列表
GET /api/mcp/accounts/{account_id}/tweets/

# 搜索推文
GET /api/mcp/tweets/search/?q=关键词&sentiment=positive
```

## 🐳 开发调试

### Docker 容器调试

项目支持在 Docker 容器内进行实时调试：

```powershell
# 使用 PowerShell 脚本（Windows）
.\docker-dev.ps1

# 选择操作：
# 1 - 首次构建
# 2 - 启动服务
# 9 - 数据库迁移
```

### VS Code 调试

1. 按 `Ctrl+Shift+D` 打开调试面板
2. 选择 `🐳 Docker: Full Stack Debug`
3. 按 `F5` 开始调试

**调试配置**:
- `🐳 Docker: Full Stack Debug` - 前后端同时调试
- `Docker: Backend (Remote)` - 后端调试（端口 5678）
- `Docker: Frontend (Chrome)` - 前端调试

详见 [DOCKER_DEBUG.md](DOCKER_DEBUG.md) 获取完整指南。

## ☁️ 云端部署

### Google Cloud Run

```bash
# 安装 gcloud CLI 并认证
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 配置密钥
chmod +x setup-secrets.sh
./setup-secrets.sh YOUR_PROJECT_ID

# 部署应用
chmod +x deploy.sh
./deploy.sh YOUR_PROJECT_ID
```

**当前配置**（`cloudbuild.yaml`）：
- CPU: 1 核
- 内存: 512Mi
- 实例数: 0-10（自动扩缩容）
- 成本: 无流量时 $0/月

## 🔧 配置与定制

### 调整监控频率

编辑 `backend/auto_ski_info/celery.py`:

```python
app.conf.beat_schedule = {
    'monitor-x-accounts': {
        'task': 'x_monitor.tasks.monitor_all_active_accounts',
        'schedule': crontab(minute='*/15'),  # 修改为 */30 表示 30 分钟
    },
}
```

### 自定义 AI 提示词

编辑 `backend/ai_service/services.py` 中的 `GeminiService` 类方法。

## 🛠️ 故障排查

### Cookie 认证失败

- 检查 Cookie 是否过期（重新从浏览器获取）
- 确认 `.env` 中的值正确无误
- 查看日志：`docker-compose logs backend | grep -i auth`

### Celery 任务不执行

- 检查 Redis：`docker-compose ps redis`
- 查看 Worker 日志：`docker-compose logs celery`
- 手动测试：`docker-compose exec backend python manage.py shell`

### 无法抓取推文

- 确认目标账号为公开账号
- 检查用户名格式（不含 `@`）
- 查看 Playwright 日志：`docker-compose logs backend | grep playwright`

## 📚 相关文档

- **[DOCKER_DEBUG.md](DOCKER_DEBUG.md)** - Docker 容器调试指南
- **[LOCAL_SETUP.md](LOCAL_SETUP.md)** - 本地开发环境设置
- **[backend/MCP_INTEGRATION.md](backend/MCP_INTEGRATION.md)** - MCP 协议集成说明

## 🔐 安全与合规

### Cookie 安全

- ⚠️ **切勿公开** 您的 `auth_token` 和 `ct0` Cookie
- ✅ 使用 `.env` 文件存储，添加到 `.gitignore`
- ✅ 生产环境使用 Secret Manager
- ✅ 定期更新 Cookie（建议每月）

### 使用限制

- ⚠️ 遵守 X (Twitter) 服务条款
- ⚠️ 建议间隔 15-30 分钟，避免过于频繁
- ⚠️ 仅限个人学习和研究，不得商业使用
- ⚠️ 仅抓取公开信息，尊重隐私

## 🤝 贡献指南

欢迎贡献！请遵循以下流程：

1. Fork 本仓库
2. 创建分支: `git checkout -b feature/amazing-feature`
3. 提交代码: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

**代码规范**:
- Python: PEP 8
- JavaScript: ESLint + Prettier
- Commit: 语义化提交信息（`feat:`, `fix:`, `docs:`）

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

## ⚠️ 免责声明

**本项目仅供学习和技术研究使用。**

- 使用者需遵守 X (Twitter) 服务条款和相关法律法规
- 使用者自行承担使用本工具产生的一切法律责任
- 开发者不对账号封禁或其他后果负责
- 请勿将本工具用于任何违法或侵权行为

**使用本工具即表示您已阅读并同意上述免责声明。**

---

**Star ⭐ 本项目，如果对您有帮助！**
