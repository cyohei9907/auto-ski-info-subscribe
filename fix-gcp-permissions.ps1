# GCP 权限修复脚本
# 解决 Cloud Build 部署到 Cloud Run 的权限问题

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "GCP 权限修复脚本" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# 获取项目 ID
$projectId = gcloud config get-value project 2>$null
if (-not $projectId) {
    Write-Host "❌ 错误: 无法获取当前项目 ID" -ForegroundColor Red
    Write-Host "   请先设置项目: gcloud config set project YOUR_PROJECT_ID" -ForegroundColor Yellow
    exit 1
}

Write-Host "当前项目 ID: " -NoNewline
Write-Host $projectId -ForegroundColor Green
Write-Host ""

# 获取项目编号
$projectNumber = gcloud projects describe $projectId --format="value(projectNumber)" 2>$null
Write-Host "项目编号: " -NoNewline
Write-Host $projectNumber -ForegroundColor Green
Write-Host ""

# Cloud Build 服务账号
$cloudBuildSA = "${projectNumber}@cloudbuild.gserviceaccount.com"
$computeSA = "${projectNumber}-compute@developer.gserviceaccount.com"

Write-Host "Cloud Build 服务账号:" -ForegroundColor Cyan
Write-Host "  - Cloud Build: $cloudBuildSA" -ForegroundColor Gray
Write-Host "  - Compute Engine: $computeSA" -ForegroundColor Gray
Write-Host ""

# 需要授予的角色
$roles = @(
    "roles/run.admin",                    # Cloud Run 管理员
    "roles/iam.serviceAccountUser",       # 服务账号用户
    "roles/cloudsql.client",              # Cloud SQL 客户端
    "roles/secretmanager.secretAccessor"  # Secret Manager 访问
)

Write-Host "开始授予权限..." -ForegroundColor Yellow
Write-Host ""

foreach ($role in $roles) {
    Write-Host "授予角色: " -NoNewline
    Write-Host $role -ForegroundColor Cyan
    
    # 授予给 Cloud Build 服务账号
    try {
        gcloud projects add-iam-policy-binding $projectId `
            --member="serviceAccount:$cloudBuildSA" `
            --role=$role `
            --condition=None `
            2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ 已授予给 Cloud Build SA" -ForegroundColor Green
        }
        else {
            Write-Host "  ⚠️  授予 Cloud Build SA 失败" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  ❌ 错误: $_" -ForegroundColor Red
    }
    
    # 授予给 Compute Engine 服务账号
    try {
        gcloud projects add-iam-policy-binding $projectId `
            --member="serviceAccount:$computeSA" `
            --role=$role `
            --condition=None `
            2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ 已授予给 Compute Engine SA" -ForegroundColor Green
        }
        else {
            Write-Host "  ⚠️  授予 Compute Engine SA 失败" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  ❌ 错误: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

# 启用必要的 API
Write-Host "检查必要的 API..." -ForegroundColor Yellow
Write-Host ""

$apis = @(
    "run.googleapis.com",           # Cloud Run
    "cloudbuild.googleapis.com",    # Cloud Build
    "secretmanager.googleapis.com", # Secret Manager
    "sqladmin.googleapis.com",      # Cloud SQL Admin
    "cloudscheduler.googleapis.com" # Cloud Scheduler
)

foreach ($api in $apis) {
    Write-Host "检查 API: " -NoNewline
    Write-Host $api -ForegroundColor Cyan
    
    $enabled = gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>$null
    
    if ($enabled) {
        Write-Host "  ✅ 已启用" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠️  未启用，正在启用..." -ForegroundColor Yellow
        try {
            gcloud services enable $api 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ 启用成功" -ForegroundColor Green
            }
            else {
                Write-Host "  ❌ 启用失败" -ForegroundColor Red
            }
        }
        catch {
            Write-Host "  ❌ 错误: $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "✅ 权限配置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 等待 30-60 秒让权限生效" -ForegroundColor Gray
Write-Host "2. 重新运行部署命令:" -ForegroundColor Gray
Write-Host "   gcloud builds submit --config=cloudbuild.yaml" -ForegroundColor Cyan
Write-Host ""
Write-Host "如果仍然失败，请检查:" -ForegroundColor Yellow
Write-Host "- Cloud SQL 实例是否存在并正在运行" -ForegroundColor Gray
Write-Host "- Secret Manager 中的密钥是否都已创建" -ForegroundColor Gray
Write-Host "- 服务账号名称是否正确" -ForegroundColor Gray
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
