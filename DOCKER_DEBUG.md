# 🐳 Docker 实时调试配置指南

本项目已配置完整的 Docker 开发环境，支持在容器中运行并进行实时调试。

## 🎯 功能特性

- ✅ 在 Docker 容器中运行所有服务
- ✅ 支持代码热重载（无需重启容器）
- ✅ VS Code 远程调试（通过 debugpy）
- ✅ 前端和后端实时调试
- ✅ 完全隔离的开发环境

## 📋 前置要求

1. **Docker Desktop** - 已安装并运行
2. **VS Code** - 安装以下扩展：
   - Python (ms-python.python)
   - Docker (ms-azuretools.vscode-docker)
   - Debugger for Chrome/Edge

## 🚀 快速开始

### 方法一：使用 VS Code 调试面板（推荐）

1. **首次构建镜像**（只需一次）：

   - 按 `Ctrl+Shift+P`
   - 运行 `Tasks: Run Task` → `Docker: Build Dev Images`
   - 等待构建完成（约 5-10 分钟）

2. **启动调试**：

   - 按 `Ctrl+Shift+D` 打开调试面板
   - 选择 `🐳 Docker: Full Stack Debug` 或 `🐳 Docker: All Services Debug`
   - 按 `F5` 开始调试

3. **访问应用**：
   - 前端：http://localhost:3000
   - 后端 API：http://localhost:8000
   - Django Admin：http://localhost:8000/admin

### 方法二：使用命令行

1. **构建开发镜像**：

   ```powershell
   docker-compose -f docker-compose.dev.yml build
   ```

2. **启动所有服务**：

   ```powershell
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **在 VS Code 中附加调试器**：

   - 打开调试面板
   - 选择 `Docker: Backend (Remote)`
   - 按 `F5` 连接到容器中的调试器

4. **查看日志**：

   ```powershell
   docker-compose -f docker-compose.dev.yml logs -f
   ```

5. **停止所有服务**：
   ```powershell
   docker-compose -f docker-compose.dev.yml down
   ```

## 🐛 调试配置说明

### 可用的调试配置

1. **Docker: Backend (Remote)** - 调试后端容器

   - 远程端口：5678
   - 支持断点和变量检查
   - 代码热重载（修改后自动重启）

2. **Docker: Celery Worker (Remote)** - 调试 Celery 任务

   - 远程端口：5679
   - 使用 `--pool=solo` 模式便于调试

3. **Docker: Celery Beat (Remote)** - 调试定时任务

   - 远程端口：5680

4. **Docker: Frontend (Chrome)** - 调试前端
   - 连接到 http://localhost:3000
   - 支持 React 源码调试

### 组合调试配置

1. **🐳 Docker: Full Stack Debug** - Django + React

   - 自动启动所有容器
   - 附加后端和前端调试器
   - 最常用的开发配置

2. **🐳 Docker: All Services Debug** - 完整服务
   - 启动所有服务（Backend, Celery, Beat, Frontend）
   - 同时调试所有组件

## 🔧 实时调试功能

### 后端热重载

- 修改 Python 代码后自动重启 Django
- 无需手动重启容器
- 断点在重启后保持有效

### 前端热重载

- 修改 React 代码立即反映在浏览器
- 支持 CSS 和 JSX 热更新
- 保持应用状态

### 设置断点

1. 在代码行号左侧点击设置断点（红点）
2. 运行到断点时自动暂停
3. 可以检查变量、调用堆栈等

## 📁 文件说明

### Docker 配置文件

- **`docker-compose.dev.yml`** - 开发环境配置

  - 包含所有服务定义
  - 挂载源码目录实现热重载
  - 暴露调试端口（5678, 5679, 5680）

- **`backend/Dockerfile.dev`** - 后端开发镜像

  - 安装 debugpy 调试器
  - 暴露调试端口 5678

- **`backend/entrypoint.dev.sh`** - 后端启动脚本

  - 运行数据库迁移
  - 启动带调试的 Django 服务器

- **`frontend/Dockerfile.dev`** - 前端开发镜像
  - 支持热重载
  - 开发服务器模式

## 🎮 常用任务

通过 `Ctrl+Shift+P` → `Tasks: Run Task` 运行：

### Docker 开发任务

- **Docker: Build Dev Images** - 构建开发镜像（首次使用）
- **Docker: Start Dev Services** - 启动所有容器
- **Docker: Stop Dev Services** - 停止所有容器
- **Docker: View Dev Logs** - 查看容器日志
- **Docker: Restart Backend** - 重启后端容器
- **Docker: Shell into Backend** - 进入后端容器 Shell

## 🔍 调试技巧

### 1. 查看容器状态

```powershell
docker-compose -f docker-compose.dev.yml ps
```

### 2. 查看特定服务日志

```powershell
# 后端日志
docker-compose -f docker-compose.dev.yml logs -f backend

# Celery 日志
docker-compose -f docker-compose.dev.yml logs -f celery

# 前端日志
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### 3. 进入容器执行命令

```powershell
# 进入后端容器
docker-compose -f docker-compose.dev.yml exec backend bash

# 运行 Django 管理命令
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

### 4. 重启特定服务

```powershell
docker-compose -f docker-compose.dev.yml restart backend
docker-compose -f docker-compose.dev.yml restart celery
```

### 5. 查看容器资源使用

```powershell
docker stats
```

## 🆘 故障排除

### 调试器无法连接

1. 确认容器正在运行：

   ```powershell
   docker-compose -f docker-compose.dev.yml ps
   ```

2. 检查端口是否暴露：

   ```powershell
   docker-compose -f docker-compose.dev.yml port backend 5678
   ```

3. 查看后端日志确认 debugpy 已启动：
   ```powershell
   docker-compose -f docker-compose.dev.yml logs backend
   ```
   应该看到 "Starting Django with debugpy on port 5678..."

### 代码修改不生效

1. 确认卷挂载正确：

   ```powershell
   docker-compose -f docker-compose.dev.yml config
   ```

2. 重启相关容器：
   ```powershell
   docker-compose -f docker-compose.dev.yml restart backend
   ```

### 前端无法访问后端 API

1. 检查后端容器状态和日志
2. 确认 CORS 设置（在 `settings.py` 中）
3. 检查网络连接：
   ```powershell
   docker network inspect auto-ski-info-subscribe_auto-ski-network
   ```

### 容器启动失败

1. 查看详细日志：

   ```powershell
   docker-compose -f docker-compose.dev.yml logs backend
   ```

2. 重新构建镜像：

   ```powershell
   docker-compose -f docker-compose.dev.yml build --no-cache
   ```

3. 清理并重启：
   ```powershell
   docker-compose -f docker-compose.dev.yml down -v
   docker-compose -f docker-compose.dev.yml up -d
   ```

## 💡 最佳实践

### 1. 首次设置工作流

```powershell
# 1. 构建镜像
docker-compose -f docker-compose.dev.yml build

# 2. 启动服务
docker-compose -f docker-compose.dev.yml up -d

# 3. 运行迁移（首次）
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

# 4. 创建超级用户（可选）
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser

# 5. 在 VS Code 中开始调试
```

### 2. 日常开发工作流

1. 打开 VS Code
2. 按 `F5` 启动调试（会自动启动容器）
3. 设置断点并开始开发
4. 修改代码自动重载
5. 完成后停止调试（容器继续运行）

### 3. 关闭开发环境

```powershell
docker-compose -f docker-compose.dev.yml down
```

### 4. 完全清理（包括数据）

```powershell
docker-compose -f docker-compose.dev.yml down -v
```

## 🔄 本地开发 vs Docker 开发

### 本地开发（传统方式）

- 需要在本机安装 Python、Node.js、Redis
- 配置环境变量
- 手动管理多个终端和进程
- 使用配置：`Django: Backend`, `Chrome: Frontend`

### Docker 开发（推荐）

- ✅ 所有依赖都在容器中
- ✅ 环境完全隔离和可复现
- ✅ 一键启动所有服务
- ✅ 团队成员环境一致
- 使用配置：`🐳 Docker: Full Stack Debug`

## 📚 相关文档

- [Docker Compose 文档](https://docs.docker.com/compose/)
- [debugpy 文档](https://github.com/microsoft/debugpy)
- [VS Code Docker 扩展](https://code.visualstudio.com/docs/containers/overview)
- [VS Code Python 调试](https://code.visualstudio.com/docs/python/debugging)

## 🎓 学习资源

### 设置断点

- 在代码行号左侧点击 → 红点出现
- 条件断点：右键断点 → 编辑断点
- 日志断点：不暂停，只输出日志

### 调试控制

- `F5` - 继续执行
- `F10` - 单步跳过
- `F11` - 单步进入
- `Shift+F11` - 单步跳出
- `Shift+F5` - 停止调试

### 变量检查

- 悬停在变量上查看值
- 左侧调试面板查看所有变量
- 调试控制台执行表达式

---

现在你可以在 Docker 容器中享受完整的开发和调试体验了！🚀
