# Cloud Run 部署优化说明

## 问题分析

### 原始错误

```
ERROR: The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable within the allocated timeout.
```

### 根本原因

1. **资源配置不足**：2Gi 内存 + 2 CPU 对于包含 Playwright 的 Django 应用不够
2. **启动超时**：默认 300 秒超时不足以完成：
   - Cloud SQL 连接等待（10s）
   - 数据库迁移（可能需要 30-60s）
   - 静态文件收集（10-20s）
   - Playwright 初始化（20-30s）
   - Nginx + Gunicorn 启动（5-10s）
3. **Supervisor 启动慢**：之前直接启动 supervisord，跳过了数据库迁移步骤

## 优化方案

### 1. 提升资源配置（已完成）

**cloudbuild.yaml 修改**：

```yaml
--memory: "2Gi" → "4Gi"  # 内存翻倍
--cpu: "2" → "4"          # CPU 翻倍
--timeout: "300" → "600"  # 超时时间翻倍
```

**成本估算**（asia-northeast1 区域）：

- 原配置：2 vCPU + 2Gi = $0.000024/秒 ≈ $1.73/天（持续运行）
- 新配置：4 vCPU + 4Gi = $0.000048/秒 ≈ $3.46/天（持续运行）
- **实际成本**：由于设置了 `--min-instances=0`，无请求时不计费，实际成本会低很多

### 2. 优化启动流程（已完成）

**Dockerfile 修改**：

```dockerfile
# 创建启动脚本，按顺序执行：
CMD ["/app/startup.sh"]

启动脚本内容：
1. Cloud SQL 连接等待（10s）
2. 数据库迁移（migrate）
3. 用户初始化（init_users.py）
4. 静态文件收集（collectstatic）
5. 启动 Supervisor（Nginx + Gunicorn）
```

**supervisord.combined.conf 修改**：

```ini
# Backend 直接启动 Gunicorn（不再调用 entrypoint.sh）
command=/usr/local/bin/gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 2 --timeout 600 --graceful-timeout 60 auto_ski_info.wsgi:application
```

### 3. Gunicorn 工作进程优化

**配置说明**：

- `--workers 2`：2 个工作进程（之前是 3 个，减少内存占用）
- `--threads 2`：每个进程 2 个线程（提升并发能力）
- `--timeout 600`：请求超时 10 分钟（适应 Playwright 爬虫）
- `--graceful-timeout 60`：优雅关闭超时 1 分钟

**工作进程计算公式**：

```
推荐 workers = (2 × CPU核心数) + 1
4 CPU → 推荐 9 workers（但会占用大量内存）
折中方案：2 workers × 2 threads = 4 并发连接（足够 API 使用）
```

### 4. 健康检查端点

**nginx.combined.conf 已配置**：

```nginx
location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}
```

- Cloud Run 会定期访问此端点检查服务健康状态
- 不依赖后端 Django（Nginx 直接响应）
- 响应速度快，不会触发超时

## 部署步骤

### 1. 提交代码

```powershell
git add .
git commit -m "优化：提升 Cloud Run 资源配置（4CPU+4Gi），优化启动流程"
git push
```

### 2. 监控部署日志

访问 Cloud Build 控制台：
https://console.cloud.google.com/cloud-build/builds?project=gen-lang-client-0543160602

关键日志检查点：

- ✅ Step #0: Build Combined Image（约 5-8 分钟）
- ✅ Step #1-2: Push Backend（约 1-2 分钟）
- ✅ Step #3: Deploy Backend（约 3-5 分钟）
  - 关注 "Creating Revision" 阶段
  - 应该看到 "done" 而不是 "failed"
- ✅ Step #4-5: Setup Scheduler（约 30 秒）

### 3. 验证部署结果

#### 3.1 健康检查

```bash
curl https://auto-ski-info-backend-[hash]-asia-northeast1.a.run.app/health
# 预期输出：healthy
```

#### 3.2 前端访问

浏览器打开：`https://auto-ski-info-backend-[hash]-asia-northeast1.a.run.app/`

- 应该看到 React 前端界面
- 检查浏览器控制台无 404 错误（CSS/JS 加载成功）

#### 3.3 API 测试

```bash
# 获取监控账号列表
curl https://auto-ski-info-backend-[hash]-asia-northeast1.a.run.app/api/monitor/accounts/
```

#### 3.4 Admin 面板

访问：`https://auto-ski-info-backend-[hash]-asia-northeast1.a.run.app/admin`

- 使用 `init_users.py` 创建的管理员账号登录

### 4. 查看容器日志（如果还有问题）

#### 4.1 Cloud Run 日志

https://console.cloud.google.com/logs/query?project=gen-lang-client-0543160602

过滤器：

```
resource.type="cloud_run_revision"
resource.labels.service_name="auto-ski-info-backend"
```

关键日志：

```
Starting initialization...
Waiting for Cloud SQL to be ready...
Running database migrations...
Operations to perform: ...
Initializing users...
Collecting static files...
Starting Supervisor...
```

#### 4.2 Supervisor 日志

查看 Nginx 和 Backend 进程状态：

```bash
# 进入容器（如果部署成功）
gcloud run services exec auto-ski-info-backend --region=asia-northeast1 --command=/bin/bash

# 查看 Supervisor 状态
supervisorctl status
# 预期输出：
# backend    RUNNING   pid xxx, uptime x:xx:xx
# nginx      RUNNING   pid xxx, uptime x:xx:xx
```

## 成本优化建议

### 当前配置

- **资源**：4 CPU + 4Gi 内存
- **扩展**：0-10 实例（无请求时缩容到 0）
- **预估成本**（低流量）：$10-20/月

### 进一步优化（可选）

如果部署成功后发现资源使用率低，可以调整：

```yaml
# 选项 1：保守配置（适合低流量）
--memory: "3Gi"
--cpu: "2"
--workers: 1
--threads: 2

# 选项 2：平衡配置（当前推荐）
--memory: "4Gi"
--cpu: "4"
--workers: 2
--threads: 2

# 选项 3：高性能配置（适合高并发）
--memory: "8Gi"
--cpu: "4"
--workers: 4
--threads: 4
```

### 监控指标

通过 Cloud Monitoring 观察：

- **CPU 利用率**：应该在 30%-70% 之间
- **内存利用率**：应该在 50%-80% 之间
- **请求延迟**：P95 应该小于 2 秒
- **冷启动时间**：应该小于 60 秒

如果 CPU < 20% 或内存 < 40%，可以考虑降低配置。

## 故障排查

### 问题 1：容器仍然无法启动

**检查点**：

1. Cloud SQL 连接字符串是否正确
2. DATABASE_PASSWORD 和 AI_API_KEY_GOOGLE 密钥是否存在
3. 数据库迁移是否有错误

**解决方案**：
查看完整日志，找到具体错误信息。

### 问题 2：502 Bad Gateway

**原因**：Nginx 启动了，但 Backend 没有启动
**检查**：

```bash
# 查看 Backend 日志
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~'backend'" --limit 50
```

### 问题 3：前端加载失败（404）

**原因**：前端静态文件未正确复制
**检查**：

```bash
# 进入容器验证文件
gcloud run services exec auto-ski-info-backend --region=asia-northeast1 --command=/bin/sh
ls -la /usr/share/nginx/html/
```

### 问题 4：数据库连接失败

**检查**：

1. Cloud SQL 实例是否正在运行
2. 环境变量配置是否正确：
   - CLOUD_SQL_CONNECTION_NAME
   - CLOUD_DB_NAME
   - CLOUD_DB_USER
3. Secret Manager 中的 DATABASE_PASSWORD 是否正确

## 下一步建议

### 部署成功后

1. ✅ 测试所有 API 端点
2. ✅ 验证 Cloud Scheduler 定时任务
3. ✅ 测试 Playwright 爬虫功能
4. ✅ 配置监控告警（CPU/内存/错误率）

### 持续优化

1. 根据实际使用情况调整资源配置
2. 考虑使用 Cloud CDN 加速前端静态文件
3. 设置 `--min-instances=1` 避免冷启动（会增加成本）
4. 配置自动扩缩容策略（基于 CPU 或请求数）

---

**最后更新**：2025-11-10
**配置版本**：v2.0（优化版）
