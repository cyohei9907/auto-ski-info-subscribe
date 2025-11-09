#!/bin/bash
# GCP 权限修复脚本
# 解决 Cloud Build 部署到 Cloud Run 的权限问题

set -e

echo "============================================================"
echo "GCP 权限修复脚本"
echo "============================================================"
echo ""

# 获取项目 ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ 错误: 无法获取当前项目 ID"
    echo "   请先设置项目: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "当前项目 ID: $PROJECT_ID"
echo ""

# 获取项目编号
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
echo "项目编号: $PROJECT_NUMBER"
echo ""

# Cloud Build 服务账号
CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Cloud Build 服务账号:"
echo "  - Cloud Build: $CLOUD_BUILD_SA"
echo "  - Compute Engine: $COMPUTE_SA"
echo ""

# 需要授予的角色
ROLES=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/cloudsql.client"
    "roles/secretmanager.secretAccessor"
)

echo "开始授予权限..."
echo ""

for ROLE in "${ROLES[@]}"; do
    echo "授予角色: $ROLE"
    
    # 授予给 Cloud Build 服务账号
    if gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$CLOUD_BUILD_SA" \
        --role=$ROLE \
        --condition=None \
        >/dev/null 2>&1; then
        echo "  ✅ 已授予给 Cloud Build SA"
    else
        echo "  ⚠️  授予 Cloud Build SA 失败"
    fi
    
    # 授予给 Compute Engine 服务账号
    if gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$COMPUTE_SA" \
        --role=$ROLE \
        --condition=None \
        >/dev/null 2>&1; then
        echo "  ✅ 已授予给 Compute Engine SA"
    else
        echo "  ⚠️  授予 Compute Engine SA 失败"
    fi
    
    echo ""
done

# 启用必要的 API
echo "检查必要的 API..."
echo ""

APIS=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "secretmanager.googleapis.com"
    "sqladmin.googleapis.com"
    "cloudscheduler.googleapis.com"
)

for API in "${APIS[@]}"; do
    echo "检查 API: $API"
    
    if gcloud services list --enabled --filter="name:$API" --format="value(name)" 2>/dev/null | grep -q "$API"; then
        echo "  ✅ 已启用"
    else
        echo "  ⚠️  未启用，正在启用..."
        if gcloud services enable $API >/dev/null 2>&1; then
            echo "  ✅ 启用成功"
        else
            echo "  ❌ 启用失败"
        fi
    fi
done

echo ""
echo "============================================================"
echo "✅ 权限配置完成！"
echo ""
echo "下一步："
echo "1. 等待 30-60 秒让权限生效"
echo "2. 重新运行部署命令:"
echo "   gcloud builds submit --config=cloudbuild.yaml"
echo ""
echo "如果仍然失败，请检查:"
echo "- Cloud SQL 实例是否存在并正在运行"
echo "- Secret Manager 中的密钥是否都已创建"
echo "- 服务账号名称是否正确"
echo "============================================================"
