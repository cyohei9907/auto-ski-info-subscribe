# Cloud Build 最低配置部署后设置脚本

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Cloud Build 最低配置 - 部署后设置" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# 获取项目信息
$projectId = gcloud config get-value project 2>$null
if (-not $projectId) {
    Write-Host "❌ 错误: 无法获取项目 ID" -ForegroundColor Red
    exit 1
}

Write-Host "项目 ID: " -NoNewline
Write-Host $projectId -ForegroundColor Green
Write-Host ""

# 获取 Backend URL
Write-Host "1. 获取 Backend URL..." -ForegroundColor Cyan
$backendUrl = gcloud run services describe auto-ski-info-backend `
    --region=asia-northeast1 `
    --format="value(status.url)" 2>$null

if ($backendUrl) {
    Write-Host "   Backend URL: " -NoNewline
    Write-Host $backendUrl -ForegroundColor Green
}
else {
    Write-Host "   ❌ Backend 服务未找到" -ForegroundColor Red
    exit 1
}

# 更新 Frontend 环境变量
Write-Host ""
Write-Host "2. 更新 Frontend 环境变量..." -ForegroundColor Cyan
Write-Host "   设置 REACT_APP_API_URL 为: $backendUrl/api" -ForegroundColor Gray

try {
    gcloud run services update auto-ski-info-frontend `
        --region=asia-northeast1 `
        --set-env-vars="REACT_APP_API_URL=$backendUrl/api" `
        2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Frontend 环境变量更新成功" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ 更新失败" -ForegroundColor Red
    }
}
catch {
    Write-Host "   ❌ 错误: $_" -ForegroundColor Red
}

# 获取 Frontend URL
Write-Host ""
Write-Host "3. 获取 Frontend URL..." -ForegroundColor Cyan
$frontendUrl = gcloud run services describe auto-ski-info-frontend `
    --region=asia-northeast1 `
    --format="value(status.url)" 2>$null

if ($frontendUrl) {
    Write-Host "   Frontend URL: " -NoNewline
    Write-Host $frontendUrl -ForegroundColor Green
}
else {
    Write-Host "   ❌ Frontend 服务未找到" -ForegroundColor Red
}

# 创建智能 Cloud Scheduler
Write-Host ""
Write-Host "4. 创建 Cloud Scheduler (智能分级调度)..." -ForegroundColor Cyan
Write-Host "   这将创建 4 个不同间隔的调度器以节省成本" -ForegroundColor Gray
Write-Host ""

# 定义调度器配置
$schedulers = @(
    @{
        Name        = "monitor-x-accounts-30min"
        Schedule    = "*/30 * * * *"
        Interval    = 30
        Description = "高频监控 (30分钟)"
    },
    @{
        Name        = "monitor-x-accounts-1hour"
        Schedule    = "0 * * * *"
        Interval    = 60
        Description = "中频监控 (1小时)"
    },
    @{
        Name        = "monitor-x-accounts-4hours"
        Schedule    = "0 */4 * * *"
        Interval    = 240
        Description = "低频监控 (4小时)"
    },
    @{
        Name        = "monitor-x-accounts-12hours"
        Schedule    = "0 */12 * * *"
        Interval    = 720
        Description = "极低频监控 (12小时)"
    }
)

$createdCount = 0
$existsCount = 0

foreach ($scheduler in $schedulers) {
    Write-Host "   创建: " -NoNewline
    Write-Host "$($scheduler.Description)" -ForegroundColor Yellow
    
    $uri = "$backendUrl/api/monitor/trigger-monitoring/?interval=$($scheduler.Interval)"
    
    # 检查是否已存在
    $exists = gcloud scheduler jobs list --location=asia-northeast1 2>$null | Select-String $scheduler.Name
    
    if ($exists) {
        Write-Host "      ⚠️  已存在，跳过" -ForegroundColor Yellow
        $existsCount++
    }
    else {
        try {
            gcloud scheduler jobs create http $scheduler.Name `
                --schedule="$($scheduler.Schedule)" `
                --uri="$uri" `
                --http-method=POST `
                --location=asia-northeast1 `
                --time-zone=Asia/Tokyo `
                2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "      ✅ 创建成功" -ForegroundColor Green
                $createdCount++
            }
            else {
                Write-Host "      ❌ 创建失败" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "      ❌ 错误: $_" -ForegroundColor Red
        }
    }
}

# 测试连接
Write-Host ""
Write-Host "5. 测试服务连接..." -ForegroundColor Cyan

Write-Host "   测试 Backend..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "$backendUrl/admin/" -Method Head -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 302) {
        Write-Host "      ✅ Backend 响应正常" -ForegroundColor Green
    }
    else {
        Write-Host "      ⚠️  Backend 返回状态码: $($response.StatusCode)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "      ❌ Backend 无法访问" -ForegroundColor Red
}

Write-Host "   测试 Frontend..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri $frontendUrl -Method Head -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "      ✅ Frontend 响应正常" -ForegroundColor Green
    }
    else {
        Write-Host "      ⚠️  Frontend 返回状态码: $($response.StatusCode)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "      ❌ Frontend 无法访问" -ForegroundColor Red
}

# 显示资源使用情况
Write-Host ""
Write-Host "6. 检查资源配置..." -ForegroundColor Cyan

Write-Host "   Backend 配置:" -ForegroundColor Gray
$backendConfig = gcloud run services describe auto-ski-info-backend `
    --region=asia-northeast1 `
    --format="value(spec.template.spec.containers[0].resources.limits.memory,spec.template.spec.containers[0].resources.limits.cpu,spec.template.spec.containerConcurrency)" `
    2>$null

if ($backendConfig) {
    $parts = $backendConfig -split "`t"
    Write-Host "      Memory: $($parts[0])" -ForegroundColor White
    Write-Host "      CPU: $($parts[1])" -ForegroundColor White
    Write-Host "      Concurrency: $($parts[2])" -ForegroundColor White
}

Write-Host "   Frontend 配置:" -ForegroundColor Gray
$frontendConfig = gcloud run services describe auto-ski-info-frontend `
    --region=asia-northeast1 `
    --format="value(spec.template.spec.containers[0].resources.limits.memory,spec.template.spec.containers[0].resources.limits.cpu,spec.template.spec.containerConcurrency)" `
    2>$null

if ($frontendConfig) {
    $parts = $frontendConfig -split "`t"
    Write-Host "      Memory: $($parts[0])" -ForegroundColor White
    Write-Host "      CPU: $($parts[1])" -ForegroundColor White
    Write-Host "      Concurrency: $($parts[2])" -ForegroundColor White
}

# 总结
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "✅ 部署后设置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "服务 URL:" -ForegroundColor Yellow
Write-Host "  Backend:  $backendUrl" -ForegroundColor Cyan
Write-Host "  Frontend: $frontendUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cloud Scheduler 状态:" -ForegroundColor Yellow
Write-Host "  创建: $createdCount 个" -ForegroundColor Green
Write-Host "  已存在: $existsCount 个" -ForegroundColor Yellow
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "1. 访问 Frontend: $frontendUrl" -ForegroundColor Gray
Write-Host "2. 登录系统并测试功能" -ForegroundColor Gray
Write-Host "3. 进入'智能调度'页面查看成本预估" -ForegroundColor Gray
Write-Host "4. 根据账号活跃度应用优化建议" -ForegroundColor Gray
Write-Host ""
Write-Host "成本优化提示:" -ForegroundColor Yellow
Write-Host "- 当前配置: 最低可运行配置 (512Mi/1CPU backend, 256Mi/0.5CPU frontend)" -ForegroundColor Gray
Write-Host "- 预估月成本: `$15-25" -ForegroundColor Green
Write-Host "- 如需更高性能，可手动调整资源配置" -ForegroundColor Gray
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
