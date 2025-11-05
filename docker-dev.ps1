# Docker 开发环境快速启动脚本

Write-Host "🐳 Auto Ski Info - Docker 开发环境" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否运行
Write-Host "检查 Docker Desktop..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker Desktop 未运行！请先启动 Docker Desktop。" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker Desktop 正在运行" -ForegroundColor Green
Write-Host ""

# 检查环境变量文件
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  未找到 .env 文件" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "正在从 .env.example 创建 .env 文件..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "✅ 已创建 .env 文件，请编辑并添加你的 API 密钥" -ForegroundColor Green
        Write-Host ""
    }
}

# 提供选项菜单
Write-Host "请选择操作：" -ForegroundColor Cyan
Write-Host "1. 🏗️  首次构建（构建 Docker 镜像）" -ForegroundColor White
Write-Host "2. 🚀 启动服务（启动所有容器）" -ForegroundColor White
Write-Host "3. 🔍 查看日志" -ForegroundColor White
Write-Host "4. 🛑 停止服务" -ForegroundColor White
Write-Host "5. 🔄 重启后端" -ForegroundColor White
Write-Host "6. 🗑️  清理（停止并删除容器和数据卷）" -ForegroundColor White
Write-Host "7. 📊 查看容器状态" -ForegroundColor White
Write-Host "8. 🐚 进入后端容器 Shell" -ForegroundColor White
Write-Host "9. ⚙️  运行数据库迁移" -ForegroundColor White
Write-Host "0. 退出" -ForegroundColor White
Write-Host ""

$choice = Read-Host "输入选项 (0-9)"

switch ($choice) {
    "1" {
        Write-Host "🏗️  开始构建 Docker 镜像..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml build
        Write-Host "✅ 构建完成！" -ForegroundColor Green
        Write-Host "💡 提示：现在可以运行选项 2 启动服务，或直接在 VS Code 中按 F5 调试" -ForegroundColor Cyan
    }
    "2" {
        Write-Host "🚀 启动所有服务..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml up -d
        Write-Host ""
        Write-Host "✅ 服务已启动！" -ForegroundColor Green
        Write-Host ""
        Write-Host "📍 访问地址：" -ForegroundColor Cyan
        Write-Host "   前端: http://localhost:3000" -ForegroundColor White
        Write-Host "   后端: http://localhost:8000" -ForegroundColor White
        Write-Host "   Admin: http://localhost:8000/admin" -ForegroundColor White
        Write-Host ""
        Write-Host "🐛 调试端口：" -ForegroundColor Cyan
        Write-Host "   Backend: localhost:5678" -ForegroundColor White
        Write-Host "   Celery Worker: localhost:5679" -ForegroundColor White
        Write-Host "   Celery Beat: localhost:5680" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 在 VS Code 中按 Ctrl+Shift+D，选择 '🐳 Docker: Full Stack Debug'，按 F5 开始调试" -ForegroundColor Cyan
    }
    "3" {
        Write-Host "🔍 查看日志（按 Ctrl+C 退出）..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml logs -f
    }
    "4" {
        Write-Host "🛑 停止所有服务..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml down
        Write-Host "✅ 服务已停止" -ForegroundColor Green
    }
    "5" {
        Write-Host "🔄 重启后端容器..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml restart backend
        Write-Host "✅ 后端已重启" -ForegroundColor Green
    }
    "6" {
        Write-Host "⚠️  这将删除所有容器和数据！" -ForegroundColor Red
        $confirm = Read-Host "确认继续？(y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            Write-Host "🗑️  清理中..." -ForegroundColor Yellow
            docker-compose -f docker-compose.dev.yml down -v
            Write-Host "✅ 清理完成" -ForegroundColor Green
        }
        else {
            Write-Host "已取消" -ForegroundColor Yellow
        }
    }
    "7" {
        Write-Host "📊 容器状态：" -ForegroundColor Cyan
        Write-Host ""
        docker-compose -f docker-compose.dev.yml ps
        Write-Host ""
        Write-Host "💾 资源使用：" -ForegroundColor Cyan
        docker stats --no-stream
    }
    "8" {
        Write-Host "🐚 进入后端容器 Shell..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml exec backend bash
    }
    "9" {
        Write-Host "⚙️  运行数据库迁移..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
        Write-Host "✅ 迁移完成" -ForegroundColor Green
        Write-Host ""
        $createUser = Read-Host "是否创建超级用户？(y/N)"
        if ($createUser -eq "y" -or $createUser -eq "Y") {
            docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
        }
    }
    "0" {
        Write-Host "👋 再见！" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "❌ 无效选项" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
