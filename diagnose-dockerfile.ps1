# Dockerfile 诊断脚本
# 检查可能导致 Cloud Run 部署失败的问题

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Dockerfile 配置诊断" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()
$warnings = @()

# 读取 Dockerfile
$dockerfile = Get-Content "Dockerfile" -Raw

# 检查 1: EXPOSE 端口
Write-Host "[检查 1] EXPOSE 端口配置..." -ForegroundColor Yellow
if ($dockerfile -match "EXPOSE\s+8080") {
    Write-Host "✅ EXPOSE 8080 已配置" -ForegroundColor Green
}
else {
    $issues += "❌ 未找到 EXPOSE 8080"
    Write-Host "❌ 未找到 EXPOSE 8080" -ForegroundColor Red
}

# 检查 2: 基础镜像兼容性
Write-Host ""
Write-Host "[检查 2] 基础镜像兼容性..." -ForegroundColor Yellow
if ($dockerfile -match "FROM nginx:alpine") {
    $warnings += "⚠️  使用 nginx:alpine 作为最终镜像，可能存在 Python 路径兼容问题"
    Write-Host "⚠️  使用 nginx:alpine，可能与 Python 3.11 路径不兼容" -ForegroundColor Yellow
    Write-Host "   建议: 改用 python:3.11-slim 并手动安装 nginx" -ForegroundColor Gray
}
else {
    Write-Host "✅ 未使用 alpine 作为最终镜像" -ForegroundColor Green
}

# 检查 3: supervisord 配置
Write-Host ""
Write-Host "[检查 3] Supervisord 配置..." -ForegroundColor Yellow
if (Test-Path "supervisord.combined.conf") {
    $supervisord = Get-Content "supervisord.combined.conf" -Raw
    
    if ($supervisord -match "nodaemon=true") {
        Write-Host "✅ supervisord nodaemon=true 已配置" -ForegroundColor Green
    }
    else {
        $issues += "❌ supervisord 未设置 nodaemon=true"
        Write-Host "❌ supervisord 未设置 nodaemon=true" -ForegroundColor Red
    }
    
    if ($supervisord -match "/var/log/supervisor") {
        $warnings += "⚠️  supervisord 日志路径使用文件系统，建议改为 stdout/stderr"
        Write-Host "⚠️  建议将日志输出到 stdout/stderr 而不是文件" -ForegroundColor Yellow
    }
    
    if ($supervisord -match "startsecs") {
        Write-Host "✅ 配置了进程启动等待时间" -ForegroundColor Green
    }
    else {
        $warnings += "⚠️  未配置 startsecs，可能导致进程启动检查过快"
        Write-Host "⚠️  未配置 startsecs，建议添加" -ForegroundColor Yellow
    }
}
else {
    $issues += "❌ 找不到 supervisord.combined.conf"
    Write-Host "❌ 找不到 supervisord.combined.conf" -ForegroundColor Red
}

# 检查 4: nginx 配置
Write-Host ""
Write-Host "[检查 4] Nginx 配置..." -ForegroundColor Yellow
if (Test-Path "nginx.combined.conf") {
    $nginx = Get-Content "nginx.combined.conf" -Raw
    
    if ($nginx -match "listen\s+8080") {
        Write-Host "✅ nginx 监听端口 8080" -ForegroundColor Green
    }
    else {
        $issues += "❌ nginx 未监听 8080 端口"
        Write-Host "❌ nginx 未监听 8080 端口" -ForegroundColor Red
    }
    
    if ($nginx -match "upstream\s+backend") {
        Write-Host "✅ 配置了 backend upstream" -ForegroundColor Green
    }
    
    if ($nginx -match "127\.0\.0\.1:8000") {
        Write-Host "✅ backend 指向 127.0.0.1:8000" -ForegroundColor Green
    }
    else {
        $issues += "❌ backend upstream 未正确配置"
        Write-Host "❌ backend upstream 未正确配置" -ForegroundColor Red
    }
}
else {
    $issues += "❌ 找不到 nginx.combined.conf"
    Write-Host "❌ 找不到 nginx.combined.conf" -ForegroundColor Red
}

# 检查 5: 启动脚本
Write-Host ""
Write-Host "[检查 5] 启动脚本..." -ForegroundColor Yellow
if ($dockerfile -match "startup\.sh") {
    Write-Host "✅ 使用了 startup.sh" -ForegroundColor Green
    
    if ($dockerfile -match "migrate.*--noinput") {
        Write-Host "✅ 包含数据库迁移步骤" -ForegroundColor Green
        $warnings += "⚠️  数据库迁移可能导致启动超时（Cloud Run 默认 240 秒）"
        Write-Host "⚠️  注意: 迁移可能导致 Cloud Run 启动超时" -ForegroundColor Yellow
    }
    
    if ($dockerfile -match "collectstatic") {
        Write-Host "✅ 包含静态文件收集步骤" -ForegroundColor Green
    }
    
    if ($dockerfile -match "exec.*supervisord") {
        Write-Host "✅ 使用 exec 启动 supervisord" -ForegroundColor Green
    }
    else {
        $warnings += "⚠️  未使用 exec 启动 supervisord，可能导致信号传递问题"
        Write-Host "⚠️  建议使用 exec supervisord 而不是直接调用" -ForegroundColor Yellow
    }
}
else {
    $issues += "❌ 未找到 startup.sh 配置"
    Write-Host "❌ 未找到 startup.sh 配置" -ForegroundColor Red
}

# 检查 6: Python 路径兼容性
Write-Host ""
Write-Host "[检查 6] Python 路径兼容性..." -ForegroundColor Yellow
if ($dockerfile -match "COPY --from=backend-builder /usr/local/lib/python3.11") {
    if ($dockerfile -match "FROM nginx:alpine") {
        $issues += "❌ 严重: Debian Python 路径复制到 Alpine 系统"
        Write-Host "❌ 严重问题: 从 Debian (backend-builder) 复制 Python 到 Alpine (nginx:alpine)" -ForegroundColor Red
        Write-Host "   这会导致 Python 模块无法导入！" -ForegroundColor Red
        Write-Host "   解决方案: 使用统一的基础镜像 (python:3.11-slim)" -ForegroundColor Yellow
    }
    else {
        Write-Host "✅ Python 路径复制正确" -ForegroundColor Green
    }
}

# 检查 7: 目录创建
Write-Host ""
Write-Host "[检查 7] 必要目录创建..." -ForegroundColor Yellow
if ($dockerfile -match "mkdir.*-p.*\/app\/data") {
    Write-Host "✅ 创建了 /app/data 目录" -ForegroundColor Green
}
else {
    $warnings += "⚠️  未在 Dockerfile 中创建 /app/data"
    Write-Host "⚠️  建议在 Dockerfile 中预创建 /app/data" -ForegroundColor Yellow
}

if ($dockerfile -match "mkdir.*\/var\/log\/supervisor") {
    Write-Host "✅ 创建了 /var/log/supervisor 目录" -ForegroundColor Green
}
else {
    if ($supervisord -match "/var/log/supervisor") {
        $warnings += "⚠️  supervisord 使用 /var/log/supervisor 但未创建目录"
        Write-Host "⚠️  supervisord 使用 /var/log/supervisor 但未创建目录" -ForegroundColor Yellow
    }
}

# 汇总报告
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "诊断汇总" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

if ($issues.Count -eq 0) {
    Write-Host "✅ 未发现严重问题" -ForegroundColor Green
}
else {
    Write-Host "发现 $($issues.Count) 个严重问题:" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  $issue" -ForegroundColor Red
    }
}

Write-Host ""
if ($warnings.Count -eq 0) {
    Write-Host "✅ 无警告" -ForegroundColor Green
}
else {
    Write-Host "发现 $($warnings.Count) 个警告:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  $warning" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "推荐修复方案" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

if ($dockerfile -match "FROM nginx:alpine" -and $dockerfile -match "COPY --from=backend-builder /usr/local/lib/python3.11") {
    Write-Host "🔧 关键修复: 修改最终镜像为 python:3.11-slim" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   修改前:" -ForegroundColor Gray
    Write-Host "   FROM nginx:alpine" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   修改后:" -ForegroundColor Green
    Write-Host "   FROM python:3.11-slim" -ForegroundColor Green
    Write-Host ""
    Write-Host "   然后添加:" -ForegroundColor Green
    Write-Host "   RUN apt-get update && apt-get install -y nginx supervisor ..." -ForegroundColor Green
}

Write-Host ""
Write-Host "完成诊断！" -ForegroundColor Cyan
