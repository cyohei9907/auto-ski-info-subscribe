# 修复 Secret Manager 权限
# 为 Cloud Run 服务账号授予访问所有密钥的权限

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Secret Manager 权限修复脚本" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# 获取项目信息
$projectId = gcloud config get-value project 2>$null
$projectNumber = gcloud projects describe $projectId --format="value(projectNumber)" 2>$null

Write-Host "项目 ID: " -NoNewline
Write-Host $projectId -ForegroundColor Green
Write-Host "项目编号: " -NoNewline
Write-Host $projectNumber -ForegroundColor Green
Write-Host ""

# 服务账号
$computeSA = "${projectNumber}-compute@developer.gserviceaccount.com"
Write-Host "服务账号: " -NoNewline
Write-Host $computeSA -ForegroundColor Cyan
Write-Host ""

# 所有需要访问的密钥
$secrets = @(
    "DATABASE_PASSWORD",
    "AI_API_KEY_GOOGLE"
)

Write-Host "开始授予密钥访问权限..." -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($secret in $secrets) {
    Write-Host "处理密钥: " -NoNewline
    Write-Host $secret -ForegroundColor Cyan
    
    try {
        # 为每个密钥单独授予访问权限
        $output = gcloud secrets add-iam-policy-binding $secret `
            --member="serviceAccount:$computeSA" `
            --role="roles/secretmanager.secretAccessor" `
            2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ 成功" -ForegroundColor Green
            $successCount++
        }
        else {
            Write-Host "  ⚠️  失败: $output" -ForegroundColor Yellow
            $failCount++
        }
    }
    catch {
        Write-Host "  ❌ 错误: $_" -ForegroundColor Red
        $failCount++
    }
    
    Write-Host ""
}

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "完成!" -ForegroundColor Green
Write-Host "  成功: $successCount" -ForegroundColor Green
Write-Host "  失败: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Yellow" } else { "Green" })
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "✅ 所有权限配置成功!" -ForegroundColor Green
    Write-Host ""
    Write-Host "现在可以重新部署:" -ForegroundColor Yellow
    Write-Host "  gcloud builds submit --config=cloudbuild.minimal.yaml" -ForegroundColor Cyan
}
else {
    Write-Host "⚠️  部分密钥权限配置失败" -ForegroundColor Yellow
    Write-Host "   请检查这些密钥是否存在:" -ForegroundColor Gray
    Write-Host "   gcloud secrets list" -ForegroundColor Cyan
}
