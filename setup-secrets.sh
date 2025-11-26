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

echo ""
echo "✅ シークレットの設定が完了しました！"
echo ""

# サービスアカウントへのアクセス権限付与
echo "🔧 Cloud Run サービスアカウントにシークレットへのアクセス権限を付与しています..."

# デフォルトの Compute Engine サービスアカウント
SERVICE_ACCOUNT="${PROJECT_ID}-compute@developer.gserviceaccount.com"

for SECRET in DATABASE_PASSWORD AI_API_KEY_GOOGLE; do
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