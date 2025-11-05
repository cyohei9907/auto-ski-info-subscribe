# 🐳 Docker 实时调试 - 快速开始

## 方式一：使用 PowerShell 脚本（推荐新手）

1. **运行快速启动脚本**：

   ```powershell
   .\docker-dev.ps1
   ```

2. **选择操作**：

   - 首次使用选择 `1` 构建镜像（需要 5-10 分钟）
   - 然后选择 `2` 启动服务
   - 选择 `9` 运行数据库迁移

3. **开始调试**：
   - 在 VS Code 中按 `Ctrl+Shift+D`
   - 选择 `🐳 Docker: Full Stack Debug`
   - 按 `F5` 开始调试

## 方式二：使用 VS Code 任务

1. **构建镜像**（首次）：

   - `Ctrl+Shift+P` → `Tasks: Run Task`
   - 选择 `Docker: Build Dev Images`

2. **启动调试**：
   - `Ctrl+Shift+D` 打开调试面板
   - 选择 `🐳 Docker: Full Stack Debug`
   - 按 `F5`

## 方式三：手动命令行

```powershell
# 1. 构建镜像（首次）
docker-compose -f docker-compose.dev.yml build

# 2. 启动服务
docker-compose -f docker-compose.dev.yml up -d

# 3. 运行迁移
docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

# 4. 在 VS Code 中附加调试器
# 选择 "Docker: Backend (Remote)" 并按 F5

# 5. 查看日志
docker-compose -f docker-compose.dev.yml logs -f

# 6. 停止服务
docker-compose -f docker-compose.dev.yml down
```

## 访问地址

- 🌐 前端：http://localhost:3000
- 🔧 后端 API：http://localhost:8000
- 👤 Django Admin：http://localhost:8000/admin
- 🐛 调试端口：5678 (Backend), 5679 (Celery), 5680 (Beat)

## 调试功能

✅ 代码热重载（修改即生效）  
✅ 设置断点暂停执行  
✅ 检查变量值  
✅ 单步调试  
✅ 前后端同时调试

详细文档：查看 `DOCKER_DEBUG.md`
