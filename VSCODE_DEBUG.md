# VS Code 调试配置说明

本项目已配置完整的 VS Code 调试和任务设置，支持快速启动和调试。

## 📋 前置要求

1. **Python 3.8+** - Django 后端
2. **Node.js 16+** - React 前端
3. **Docker** - 用于 Redis 和容器化部署
4. **Redis** - Celery 任务队列（可通过 Docker 运行）

## 🚀 快速开始

### 1. 首次设置

1. 复制环境变量文件：

   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入你的 API 密钥

3. 安装后端依赖：

   - 按 `Ctrl+Shift+P` (Windows) 或 `Cmd+Shift+P` (Mac)
   - 运行任务：`Tasks: Run Task` → `Install Backend Dependencies`

4. 安装前端依赖：

   - 运行任务：`Tasks: Run Task` → `Install Frontend Dependencies`

5. 数据库迁移：

   - 运行任务：`Tasks: Run Task` → `Django: Migrate Database`

6. 创建超级用户（可选）：
   - 运行任务：`Tasks: Run Task` → `Django: Create Superuser`

### 2. 启动 Redis（必需）

运行任务：`Tasks: Run Task` → `Start Redis`

或手动运行：

```bash
docker run -d --name auto-ski-redis -p 6379:6379 redis:7-alpine
```

## 🐛 调试配置

### 单独调试配置

在调试面板（`Ctrl+Shift+D`）中选择以下配置之一：

1. **Django: Backend** - 调试 Django 后端服务器

   - 端口：`http://localhost:8000`
   - 包含所有 Django 断点和调试功能

2. **Django: Celery Worker** - 调试 Celery 后台任务

   - 使用 `--pool=solo` 模式便于调试

3. **Django: Celery Beat** - 调试定时任务调度器

4. **Chrome: Frontend** - 在 Chrome 中调试 React 前端

   - 端口：`http://localhost:3000`
   - 需要先手动启动前端开发服务器

5. **Edge: Frontend** - 在 Edge 中调试 React 前端

### 组合调试配置（推荐）

这些配置会同时启动多个服务：

1. **Full Stack: Django + React**

   - 自动启动前端开发服务器
   - 启动 Django 后端
   - 在 Chrome 中打开前端

2. **Full Stack: Django + Celery**

   - 启动 Django 后端
   - 启动 Celery Worker

3. **All Services**（完整开发环境）
   - 启动 Django 后端
   - 启动 Celery Worker
   - 启动 Celery Beat
   - 自动启动前端开发服务器

## 📝 常用任务

通过 `Ctrl+Shift+P` → `Tasks: Run Task` 运行：

### 开发任务

- **Install Backend Dependencies** - 安装 Python 包
- **Install Frontend Dependencies** - 安装 npm 包
- **Django: Migrate Database** - 运行数据库迁移
- **Django: Make Migrations** - 创建新的迁移文件
- **Django: Create Superuser** - 创建管理员账户

### 测试和构建

- **Django: Run Tests** - 运行 Python 测试（默认测试任务）
- **Frontend: Build** - 构建生产版本前端（默认构建任务）

### Docker 任务

- **Start Redis** - 启动 Redis 容器
- **Stop Redis** - 停止并删除 Redis 容器
- **Docker: Build All** - 构建所有 Docker 镜像
- **Docker: Up All Services** - 启动所有服务
- **Docker: Down All Services** - 停止所有服务
- **Docker: View Logs** - 查看容器日志

## 🔧 推荐的调试工作流

### 开发全栈应用

1. 确保 Redis 正在运行：

   ```bash
   docker ps | grep redis
   ```

   如果没有运行，执行任务 `Start Redis`

2. 在调试面板选择 **"All Services"**

3. 按 `F5` 启动所有服务

4. 访问：
   - 前端：http://localhost:3000
   - 后端 API：http://localhost:8000
   - Django Admin：http://localhost:8000/admin

### 只调试后端

1. 启动 Redis
2. 选择 **"Django: Backend"** 配置
3. 按 `F5` 开始调试
4. 在代码中设置断点即可

### 调试 Celery 任务

1. 启动 Redis
2. 启动 Django 后端（终端或调试）
3. 选择 **"Django: Celery Worker"** 配置
4. 按 `F5` 开始调试
5. 在 Celery 任务代码中设置断点

## 🌐 环境变量

所有环境变量都在 `.env` 文件中配置，包括：

- `AI_API_KEY_GOOGLE` - Google Gemini AI API 密钥
- `X_API_KEY` 等 - Twitter/X API 凭据
- `DEBUG` - 调试模式开关
- `REDIS_URL` - Redis 连接 URL

## 📦 推荐的 VS Code 扩展

项目已在 `.vscode/extensions.json` 中配置推荐扩展，首次打开项目时 VS Code 会提示安装：

- **Python** - Python 语言支持
- **Pylance** - Python 类型检查和智能提示
- **ESLint** - JavaScript 代码检查
- **Prettier** - 代码格式化
- **Docker** - Docker 支持
- **Django** - Django 模板支持
- **ES7+ React/Redux/React-Native snippets** - React 代码片段

## 🆘 故障排除

### Redis 连接错误

确保 Redis 容器正在运行：

```bash
docker ps | grep redis
```

### 前端无法连接后端

检查后端是否在 http://localhost:8000 运行，并且 CORS 设置正确。

### Celery 任务不执行

确保 Celery Worker 正在运行，并且 Redis 可访问。

### 数据库错误

运行数据库迁移：

```bash
cd backend
python manage.py migrate
```

## 📚 更多信息

- [Django 文档](https://docs.djangoproject.com/)
- [React 文档](https://react.dev/)
- [Celery 文档](https://docs.celeryq.dev/)
- [Docker 文档](https://docs.docker.com/)
