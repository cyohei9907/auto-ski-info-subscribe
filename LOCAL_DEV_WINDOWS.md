# 本地 Windows 开发环境指南

## 📋 概述

前端和后端现在运行在本地 Windows 环境中，而 Redis 和 Celery 继续在 Docker 容器中运行。

## 🔧 架构

```
┌─────────────────────────────────────┐
│     本地 Windows 环境                │
│  ┌──────────────────────────────┐  │
│  │  Frontend (React)            │  │
│  │  http://localhost:3000       │  │
│  └──────────────────────────────┘  │
│              ↓                      │
│  ┌──────────────────────────────┐  │
│  │  Backend (Django)            │  │
│  │  http://localhost:8000       │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│     Docker 容器                      │
│  ┌──────────────────────────────┐  │
│  │  Redis (localhost:6379)      │  │
│  │  Celery Worker               │  │
│  │  Celery Beat                 │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 🚀 启动步骤

### 1. 启动 Docker 服务（必须先执行）

```powershell
docker-compose up -d redis celery celery-beat
```

验证服务运行:

```powershell
docker ps
```

应该看到:

- `auto-ski-info-subscribe-redis-1` - Up
- `auto-ski-info-subscribe-celery-1` - Up
- `auto-ski-info-subscribe-celery-beat-1` - Up

### 2. 启动后端（Django）

**选项 A: 使用 VS Code 调试器（推荐）**

1. 打开 VS Code
2. 按 F5 或点击 Run and Debug
3. 选择 "Django: Backend Server"
4. 后端将启动在 http://localhost:8000

**选项 B: 使用终端**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
```

验证: 访问 http://localhost:8000/admin

### 3. 启动前端（React）

打开新终端窗口:

```powershell
cd frontend
npm start
```

浏览器将自动打开 http://localhost:3000

## 🐞 VS Code 调试配置

### 可用的调试配置

**launch.json** 包含以下配置:

1. **Django: Backend Server** - 启动 Django 开发服务器

   - 支持断点调试
   - 自动重载代码更改
   - 在集成终端中运行

2. **Celery Worker** - 调试 Celery 任务

   - 使用 `--pool=solo` 模式支持调试
   - 适合调试异步任务逻辑

3. **Celery Beat** - 调试定时任务

   - 用于调试定时任务触发逻辑

4. **Full Backend Stack** - 组合配置
   - 同时启动 Django 服务器
   - 一键启动整个后端栈

### 使用调试器

1. 在代码中设置断点（点击行号左侧）
2. 按 F5 启动调试
3. 触发功能（如 API 调用）
4. 代码将在断点处暂停
5. 使用调试控制台查看变量值

## 📁 环境配置文件

### backend/.env

```
USE_CLOUD_SQL=False
DEBUG=True
SECRET_KEY=django-insecure-local-dev-key-for-windows
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
USE_AUTHENTICATED_SCRAPER=True
AI_API_KEY_GOOGLE=
```

### frontend/.env

```
REACT_APP_API_URL=http://localhost:8000/api
```

## 🔍 服务访问地址

- **前端应用**: http://localhost:3000
- **后端 API**: http://localhost:8000/api
- **Django Admin**: http://localhost:8000/admin
- **Redis**: localhost:6379
- **调试工具**: http://localhost:3000/debug-scrape

## 📦 依赖管理

### 前端依赖更新

```powershell
cd frontend
npm install
```

当前安装: 1628 packages (9 个安全警告，非阻塞性)

### 后端依赖更新

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

当前安装: 82 packages including:

- Django 5.2.8
- djangorestframework 3.16.1
- celery 5.5.3
- redis 7.0.1
- playwright 1.55.0

### Playwright 浏览器

```powershell
cd backend
.\venv\Scripts\Activate.ps1
playwright install chromium
```

当前安装: Chromium 140.0.7339.16 (~242 MB)

## 🛑 停止服务

### 停止前端

在前端终端中按 `Ctrl+C`

### 停止后端

在后端终端中按 `Ctrl+C` 或在 VS Code 中停止调试

### 停止 Docker 服务

```powershell
docker-compose down
```

## 🔧 常见问题

### Q: 端口被占用

**A:** 检查并关闭占用端口的进程

```powershell
# 检查3000端口
netstat -ano | findstr :3000
# 检查8000端口
netstat -ano | findstr :8000
# 终止进程
taskkill /PID <进程ID> /F
```

### Q: Redis 连接失败

**A:** 确保 Docker 容器正在运行

```powershell
docker ps | findstr redis
docker-compose up -d redis
```

### Q: Celery 任务不执行

**A:** 检查 Celery worker 状态

```powershell
docker logs auto-ski-info-subscribe-celery-1
docker-compose restart celery celery-beat
```

### Q: 数据库迁移

**A:** 在本地运行迁移

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
```

### Q: 前端无法连接后端 API

**A:** 检查环境配置

1. 确认 `frontend/.env` 中 `REACT_APP_API_URL=http://localhost:8000/api`
2. 确认后端在 8000 端口运行
3. 重启前端服务器

## 🎯 开发工作流

1. **启动环境**

   ```powershell
   # Terminal 1: Docker服务
   docker-compose up -d redis celery celery-beat

   # Terminal 2: 后端
   cd backend
   .\venv\Scripts\Activate.ps1
   python manage.py runserver

   # Terminal 3: 前端
   cd frontend
   npm start
   ```

2. **开发代码**

   - 修改后端代码 → 自动重载
   - 修改前端代码 → 热更新
   - 设置断点 → F5 调试

3. **测试功能**

   - 访问 http://localhost:3000
   - 使用调试工具测试爬虫: http://localhost:3000/debug-scrape
   - 查看 API 文档: http://localhost:8000/api

4. **提交代码**
   ```powershell
   git add .
   git commit -m "描述更改"
   git push
   ```

## 📊 数据和日志

### 数据库位置

- SQLite: `backend/data/db.sqlite3`
- 在本地和 Docker 容器间共享

### 日志位置

- Django 日志: 终端输出
- Celery 日志: `docker logs auto-ski-info-subscribe-celery-1`
- 调试 HTML 文件: `backend/data/debug_*.html`

## 🔄 从 Docker 环境迁移

如果之前使用完整 Docker 环境:

1. ✅ **已完成**: 前端和后端镜像已删除
2. ✅ **已保留**: Redis 和 Celery 在 Docker 中继续运行
3. ✅ **数据保留**: SQLite 数据库文件通过 volume 映射保持不变
4. ✅ **配置更新**: 环境变量已更新为本地开发模式

## 📝 下一步

- [ ] 测试登录功能
- [ ] 测试账号添加功能
- [ ] 使用调试工具 `/debug-scrape` 测试 URL 爬取
- [ ] 分析为什么推文爬取返回 0 条数据
- [ ] 修复推文选择器问题

## 🆘 需要帮助?

- 检查终端错误输出
- 查看 Docker 日志: `docker logs <container-name>`
- 查看 Django 错误页面
- 使用 VS Code 调试器设置断点
