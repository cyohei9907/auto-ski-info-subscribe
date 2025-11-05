#!/bin/bash

# Google Cloud Secret Manager セットアップスクリプト
# 使用方法: ./setup-secrets.sh [project-id]

PROJECT_ID=${1:-gen-lang-client-0543160602}

echo "🔐 Secret Manager にシークレットを設定します..."
echo "プロジェクトID: $PROJECT_ID"

# Google Cloud プロジェクトを設定
gcloud config set project $PROJECT_ID

# Secret Manager API を有効化
echo "📋 Secret Manager API を有効化しています..."
gcloud services enable secretmanager.googleapis.com

# シークレットの作成と設定
echo ""
echo "🔑 シークレットを設定してください:"
echo ""

# DATABASE_PASSWORD
read -sp "DATABASE_PASSWORD (Cloud SQL パスワード): " DB_PASSWORD
echo ""
echo $DB_PASSWORD | gcloud secrets create DATABASE_PASSWORD --data-file=- --replication-policy="automatic" 2>/dev/null || \
echo $DB_PASSWORD | gcloud secrets versions add DATABASE_PASSWORD --data-file=-

# AI_API_KEY_GOOGLE
read -sp "AI_API_KEY_GOOGLE (Gemini API キー): " GEMINI_KEY
echo ""
echo $GEMINI_KEY | gcloud secrets create AI_API_KEY_GOOGLE --data-file=- --replication-policy="automatic" 2>/dev/null || \
echo $GEMINI_KEY | gcloud secrets versions add AI_API_KEY_GOOGLE --data-file=-

# X_API_KEY
read -sp "X_API_KEY (Twitter API キー): " X_KEY
echo ""
echo $X_KEY | gcloud secrets create X_API_KEY --data-file=- --replication-policy="automatic" 2>/dev/null || \
echo $X_KEY | gcloud secrets versions add X_API_KEY --data-file=-

# X_API_SECRET
read -sp "X_API_SECRET (Twitter API シークレット): " X_SECRET
echo ""
echo $X_SECRET | gcloud secrets create X_API_SECRET --data-file=- --replication-policy="automatic" 2>/dev/null || \
echo $X_SECRET | gcloud secrets versions add X_API_SECRET --data-file=-

# X_ACCESS_TOKEN
read -sp "X_ACCESS_TOKEN (Twitter アクセストークン): " X_TOKEN
echo ""
echo $X_TOKEN | gcloud secrets create X_ACCESS_TOKEN --data-file=- --replication-policy="automatic" 2>/dev/null || \
echo $X_TOKEN | gcloud secrets versions add X_ACCESS_TOKEN --data-file=-

# X_ACCESS_TOKEN_SECRET
read -sp "X_ACCESS_TOKEN_SECRET (Twitter アクセストークンシークレット): " X_TOKEN_SECRET
echo ""
echo $X_TOKEN_SECRET | gcloud secrets create X_ACCESS_TOKEN_SECRET --data-file=- --replication-policy="automatic" 2>/dev/null || \
echo $X_TOKEN_SECRET | gcloud secrets versions add X_ACCESS_TOKEN_SECRET --data-file=-

# X_BEARER_TOKEN
read -sp "X_BEARER_TOKEN (Twitter Bearer トークン): " X_BEARER
echo ""
echo $X_BEARER | gcloud secrets create X_BEARER_TOKEN --data-file=- --replication-policy="automatic" 2>/dev/null || \
echo $X_BEARER | gcloud secrets versions add X_BEARER_TOKEN --data-file=-

echo ""
echo "✅ シークレットの設定が完了しました！"
echo ""

# サービスアカウントへのアクセス権限付与
echo "🔧 Cloud Run サービスアカウントにシークレットへのアクセス権限を付与しています..."

# デフォルトの Compute Engine サービスアカウント
SERVICE_ACCOUNT="${PROJECT_ID}-compute@developer.gserviceaccount.com"

for SECRET in DATABASE_PASSWORD AI_API_KEY_GOOGLE X_API_KEY X_API_SECRET X_ACCESS_TOKEN X_ACCESS_TOKEN_SECRET X_BEARER_TOKEN; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
done

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "📝 次のステップ:"
echo "1. Cloud SQL データベース 'ski-scrapy' が作成されていることを確認"
echo "2. ./deploy.sh を実行してアプリケーションをデプロイ"
echo ""
echo "🔍 設定されたシークレット一覧:"
gcloud secrets list