# GCP 部署权限问题修复指南

## 🔴 错误信息

```
ERROR: (gcloud.run.deploy) [PROJECT_NUMBER-compute@developer.gserviceaccount.com]
does not have permission to access namespaces instance [PROJECT_ID]
(or it may not exist): Permission 'iam.serviceaccounts.actAs' denied on
service account default-service-account@PROJECT_ID.iam.gserviceaccount.com
(or it may not exist).
```

## 🎯 问题根因

Cloud Build 的默认服务账号没有足够的权限来：

1. 部署到 Cloud Run
2. 访问 Secret Manager
3. 连接 Cloud SQL
4. 模拟其他服务账号

## ✅ 解决方案

### 方案 1: 自动修复（推荐）⭐

运行自动修复脚本：

#### Windows (PowerShell)

```powershell
.\fix-gcp-permissions.ps1
```

#### macOS/Linux (bash)

```bash
chmod +x fix-gcp-permissions.sh
./fix-gcp-permissions.sh
```

等待 30-60 秒后重新部署：

```bash
gcloud builds submit --config=cloudbuild.yaml
```

---

### 方案 2: 手动修复

#### 步骤 1: 获取项目信息

```bash
# 获取项目 ID
PROJECT_ID=$(gcloud config get-value project)
echo "项目 ID: $PROJECT_ID"

# 获取项目编号
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
echo "项目编号: $PROJECT_NUMBER"

# Cloud Build 服务账号
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Cloud Build SA: $CLOUD_BUILD_SA"
echo "Compute Engine SA: $COMPUTE_SA"
```

#### 步骤 2: 授予必要权限

```bash
# 授予 Cloud Run 管理员角色
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/run.admin"

# 授予服务账号用户角色（允许模拟其他服务账号）
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/iam.serviceAccountUser"

# 授予 Cloud SQL 客户端角色
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/cloudsql.client"

# 授予 Secret Manager 访问角色
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/secretmanager.secretAccessor"
```

#### 步骤 3: 启用必要的 API

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
```

#### 步骤 4: 等待并重试

```bash
# 等待 30-60 秒让权限生效
sleep 60

# 重新部署
gcloud builds submit --config=cloudbuild.yaml
```

---

### 方案 3: 简化配置（如果方案 1 和 2 都失败）

修改 `cloudbuild.yaml`，移除自定义服务账号配置。

**已完成** ✅：我已经移除了 backend 部署中的 `--service-account` 参数。

如果 Cloud Scheduler 创建仍然失败，可以手动创建：

```bash
# 获取 backend URL
BACKEND_URL=$(gcloud run services describe auto-ski-info-backend \
    --region=asia-northeast1 \
    --format="value(status.url)")

# 创建 Cloud Scheduler 作业（不使用 OIDC）
gcloud scheduler jobs create http monitor-x-accounts \
    --schedule="*/15 * * * *" \
    --uri="${BACKEND_URL}/api/monitor/trigger-monitoring/" \
    --http-method=POST \
    --location=asia-northeast1 \
    --time-zone=Asia/Tokyo
```

---

## 🔍 验证权限

### 检查服务账号权限

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# 查看 Cloud Build 服务账号的所有角色
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
```

### 检查 API 是否启用

```bash
gcloud services list --enabled | grep -E "run|build|secret|sql|scheduler"
```

### 检查 Secret Manager 密钥

```bash
# 列出所有密钥
gcloud secrets list

# 验证密钥值（显示前 20 个字符）
gcloud secrets versions access latest --secret=AI_API_KEY_GOOGLE | head -c 20
gcloud secrets versions access latest --secret=DATABASE_PASSWORD | head -c 20
```

---

## 📋 必需的 IAM 角色

| 角色                                 | 用途                      | 必需  |
| ------------------------------------ | ------------------------- | ----- |
| `roles/run.admin`                    | 部署和管理 Cloud Run 服务 | ✅ 是 |
| `roles/iam.serviceAccountUser`       | 模拟其他服务账号          | ✅ 是 |
| `roles/cloudsql.client`              | 连接 Cloud SQL            | ✅ 是 |
| `roles/secretmanager.secretAccessor` | 访问 Secret Manager       | ✅ 是 |

---

## 🆘 常见问题

### Q1: 权限已授予但仍然失败

**A**: 等待时间不够，IAM 权限需要 30-60 秒才能生效。

```bash
# 等待 1 分钟
sleep 60

# 重试
gcloud builds submit --config=cloudbuild.yaml
```

### Q2: "Service account does not exist" 错误

**A**: 服务账号名称配置错误。

检查 `cloudbuild.yaml` 中的 `substitutions` 部分：

```yaml
substitutions:
  _SERVICE_ACCOUNT: "default-service-account@${PROJECT_ID}.iam.gserviceaccount.com"
```

确保该服务账号存在：

```bash
gcloud iam service-accounts list | grep default-service-account
```

如果不存在，创建它：

```bash
gcloud iam service-accounts create default-service-account \
    --display-name="Default Service Account"
```

或者直接移除 `--service-account` 参数，使用 Cloud Run 默认服务账号。

### Q3: Cloud SQL 连接失败

**A**: 检查 Cloud SQL 实例名称和状态。

```bash
# 列出所有 Cloud SQL 实例
gcloud sql instances list

# 检查实例状态
gcloud sql instances describe ai-project-database

# 确保实例正在运行
gcloud sql instances patch ai-project-database --activation-policy=ALWAYS
```

### Q4: Secret Manager 密钥不存在

**A**: 创建必需的密钥。

```bash
# 创建 AI API 密钥
echo -n "your-gemini-api-key" | gcloud secrets create AI_API_KEY_GOOGLE --data-file=-

# 创建数据库密码
echo -n "your-database-password" | gcloud secrets create DATABASE_PASSWORD --data-file=-

# 授予 Cloud Run 访问权限
gcloud secrets add-iam-policy-binding AI_API_KEY_GOOGLE \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding DATABASE_PASSWORD \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

---

## 🚀 完整部署流程

### 首次部署

```bash
# 1. 运行权限修复脚本
.\fix-gcp-permissions.ps1  # Windows
# 或
./fix-gcp-permissions.sh   # macOS/Linux

# 2. 创建必需的密钥（如果还没有）
echo -n "your-gemini-api-key" | gcloud secrets create AI_API_KEY_GOOGLE --data-file=-
echo -n "your-db-password" | gcloud secrets create DATABASE_PASSWORD --data-file=-
# ... 其他密钥

# 3. 等待权限生效
sleep 60

# 4. 开始部署
gcloud builds submit --config=cloudbuild.yaml

# 5. 查看部署日志
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)")
```

### 后续部署

```bash
gcloud builds submit --config=cloudbuild.yaml
```

---

## 📊 部署状态检查

```bash
# 查看最近的构建
gcloud builds list --limit=5

# 查看特定构建的日志
gcloud builds log BUILD_ID

# 查看 Cloud Run 服务状态
gcloud run services list --platform=managed

# 查看 Cloud Run 服务详情
gcloud run services describe auto-ski-info-backend --region=asia-northeast1
gcloud run services describe auto-ski-info-frontend --region=asia-northeast1

# 查看 Cloud Run 日志
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=auto-ski-info-backend" \
    --limit=50 \
    --format=json

# 测试 backend 健康检查
BACKEND_URL=$(gcloud run services describe auto-ski-info-backend --region=asia-northeast1 --format="value(status.url)")
curl $BACKEND_URL/admin/
```

---

## ✅ 验证部署成功

1. **Backend 可访问**

   ```bash
   BACKEND_URL=$(gcloud run services describe auto-ski-info-backend --region=asia-northeast1 --format="value(status.url)")
   curl $BACKEND_URL/admin/
   ```

2. **Frontend 可访问**

   ```bash
   FRONTEND_URL=$(gcloud run services describe auto-ski-info-frontend --region=asia-northeast1 --format="value(status.url)")
   curl $FRONTEND_URL
   ```

3. **Cloud Scheduler 已创建**

   ```bash
   gcloud scheduler jobs list --location=asia-northeast1
   ```

4. **数据库连接正常**
   - 访问 backend admin 页面
   - 尝试登录
   - 查看数据是否显示正常

---

## 📚 相关文档

- [Cloud Build 权限文档](https://cloud.google.com/build/docs/securing-builds/configure-access-to-resources)
- [Cloud Run IAM 文档](https://cloud.google.com/run/docs/securing/managing-access)
- [Secret Manager 权限](https://cloud.google.com/secret-manager/docs/access-control)

---

**如果问题仍未解决，请提供完整的错误日志以便进一步诊断。**
