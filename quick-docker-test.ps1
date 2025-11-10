# 快速 Docker 测试脚本
Write-Host "================================" -ForegroundColor Cyan
Write-Host "本地 Docker 快速测试" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$IMAGE_NAME = "auto-ski-test"
$CONTAINER_NAME = "auto-ski-test"

# 清理
Write-Host "[1/4] 清理旧容器..." -ForegroundColor Yellow
docker stop $CONTAINER_NAME 2>$null | Out-Null
docker rm $CONTAINER_NAME 2>$null | Out-Null

# 构建
Write-Host "[2/4] 构建镜像 (需要 5-10 分钟)..." -ForegroundColor Yellow
docker build -t $IMAGE_NAME -f Dockerfile . 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 构建失败" -ForegroundColor Red
    exit 1
}
Write-Host "✅ 构建成功" -ForegroundColor Green

# 启动
Write-Host "[3/4] 启动容器..." -ForegroundColor Yellow
docker run -d --name $CONTAINER_NAME -p 8080:8080 -e USE_CLOUD_SQL=False -e DEBUG=False -e "ALLOWED_HOSTS=*" -e PORT=8080 $IMAGE_NAME
Start-Sleep -Seconds 20

# 检查
Write-Host "[4/4] 检查状态..." -ForegroundColor Yellow
$status = docker inspect -f "{{.State.Status}}" $CONTAINER_NAME 2>$null
Write-Host "容器状态: $status" -ForegroundColor $(if ($status -eq "running") { "Green" } else { "Red" })

Write-Host ""
Write-Host "====== 启动日志 ======" -ForegroundColor Cyan
docker logs $CONTAINER_NAME

if ($status -eq "running") {
    Write-Host ""
    Write-Host "====== 健康检查 ======" -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 10 -UseBasicParsing
        Write-Host "✅ 健康检查成功: $($response.StatusCode)" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  健康检查失败，容器可能还在启动中" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "测试 URL: http://localhost:8080/health" -ForegroundColor Cyan
    Write-Host "查看日志: docker logs -f $CONTAINER_NAME" -ForegroundColor Gray
    Write-Host "停止容器: docker stop $CONTAINER_NAME" -ForegroundColor Gray
}
