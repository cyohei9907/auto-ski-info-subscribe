# 本地 Docker 测试脚本
# 用于测试 Cloud Run 部署镜像是否能正常启动

Write-Host "================================" -ForegroundColor Cyan
Write-Host "本地 Docker 部署测试" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 设置变量
$IMAGE_NAME = "auto-ski-info-backend-test"
$CONTAINER_NAME = "auto-ski-test"
$PORT = 8080

# 步骤 1: 清理旧容器和镜像
Write-Host "[1/5] 清理旧容器和镜像..." -ForegroundColor Yellow
docker stop $CONTAINER_NAME 2>$null
docker rm $CONTAINER_NAME 2>$null

# 步骤 2: 构建 Docker 镜像
Write-Host ""
Write-Host "[2/5] 构建 Docker 镜像..." -ForegroundColor Yellow
Write-Host "这可能需要 5-10 分钟..." -ForegroundColor Gray
$buildStart = Get-Date
docker build -t $IMAGE_NAME -f Dockerfile .
$buildEnd = Get-Date
$buildDuration = ($buildEnd - $buildStart).TotalSeconds

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ 构建失败！" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ 构建成功！耗时: $([math]::Round($buildDuration, 2)) 秒" -ForegroundColor Green

# 步骤 3: 检查镜像大小
Write-Host ""
Write-Host "[3/5] 检查镜像信息..." -ForegroundColor Yellow
docker images $IMAGE_NAME

# 步骤 4: 启动容器
Write-Host ""
Write-Host "[4/5] 启动容器..." -ForegroundColor Yellow
Write-Host "环境变量配置:" -ForegroundColor Gray
Write-Host "  - USE_CLOUD_SQL=False" -ForegroundColor Gray
Write-Host "  - DEBUG=False" -ForegroundColor Gray
Write-Host "  - PORT=$PORT" -ForegroundColor Gray

docker run -d --name $CONTAINER_NAME -p ${PORT}:8080 -e USE_CLOUD_SQL=False -e DEBUG=False -e "ALLOWED_HOSTS=*" -e DJANGO_SETTINGS_MODULE=auto_ski_info.settings -e PORT=8080 $IMAGE_NAME

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ 容器启动失败！" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ 容器已启动：$CONTAINER_NAME" -ForegroundColor Green

# 步骤 5: 监控容器启动
Write-Host ""
Write-Host "[5/5] 监控容器启动..." -ForegroundColor Yellow
Write-Host "等待 15 秒查看启动过程..." -ForegroundColor Gray
Start-Sleep -Seconds 15

# 检查容器状态
$status = docker inspect -f "{{.State.Status}}" $CONTAINER_NAME 2>$null

Write-Host ""
Write-Host "====== 容器状态 ======" -ForegroundColor Cyan
Write-Host "状态: $status" -ForegroundColor $(if ($status -eq "running") { "Green" } else { "Red" })

Write-Host ""
Write-Host "====== 容器启动日志 ======" -ForegroundColor Cyan
docker logs $CONTAINER_NAME

if ($status -eq "running") {
    Write-Host ""
    Write-Host "====== 健康检查 ======" -ForegroundColor Cyan
    Write-Host "检查端口 8080 是否响应..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$PORT/health" -TimeoutSec 10 -UseBasicParsing
        Write-Host "✅ 健康检查通过！状态码: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "   响应内容: $($response.Content)" -ForegroundColor Gray
    }
    catch {
        Write-Host "⚠️  健康检查失败: $_" -ForegroundColor Yellow
        Write-Host "   容器可能还在启动中，请稍后手动测试" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "====== 测试完成 ======" -ForegroundColor Cyan
    Write-Host "容器名称: $CONTAINER_NAME" -ForegroundColor White
    Write-Host "端口映射: localhost:$PORT -> container:8080" -ForegroundColor White
    Write-Host ""
    Write-Host "常用命令:" -ForegroundColor Yellow
    Write-Host "  查看日志: docker logs -f $CONTAINER_NAME" -ForegroundColor Gray
    Write-Host "  进入容器: docker exec -it $CONTAINER_NAME sh" -ForegroundColor Gray
    Write-Host "  停止容器: docker stop $CONTAINER_NAME" -ForegroundColor Gray
    Write-Host "  删除容器: docker rm $CONTAINER_NAME" -ForegroundColor Gray
    Write-Host ""
    Write-Host "测试 URL:" -ForegroundColor Yellow
    Write-Host "  健康检查: http://localhost:$PORT/health" -ForegroundColor Gray
    Write-Host "  前端页面: http://localhost:$PORT/" -ForegroundColor Gray
    Write-Host "  API 文档: http://localhost:$PORT/swagger/" -ForegroundColor Gray
    Write-Host "  管理后台: http://localhost:$PORT/admin/" -ForegroundColor Gray
}
