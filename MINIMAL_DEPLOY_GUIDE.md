# 🚀 Cloud Build 最低配置快速部署指南

## 💰 成本对比

| 配置         | Memory        | CPU     | 月成本     | 节省    |
| ------------ | ------------- | ------- | ---------- | ------- |
| **标准配置** | 2Gi + 512Mi   | 2 + 1   | $80-130    | -       |
| **优化配置** | 1Gi + 256Mi   | 1 + 0.5 | $26-41     | 68%     |
| **最低配置** | 512Mi + 256Mi | 1 + 0.5 | **$15-25** | **81%** |

## ⚡ 一键部署（5 分钟）

### 步骤 1: 确保权限正确

```powershell
# 运行权限修复脚本
.\fix-gcp-permissions.ps1

# 等待 30 秒
Start-Sleep -Seconds 30
```

### 步骤 2: 使用最低配置部署

```powershell
# 使用最低配置文件部署
gcloud builds submit --config=cloudbuild.minimal.yaml
```

### 步骤 3: 部署后配置

```powershell
# 自动配置 Frontend URL 和 Cloud Scheduler
.\post-deploy-setup.ps1
```

**完成！** 🎉

---

## 📋 详细步骤

### 前置要求

确保以下密钥已在 Secret Manager 中创建：

```bash
# 检查密钥
gcloud secrets list

# 应该看到这些密钥:
# - AI_API_KEY_GOOGLE
# - DATABASE_PASSWORD
# - X_API_KEY
# - X_API_SECRET
# - X_ACCESS_TOKEN
# - X_ACCESS_TOKEN_SECRET
# - X_BEARER_TOKEN
```

如果缺少密钥，创建它们：

```bash
echo -n "your-value" | gcloud secrets create AI_API_KEY_GOOGLE --data-file=-
echo -n "your-value" | gcloud secrets create DATABASE_PASSWORD --data-file=-
# ... 其他密钥
```

### 部署流程

#### 1. 首次部署

```powershell
# 1.1 修复权限
.\fix-gcp-permissions.ps1

# 1.2 等待权限生效
Start-Sleep -Seconds 60

# 1.3 开始部署
gcloud builds submit --config=cloudbuild.minimal.yaml
```

**部署时间**: 约 8-12 分钟

#### 2. 部署后配置

```powershell
# 2.1 运行配置脚本
.\post-deploy-setup.ps1
```

这个脚本会自动：

- ✅ 获取 Backend URL
- ✅ 更新 Frontend 环境变量
- ✅ 创建 4 个智能分级调度器
- ✅ 测试服务连接
- ✅ 显示资源配置

#### 3. 验证部署

```powershell
# 获取服务 URL
$backendUrl = gcloud run services describe auto-ski-info-backend --region=asia-northeast1 --format="value(status.url)"
$frontendUrl = gcloud run services describe auto-ski-info-frontend --region=asia-northeast1 --format="value(status.url)"

Write-Host "Backend: $backendUrl"
Write-Host "Frontend: $frontendUrl"

# 在浏览器中打开
Start-Process $frontendUrl
```

---

## 🔧 最低配置详情

### Backend (Django + Celery)

```yaml
Memory: 512Mi # 最低可用 (vs 2Gi 标准)
CPU: 1 # 单核 (vs 2 核标准)
Concurrency: 80 # 高并发减少实例数
Min Instances: 0 # 无流量时缩减到 0
Max Instances: 3 # 限制最大成本
CPU Throttling: Yes # 空闲时节能
CPU Boost: Yes # 启动时加速
```

**适用场景**:

- ✅ 中小规模应用 (< 100 个账号)
- ✅ 低频监控 (每小时或更少)
- ✅ 开发/测试环境
- ⚠️ 高并发场景可能需要增加资源

### Frontend (React SPA)

```yaml
Memory: 256Mi # 最低可用 (vs 512Mi 标准)
CPU: 0.5 # 半核 (vs 1 核标准)
Concurrency: 80
Min Instances: 0
Max Instances: 2
CPU Throttling: Yes
```

### Build Machine

```yaml
Machine Type: E2_HIGHCPU_4 # vs E2_HIGHCPU_8 标准
Docker Cache: Enabled # 加速构建
```

---

## 📊 性能预期

### 响应时间

| 场景     | 最低配置 | 标准配置 |
| -------- | -------- | -------- |
| 冷启动   | 3-5 秒   | 2-3 秒   |
| 热请求   | < 200ms  | < 100ms  |
| 推文抓取 | 5-10 秒  | 3-5 秒   |
| AI 分析  | 2-5 秒   | 1-3 秒   |

### 并发能力

- **Backend**: 80 并发 × 3 实例 = 240 并发请求
- **Frontend**: 80 并发 × 2 实例 = 160 并发请求

对于大多数个人/小型团队项目完全足够。

---

## 🔄 后续调整

### 如果性能不足

```bash
# 增加 Backend 内存和 CPU
gcloud run services update auto-ski-info-backend \
    --region=asia-northeast1 \
    --memory=1Gi \
    --cpu=2

# 增加 Frontend 内存
gcloud run services update auto-ski-info-frontend \
    --region=asia-northeast1 \
    --memory=512Mi
```

### 如果需要更快的冷启动

```bash
# 设置最小实例数 (会增加成本)
gcloud run services update auto-ski-info-backend \
    --region=asia-northeast1 \
    --min-instances=1
```

---

## 💡 成本优化建议

### 1. 使用智能分级调度

不要让所有账号都用 30 分钟间隔：

- 高活跃账号: 30 分钟
- 中活跃账号: 1 小时
- 低活跃账号: 4 小时
- 极低活跃账号: 12 小时

**节省**: 40-60%

### 2. 定期清理旧数据

```sql
-- 删除 30 天前的推文
DELETE FROM x_monitor_tweet WHERE posted_at < NOW() - INTERVAL '30 days';
```

### 3. 优化数据库

使用 Cloud SQL 的 Serverless 版本或降低实例大小：

```bash
# 检查当前配置
gcloud sql instances describe ai-project-database

# 如果是 db-f1-micro，已经是最低配置
# 如果更高，可以降级
gcloud sql instances patch ai-project-database --tier=db-f1-micro
```

---

## 🆘 故障排查

### 问题 1: 内存不足 (OOM)

**症状**: 容器频繁重启，日志显示 "Memory limit exceeded"

**解决**:

```bash
gcloud run services update auto-ski-info-backend \
    --memory=1Gi \
    --region=asia-northeast1
```

### 问题 2: 响应超时

**症状**: 请求返回 504 Gateway Timeout

**解决**:

```bash
# 增加超时时间
gcloud run services update auto-ski-info-backend \
    --timeout=600 \
    --region=asia-northeast1

# 或增加 CPU
gcloud run services update auto-ski-info-backend \
    --cpu=2 \
    --region=asia-northeast1
```

### 问题 3: 冷启动太慢

**症状**: 首次请求等待 5-10 秒

**解决**:

```bash
# 设置最小实例 (增加成本)
gcloud run services update auto-ski-info-backend \
    --min-instances=1 \
    --region=asia-northeast1
```

---

## 📈 监控成本

### 查看实时成本

```bash
# GCP 控制台
# Billing > Reports > 按服务过滤

# 或使用 CLI
gcloud billing accounts list
gcloud billing accounts describe YOUR_BILLING_ACCOUNT
```

### 设置预算警报

```bash
gcloud billing budgets create \
    --billing-account=YOUR_BILLING_ACCOUNT \
    --display-name="Auto-Ski-Info Budget" \
    --budget-amount=30USD \
    --threshold-rule=percent=50 \
    --threshold-rule=percent=90 \
    --threshold-rule=percent=100
```

---

## ✅ 部署检查清单

- [ ] 权限已修复 (`fix-gcp-permissions.ps1`)
- [ ] Secret Manager 密钥已创建
- [ ] Cloud SQL 实例正在运行
- [ ] 部署成功完成 (`cloudbuild.minimal.yaml`)
- [ ] 部署后配置已运行 (`post-deploy-setup.ps1`)
- [ ] Frontend 可以访问
- [ ] Backend API 响应正常
- [ ] Cloud Scheduler 已创建
- [ ] 智能调度页面功能正常

---

## 🎯 总结

**最低配置适合**:

- ✅ 个人项目
- ✅ 小型团队 (< 10 人)
- ✅ 开发/测试环境
- ✅ 预算有限的场景
- ✅ 中小规模数据 (< 100 账号, < 1000 推文/天)

**月成本**: **$15-25** (vs $80-130 标准配置)

**性能**: 对于大多数场景完全够用 ✅

---

开始部署吧！🚀
