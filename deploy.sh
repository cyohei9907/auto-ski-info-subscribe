#!/bin/bash

# デプロイスクリプト
# 使用方法: ./deploy.sh [project-id]

PROJECT_ID=${1:-gen-lang-client-0543160602}

echo "🚀 Auto Ski Info Subscribe をデプロイします..."
echo "プロジェクトID: $PROJECT_ID"

# Google Cloud プロジェクトを設定
gcloud config set project $PROJECT_ID

# Cloud Build APIを有効化
echo "📋 必要なAPIを有効化しています..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Cloud Build を実行
echo "🏗️ Cloud Build を実行しています..."
gcloud builds submit --config cloudbuild.yaml .

echo "✅ デプロイが完了しました！"

# サービスURLを取得
echo "🌐 サービスURL:"
echo "Backend: $(gcloud run services describe auto-ski-info-backend --region=asia-northeast1 --format='value(status.url)')"
echo "Frontend: $(gcloud run services describe auto-ski-info-frontend --region=asia-northeast1 --format='value(status.url)')"

echo ""
echo "📝 次のステップ:"
echo "1. Cloud SQL データベースの設定を確認してください"
echo "2. 環境変数（API キー等）をCloud Runサービスに設定してください"
echo "3. フロントエンドのAPI URLを更新してください"