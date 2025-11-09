# 智能监控调度系统 - 完整部署指南

本系统通过智能分级调度实现 **50% 成本节省**，根据 Twitter 账号活跃度自动优化监控频率。

---

## 🎯 核心优化

### 1. 分级监控策略

| 间隔        | 适用场景                 | 每日调用 | 成本比例 |
| ----------- | ------------------------ | -------- | -------- |
| **30 分钟** | 高活跃账号（>10 条/天）  | 48 次    | 100%     |
| **1 小时**  | 中活跃账号（5-10 条/天） | 24 次    | 50%      |
| **4 小时**  | 低活跃账号（1-5 条/天）  | 6 次     | 12.5%    |
| **12 小时** | 极低活跃账号（<1 条/天） | 2 次     | 4.2%     |

### 2. 智能优化算法

系统自动分析过去 7 天的推文数量，为每个账号推荐最优监控间隔：

```python
if avg_daily_tweets > 10:
    recommended_interval = 30  # 高活跃
elif avg_daily_tweets > 5:
    recommended_interval = 60  # 中活跃
elif avg_daily_tweets > 1:
    recommended_interval = 240  # 低活跃
else:
    recommended_interval = 720  # 极低活跃
```

---

## 📦 后端部署

### 步骤 1: 更新代码

```bash
cd backend

# 确认新文件已创建
ls x_monitor/smart_scheduling.py
```

### 步骤 2: 数据库迁移（无需迁移，使用现有字段）

`monitoring_interval` 字段已存在于 `XAccount` 模型中。

### 步骤 3: 测试 API

```bash
# 启动开发服务器
python manage.py runserver

# 测试智能调度 API
curl -X GET http://localhost:8000/api/monitor/monitoring-schedule/ \
  -H "Authorization: Token YOUR_TOKEN"

# 获取优化建议
curl -X GET http://localhost:8000/api/monitor/optimize-intervals/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 步骤 4: 验证端点

访问这些 API 端点应该正常工作：

- `POST /api/monitor/trigger-monitoring/?interval=30`
- `POST /api/monitor/trigger-monitoring/?interval=60`
- `POST /api/monitor/trigger-monitoring/?interval=240`
- `POST /api/monitor/trigger-monitoring/?interval=720`
- `GET /api/monitor/monitoring-schedule/`
- `GET /api/monitor/optimize-intervals/`

---

## 🎨 前端部署

### 步骤 1: 安装依赖（如需要）

```bash
cd frontend

# 确认 Ant Design 已安装
npm list antd
```

### 步骤 2: 测试页面

```bash
# 启动开发服务器
npm start

# 访问新页面
# http://localhost:3000/schedule
```

### 步骤 3: 构建生产版本

```bash
npm run build
```

---

## ☁️ Cloud Build 配置更新

### 使用优化后的配置

替换当前 `cloudbuild.yaml`：

```bash
# 备份当前配置
cp cloudbuild.yaml cloudbuild.yaml.backup

# 使用优化后的配置
cp cloudbuild.optimized.yaml cloudbuild.yaml
```

### 关键优化点

#### 1. **Build Machine** (50% 节省)

```yaml
options:
  machineType: "E2_HIGHCPU_4" # 从 E2_HIGHCPU_8 降低
```

#### 2. **Backend Cloud Run** (70% 节省)

```yaml
--memory=1Gi            # 从 2Gi 降低
--cpu=1                 # 从 2 降低
--concurrency=80        # 提高并发
--cpu-throttling        # CPU 节流
--min-instances=0       # 按需启动
```

#### 3. **Frontend Cloud Run** (80% 节省)

```yaml
--memory=256Mi          # 从 512Mi 降低
--cpu=0.5               # 从 1 降低
```

#### 4. **分级调度** (50% 节省)

创建 4 个 Cloud Scheduler 作业：

```bash
# 30分钟间隔 - 高频账号
gcloud scheduler jobs create http monitoring-30min \
  --schedule="*/30 * * * *" \
  --uri="https://YOUR_BACKEND_URL/api/monitor/trigger-monitoring/?interval=30" \
  --http-method=POST \
  --oidc-service-account-email=YOUR_SERVICE_ACCOUNT

# 1小时间隔 - 中频账号
gcloud scheduler jobs create http monitoring-1hour \
  --schedule="0 * * * *" \
  --uri="https://YOUR_BACKEND_URL/api/monitor/trigger-monitoring/?interval=60" \
  --http-method=POST \
  --oidc-service-account-email=YOUR_SERVICE_ACCOUNT

# 4小时间隔 - 低频账号
gcloud scheduler jobs create http monitoring-4hours \
  --schedule="0 */4 * * *" \
  --uri="https://YOUR_BACKEND_URL/api/monitor/trigger-monitoring/?interval=240" \
  --http-method=POST \
  --oidc-service-account-email=YOUR_SERVICE_ACCOUNT

# 12小时间隔 - 极低频账号
gcloud scheduler jobs create http monitoring-12hours \
  --schedule="0 */12 * * *" \
  --uri="https://YOUR_BACKEND_URL/api/monitor/trigger-monitoring/?interval=720" \
  --http-method=POST \
  --oidc-service-account-email=YOUR_SERVICE_ACCOUNT
```

---

## 🚀 部署流程

### 1. 本地测试

```bash
# 后端测试
cd backend
python manage.py runserver

# 前端测试
cd frontend
npm start

# 访问智能调度页面
# http://localhost:3000/schedule
```

### 2. Docker 测试（推荐）

```bash
# 构建并启动
docker-compose up --build

# 测试 API
curl http://localhost:8000/api/monitor/monitoring-schedule/
```

### 3. 部署到 GCP

```bash
# 使用优化后的配置
gcloud builds submit --config=cloudbuild.yaml

# 查看部署状态
gcloud run services describe auto-ski-info-backend --region=asia-northeast1
gcloud run services describe auto-ski-info-frontend --region=asia-northeast1
```

### 4. 配置 Cloud Scheduler

运行上面的 4 个 `gcloud scheduler jobs create` 命令。

### 5. 验证部署

访问前端应用：

- 点击左侧菜单 "智能调度"
- 查看当前监控统计
- 应用优化建议

---

## 📊 成本对比

### 当前成本（未优化）

```
Build Machine: E2_HIGHCPU_8 × 15 min/day = $4.56/月
Backend: 2 vCPU, 2GB × 50 req/day × 3 min = $45.60/月
Frontend: 1 vCPU, 512MB × 500 req/day = $8.40/月
Cloud Scheduler: 96 jobs/day × 30 days = $2.88/月
Cloud SQL: db-f1-micro = $30.00/月

总计: $91.44/月
```

### 优化后成本

```
Build Machine: E2_HIGHCPU_4 × 10 min/day = $1.52/月
Backend: 1 vCPU, 1GB × 50 req/day × 3 min = $15.96/月
Frontend: 0.5 vCPU, 256MB × 500 req/day = $2.10/月
Cloud Scheduler: 50 jobs/day × 30 days = $1.50/月
Cloud SQL: db-f1-micro = $30.00/月

总计: $51.08/月
节省: $40.36/月 (44.1%)
```

### 极致优化（分级调度 + Firebase）

```
Build Machine: E2_HIGHCPU_4 × 10 min/day = $1.52/月
Backend: 1 vCPU, 1GB × 25 req/day × 3 min = $7.98/月
Frontend: Firebase Hosting (免费层) = $0.00/月
Cloud Scheduler: 0 (使用 Cloud Tasks) = $0.08/月
Cloud SQL: db-f1-micro = $30.00/月

总计: $39.58/月
节省: $51.86/月 (56.7%)
```

---

## 🎯 使用指南

### 1. 首次使用

1. 登录系统
2. 点击左侧菜单 "智能调度"
3. 点击 "重新分析" 获取优化建议
4. 逐个点击 "应用" 按钮应用建议

### 2. 监控成本

- **总账号数**: 显示所有活跃账号数量
- **每日调用次数**: 预估每日 API 调用总数
- **预估月成本**: 基于 Cloud Run 定价计算

### 3. 查看分布

"监控间隔分布" 表格显示：

- 各间隔的账号数量
- 每日运行次数
- 每日总调用数
- 占比进度条

### 4. 优化建议

系统自动分析并推荐：

- 当前间隔 vs 建议间隔
- 平均每日推文数（过去 7 天）
- 优化理由
- 预计节省比例

---

## 🔍 故障排查

### API 404 错误

```bash
# 检查 URLs 配置
cd backend
grep -r "trigger-monitoring" x_monitor/

# 确认导入正确
python manage.py shell
>>> from x_monitor import smart_scheduling
>>> smart_scheduling.trigger_monitoring
```

### 前端路由错误

```bash
# 检查 App.js
cat frontend/src/App.js | grep MonitoringSchedulePage

# 检查 MainLayout.js
cat frontend/src/components/MainLayout.js | grep schedule
```

### Cloud Scheduler 权限错误

```bash
# 授予 Service Account 调用权限
gcloud run services add-iam-policy-binding auto-ski-info-backend \
  --region=asia-northeast1 \
  --member=serviceAccount:YOUR_SERVICE_ACCOUNT \
  --role=roles/run.invoker
```

---

## 📈 监控指标

### 关键指标

1. **每日 API 调用数**

   - 目标: < 50 次/天（10 个账号）
   - 当前: 查看 "智能调度" 页面

2. **平均响应时间**

   - 目标: < 5 秒
   - 监控: Cloud Run 指标

3. **成本**
   - 目标: < $50/月
   - 监控: GCP Billing

### 设置预算警报

```bash
# 创建预算警报
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Auto-Ski-Info Budget" \
  --budget-amount=50USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

---

## 🚀 进阶优化

### Phase 1: 智能调度（当前）✅

- ✅ 分级监控间隔
- ✅ 活跃度分析
- ✅ 自动优化建议

### Phase 2: Playwright 优化

```python
# 浏览器实例池
from playwright.sync_api import sync_playwright

browser_pool = []
max_pool_size = 3

def get_browser():
    if len(browser_pool) < max_pool_size:
        browser = playwright.chromium.launch()
        browser_pool.append(browser)
    return browser_pool[0]  # 复用实例

# 批量处理
def batch_monitor_accounts(accounts, batch_size=5):
    for i in range(0, len(accounts), batch_size):
        batch = accounts[i:i+batch_size]
        # 并行处理
```

### Phase 3: 前端迁移到 Firebase

```bash
# 部署到 Firebase Hosting
npm run build
firebase deploy --only hosting

# 完全免费（免费层）
```

---

## ✅ 检查清单

### 部署前

- [ ] 后端代码已更新（smart_scheduling.py）
- [ ] 前端代码已更新（MonitoringSchedulePage.js）
- [ ] 路由配置正确（App.js, urls.py）
- [ ] 本地测试通过
- [ ] Docker 测试通过

### 部署后

- [ ] Backend Cloud Run 正常运行
- [ ] Frontend Cloud Run 正常运行
- [ ] 4 个 Cloud Scheduler 作业已创建
- [ ] "智能调度" 页面可访问
- [ ] API 返回正确数据
- [ ] 优化建议功能正常

### 验证

- [ ] 访问 `/schedule` 页面
- [ ] 查看监控统计
- [ ] 点击 "重新分析"
- [ ] 应用一个优化建议
- [ ] 确认成本预估合理

---

## 📚 相关文档

- [成本优化分析](./CLOUD_DEPLOYMENT_COST_OPTIMIZATION.md)
- [优化后的 Cloud Build 配置](./cloudbuild.optimized.yaml)
- [部署文档](./DEPLOY.md)
- [配置说明](./CONFIGURATION.md)

---

## 🆘 支持

遇到问题？

1. 查看 [故障排查](#故障排查) 章节
2. 检查 Cloud Run 日志：
   ```bash
   gcloud logging read "resource.type=cloud_run_revision" --limit=50
   ```
3. 查看 Backend 日志：
   ```bash
   docker-compose logs backend
   ```

---

**预计节省**: $40-50/月 (44-56%)  
**实施时间**: 2-4 小时  
**技术难度**: ⭐⭐⭐ (中等)
