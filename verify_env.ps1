# 环境变量验证脚本 - Windows PowerShell
# 用途：验证 AI_API_KEY_GOOGLE 环境变量是否正确设置

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "环境变量验证脚本" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# 检查新的环境变量
$aiKey = [System.Environment]::GetEnvironmentVariable('AI_API_KEY_GOOGLE', 'User')
$oldKey = [System.Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'User')

Write-Host "1. 检查系统环境变量:" -ForegroundColor Cyan
if ($aiKey) {
    Write-Host "   AI_API_KEY_GOOGLE: " -NoNewline
    Write-Host "✅ 已设置" -ForegroundColor Green
    if ($aiKey.Length -gt 14) {
        $masked = $aiKey.Substring(0, 10) + "..." + $aiKey.Substring($aiKey.Length - 4)
        Write-Host "   值: $masked" -ForegroundColor Gray
    } else {
        Write-Host "   值: $aiKey" -ForegroundColor Gray
    }
} else {
    Write-Host "   AI_API_KEY_GOOGLE: " -NoNewline
    Write-Host "❌ 未设置" -ForegroundColor Red
}

if ($oldKey) {
    Write-Host ""
    Write-Host "   ⚠️  警告: 旧环境变量 GEMINI_API_KEY 仍然存在" -ForegroundColor Yellow
    Write-Host "   建议删除旧环境变量，只保留 AI_API_KEY_GOOGLE" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   执行以下命令删除旧环境变量:" -ForegroundColor Gray
    Write-Host "   [System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', `$null, 'User')" -ForegroundColor Gray
}

# 检查 .env 文件
Write-Host ""
Write-Host "2. 检查 .env 文件:" -ForegroundColor Cyan
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Write-Host "   .env 文件: " -NoNewline
    Write-Host "✅ 存在" -ForegroundColor Green
    
    $content = Get-Content $envFile -Raw
    if ($content -match "AI_API_KEY_GOOGLE") {
        Write-Host "   AI_API_KEY_GOOGLE: " -NoNewline
        Write-Host "✅ 已配置" -ForegroundColor Green
    } else {
        Write-Host "   AI_API_KEY_GOOGLE: " -NoNewline
        Write-Host "❌ 未配置" -ForegroundColor Red
    }
    
    if ($content -match "GEMINI_API_KEY") {
        Write-Host "   ⚠️  警告: .env 文件中仍有 GEMINI_API_KEY" -ForegroundColor Yellow
    }
} else {
    Write-Host "   .env 文件: " -NoNewline
    Write-Host "❌ 不存在" -ForegroundColor Red
}

# 检查 docker-compose.yml
Write-Host ""
Write-Host "3. 检查 docker-compose.yml:" -ForegroundColor Cyan
$dockerComposeFile = Join-Path (Split-Path $PSScriptRoot -Parent) "docker-compose.yml"
if (Test-Path $dockerComposeFile) {
    Write-Host "   docker-compose.yml: " -NoNewline
    Write-Host "✅ 存在" -ForegroundColor Green
    
    $content = Get-Content $dockerComposeFile -Raw
    if ($content -match "AI_API_KEY_GOOGLE") {
        Write-Host "   AI_API_KEY_GOOGLE: " -NoNewline
        Write-Host "✅ 已配置" -ForegroundColor Green
    } else {
        Write-Host "   AI_API_KEY_GOOGLE: " -NoNewline
        Write-Host "❌ 未配置" -ForegroundColor Red
    }
    
    if ($content -match 'GEMINI_API_KEY:\s*\$\{GEMINI_API_KEY') {
        Write-Host "   ⚠️  警告: docker-compose.yml 中仍使用 GEMINI_API_KEY" -ForegroundColor Yellow
    }
} else {
    Write-Host "   docker-compose.yml: " -NoNewline
    Write-Host "❌ 不存在" -ForegroundColor Red
}

# 总结
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
if ($aiKey -and -not $oldKey) {
    Write-Host "✅ 配置正确！环境变量迁移完成" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步：重启 PowerShell 或运行以下命令测试:" -ForegroundColor Cyan
    Write-Host "  cd backend" -ForegroundColor Gray
    Write-Host "  python verify_env.py" -ForegroundColor Gray
} elseif ($aiKey -and $oldKey) {
    Write-Host "⚠️  建议删除旧的 GEMINI_API_KEY 环境变量" -ForegroundColor Yellow
} else {
    Write-Host "❌ 请设置 AI_API_KEY_GOOGLE 环境变量" -ForegroundColor Red
    Write-Host ""
    Write-Host "设置命令:" -ForegroundColor Cyan
    Write-Host "  [System.Environment]::SetEnvironmentVariable('AI_API_KEY_GOOGLE', 'your-key', 'User')" -ForegroundColor Gray
}
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
