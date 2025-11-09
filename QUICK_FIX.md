# 🚨 GCP 部署权限修复 - 快速指南

## ⚡ 最快解决方案（1 分钟）

```bash
# 运行自动修复脚本
.\fix-gcp-permissions.ps1  # Windows
# 或
./fix-gcp-permissions.sh   # Linux/Mac

# 等待权限生效
sleep 60

# 重新部署
gcloud builds submit --config=cloudbuild.yaml
```

---

## 📋 手动修复（如果脚本失败）

```bash
# 1. 获取项目信息
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# 2. 授予权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# 3. 等待并重试
sleep 60
gcloud builds submit --config=cloudbuild.yaml
```

---

## 🔍 验证权限

```bash
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# 查看 Cloud Build 服务账号的权限
gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
```

---

## ✅ 必需的角色

- ✅ `roles/run.admin` - 部署 Cloud Run
- ✅ `roles/iam.serviceAccountUser` - 模拟服务账号
- ✅ `roles/cloudsql.client` - 连接数据库
- ✅ `roles/secretmanager.secretAccessor` - 访问密钥

---

完整文档：`GCP_PERMISSION_FIX.md`
