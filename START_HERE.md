# 🎯 现在开始调试！

所有 Docker 容器已成功启动并正在运行：

## ✅ 当前状态

- ✅ **Backend** - 正在运行，等待调试器连接（端口 5678）
- ✅ **Celery Worker** - 正在运行（端口 5679）
- ✅ **Celery Beat** - 正在运行（端口 5680）
- ✅ **Frontend** - 正在运行（端口 3000）
- ✅ **Redis** - 正在运行（端口 6379）

## 🐛 开始调试

### 方式一：完整调试（推荐）

1. 在 VS Code 中按 `Ctrl+Shift+D` 打开调试面板
2. 从下拉菜单选择 `🐳 Docker: Full Stack Debug`
3. 按 `F5` 开始调试
4. 等待调试器连接到后端容器
5. 在浏览器中访问 http://localhost:3000

### 方式二：仅调试后端

1. 按 `Ctrl+Shift+D` 打开调试面板
2. 选择 `Docker: Backend (Remote)`
3. 按 `F5`
4. 现在可以在后端代码中设置断点了

### 方式三：调试 Celery 任务

1. 按 `Ctrl+Shift+D` 打开调试面板
2. 选择 `Docker: Celery Worker (Remote)`
3. 按 `F5`
4. 在 Celery 任务代码中设置断点

## 🌐 访问地址

- **前端应用**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/swagger/
- **Django Admin**: http://localhost:8000/admin

## 🔧 设置断点

1. 打开任意 Python 文件（如 `backend/x_monitor/views.py`）
2. 在行号左侧点击设置红色断点
3. 触发相应的 API 请求
4. 程序会在断点处暂停
5. 在调试面板查看变量值

## 📝 常用命令

### 查看日志

```powershell
# 所有服务日志
docker-compose -f docker-compose.dev.yml logs -f

# 仅后端日志
docker-compose -f docker-compose.dev.yml logs -f backend

# 仅前端日志
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### 重启服务

```powershell
# 重启后端
docker-compose -f docker-compose.dev.yml restart backend

# 重启所有服务
docker-compose -f docker-compose.dev.yml restart
```

### 停止服务

```powershell
# 停止所有服务
docker-compose -f docker-compose.dev.yml down

# 停止并删除数据卷
docker-compose -f docker-compose.dev.yml down -v
```

### 进入容器

```powershell
# 进入后端容器
docker-compose -f docker-compose.dev.yml exec backend bash

# 运行 Django 命令
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
```

## 🎮 调试技巧

### 单步调试

- `F10` - 单步跳过（执行当前行，不进入函数）
- `F11` - 单步进入（进入函数内部）
- `Shift+F11` - 单步跳出（跳出当前函数）
- `F5` - 继续执行（运行到下一个断点）

### 查看变量

- 悬停在变量上查看值
- 左侧"变量"面板查看所有变量
- "监视"面板添加表达式监视

### 调试控制台

- 在断点暂停时，在调试控制台输入 Python 表达式
- 实时查看和修改变量值

## ⚠️ 常见问题

### 前端无法连接后端

- 确认后端容器正在运行：`docker-compose -f docker-compose.dev.yml ps`
- 检查后端日志：`docker-compose -f docker-compose.dev.yml logs backend`
- 确认端口 8000 没有被占用

### 调试器无法连接

- 确认容器正在运行
- 检查调试端口（5678, 5679, 5680）是否暴露
- 查看容器日志确认 debugpy 已启动

### 代码修改不生效

- Python 代码：容器会自动重启，重新附加调试器即可
- React 代码：应该自动热重载
- 如果不行，重启相关容器

## 📚 下一步

- 查看 [DOCKER_DEBUG.md](DOCKER_DEBUG.md) 了解详细调试功能
- 查看 [VSCODE_DEBUG.md](VSCODE_DEBUG.md) 了解本地开发配置
- 使用 `.\docker-dev.ps1` 脚本快速管理服务

---

现在你已经准备好开始开发了！🚀
在 VS Code 中按 F5 开始调试吧！
