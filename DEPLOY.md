# Google Cloud デプロイガイド

本番環境（Google Cloud Run）へのデプロイ手順です。

## 前提条件

### 必要なもの
- Google Cloud アカウント
- gcloud CLI インストール・認証済み
- プロジェクトID: `gen-lang-client-0543160602`
- Cloud SQL インスタンス: `gen-lang-client-0543160602:asia-northeast1:ai-project-database`
- データベース名: `ski-scrapy`

### 必要なAPIキー
- X (Twitter) API 認証情報
- Google Gemini API キー
- Cloud SQL データベースパスワード

## デプロイ手順

### 1. Google Cloud 初期設定

```bash
# プロジェクトを設定
gcloud config set project gen-lang-client-0543160602

# 認証（必要に応じて）
gcloud auth login

# 必要なAPIを有効化
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
```

### 2. Cloud SQL データベース作成

```bash
# データベースが存在しない場合は作成
gcloud sql databases create ski-scrapy \
  --instance=ai-project-database

# データベースユーザーのパスワードを設定（必要に応じて）
gcloud sql users set-password postgres \
  --instance=ai-project-database \
  --password=YOUR_SECURE_PASSWORD
```

### 3. Secret Manager にシークレットを設定

自動セットアップスクリプトを使用：

```bash
# スクリプトに実行権限を付与
chmod +x setup-secrets.sh

# スクリプトを実行
./setup-secrets.sh gen-lang-client-0543160602
```

または手動で設定：

```bash
# DATABASE_PASSWORD
echo -n "your-db-password" | gcloud secrets create DATABASE_PASSWORD --data-file=-

# AI_API_KEY_GOOGLE
echo -n "your-gemini-api-key" | gcloud secrets create AI_API_KEY_GOOGLE --data-file=-

# X API 認証情報
echo -n "your-x-api-key" | gcloud secrets create X_API_KEY --data-file=-
echo -n "your-x-api-secret" | gcloud secrets create X_API_SECRET --data-file=-
echo -n "your-x-access-token" | gcloud secrets create X_ACCESS_TOKEN --data-file=-
echo -n "your-x-access-token-secret" | gcloud secrets create X_ACCESS_TOKEN_SECRET --data-file=-
echo -n "your-x-bearer-token" | gcloud secrets create X_BEARER_TOKEN --data-file=-

# サービスアカウントに権限を付与
PROJECT_ID="gen-lang-client-0543160602"
SERVICE_ACCOUNT="${PROJECT_ID}-compute@developer.gserviceaccount.com"

for SECRET in DATABASE_PASSWORD AI_API_KEY_GOOGLE X_API_KEY X_API_SECRET X_ACCESS_TOKEN X_ACCESS_TOKEN_SECRET X_BEARER_TOKEN; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"
done
```

### 4. アプリケーションのデプロイ

```bash
# デプロイスクリプトに実行権限を付与
chmod +x deploy.sh

# デプロイを実行
./deploy.sh gen-lang-client-0543160602
```

または手動でCloud Buildを実行：

```bash
gcloud builds submit --config cloudbuild.yaml .
```

### 5. データベースマイグレーション

```bash
# バックエンドサービスのURLを取得
BACKEND_URL=$(gcloud run services describe auto-ski-info-backend \
  --region=asia-northeast1 \
  --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"

# Cloud Run インスタンスでマイグレーションを実行
# (一時的にCloud Shellからアクセス、または Cloud Run Jobs を使用)
```

手動マイグレーション方法：

```bash
# Cloud Shellでコンテナを起動してマイグレーション
gcloud run jobs create migrate-db \
  --image=gcr.io/gen-lang-client-0543160602/auto-ski-info-backend:latest \
  --region=asia-northeast1 \
  --set-env-vars=USE_CLOUD_SQL=True,CLOUD_DB_NAME=ski-scrapy,CLOUD_DB_USER=postgres \
  --set-secrets=DATABASE_PASSWORD=DATABASE_PASSWORD:latest \
  --add-cloudsql-instances=gen-lang-client-0543160602:asia-northeast1:ai-project-database \
  --command=python \
  --args=manage.py,migrate

# ジョブを実行
gcloud run jobs execute migrate-db --region=asia-northeast1
```

### 6. スーパーユーザー作成（初回のみ）

```bash
# Cloud Run Jobs でスーパーユーザーを作成
gcloud run jobs create create-superuser \
  --image=gcr.io/gen-lang-client-0543160602/auto-ski-info-backend:latest \
  --region=asia-northeast1 \
  --set-env-vars=USE_CLOUD_SQL=True,CLOUD_DB_NAME=ski-scrapy,CLOUD_DB_USER=postgres,DJANGO_SUPERUSER_USERNAME=admin,DJANGO_SUPERUSER_EMAIL=admin@example.com,DJANGO_SUPERUSER_PASSWORD=changeme123 \
  --set-secrets=DATABASE_PASSWORD=DATABASE_PASSWORD:latest \
  --add-cloudsql-instances=gen-lang-client-0543160602:asia-northeast1:ai-project-database \
  --command=python \
  --args=manage.py,createsuperuser,--noinput

gcloud run jobs execute create-superuser --region=asia-northeast1
```

### 7. Cloud Scheduler 設定（自動監視）

15分ごとに監視タスクを実行：

```bash
# App Engine アプリケーションを作成（Cloud Scheduler に必要）
gcloud app create --region=asia-northeast1 2>/dev/null || true

# Scheduler ジョブを作成
gcloud scheduler jobs create http monitor-x-accounts \
  --schedule="*/15 * * * *" \
  --uri="https://auto-ski-info-backend-XXXX.a.run.app/api/monitor/trigger-all/" \
  --http-method=POST \
  --oidc-service-account-email=${SERVICE_ACCOUNT} \
  --location=asia-northeast1 \
  --time-zone=Asia/Tokyo
```

## デプロイ後の確認

### 1. サービスURL取得

```bash
# バックエンドURL
gcloud run services describe auto-ski-info-backend \
  --region=asia-northeast1 \
  --format='value(status.url)'

# フロントエンドURL
gcloud run services describe auto-ski-info-frontend \
  --region=asia-northeast1 \
  --format='value(status.url)'
```

### 2. アクセステスト

```bash
# ヘルスチェック
BACKEND_URL=$(gcloud run services describe auto-ski-info-backend \
  --region=asia-northeast1 --format='value(status.url)')

curl "${BACKEND_URL}/admin/"
curl "${BACKEND_URL}/swagger/"
```

### 3. ログ確認

```bash
# バックエンドログ
gcloud run services logs read auto-ski-info-backend \
  --region=asia-northeast1 \
  --limit=50

# フロントエンドログ
gcloud run services logs read auto-ski-info-frontend \
  --region=asia-northeast1 \
  --limit=50
```

## 環境変数の更新

デプロイ後に環境変数を更新する場合：

```bash
# バックエンド環境変数を更新
gcloud run services update auto-ski-info-backend \
  --region=asia-northeast1 \
  --set-env-vars="NEW_VAR=value"

# シークレットを更新
echo -n "new-value" | gcloud secrets versions add SECRET_NAME --data-file=-
```

## トラブルシューティング

### デプロイが失敗する

```bash
# Cloud Build ログを確認
gcloud builds list --limit=5
gcloud builds log [BUILD_ID]

# サービスアカウントの権限を確認
gcloud projects get-iam-policy gen-lang-client-0543160602
```

### データベース接続エラー

```bash
# Cloud SQL インスタンスの状態確認
gcloud sql instances describe ai-project-database

# データベース一覧を確認
gcloud sql databases list --instance=ai-project-database

# 接続テスト
gcloud sql connect ai-project-database --user=postgres --database=ski-scrapy
```

### Secret Manager エラー

```bash
# シークレット一覧を確認
gcloud secrets list

# シークレットの値を確認（注意：機密情報が表示されます）
gcloud secrets versions access latest --secret=AI_API_KEY_GOOGLE

# IAM権限を確認
gcloud secrets get-iam-policy DATABASE_PASSWORD
```

### メモリ不足・タイムアウト

```bash
# メモリとCPUを増やす
gcloud run services update auto-ski-info-backend \
  --region=asia-northeast1 \
  --memory=4Gi \
  --cpu=4 \
  --timeout=600
```

## コスト最適化

### 最小インスタンス数の設定

```bash
# 常時起動（レスポンス速度重視）
gcloud run services update auto-ski-info-backend \
  --region=asia-northeast1 \
  --min-instances=1

# コールドスタート許容（コスト重視）
gcloud run services update auto-ski-info-backend \
  --region=asia-northeast1 \
  --min-instances=0
```

### リソース削減

```bash
# メモリを減らす
gcloud run services update auto-ski-info-backend \
  --region=asia-northeast1 \
  --memory=1Gi \
  --cpu=1
```

## 更新とロールバック

### 新しいバージョンをデプロイ

```bash
# コードを更新したら再度デプロイ
./deploy.sh gen-lang-client-0543160602
```

### 以前のバージョンにロールバック

```bash
# リビジョン一覧を表示
gcloud run revisions list \
  --service=auto-ski-info-backend \
  --region=asia-northeast1

# 特定のリビジョンにロールバック
gcloud run services update-traffic auto-ski-info-backend \
  --region=asia-northeast1 \
  --to-revisions=REVISION_NAME=100
```

## セキュリティ

### サービスアカウントの作成（推奨）

```bash
# 専用サービスアカウントを作成
gcloud iam service-accounts create auto-ski-info-sa \
  --display-name="Auto Ski Info Service Account"

# 必要な権限を付与
gcloud projects add-iam-policy-binding gen-lang-client-0543160602 \
  --member="serviceAccount:auto-ski-info-sa@gen-lang-client-0543160602.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Cloud Runサービスで使用
gcloud run services update auto-ski-info-backend \
  --region=asia-northeast1 \
  --service-account=auto-ski-info-sa@gen-lang-client-0543160602.iam.gserviceaccount.com
```

## モニタリング

### Cloud Monitoring ダッシュボード

https://console.cloud.google.com/monitoring/dashboards

### アラート設定

```bash
# エラー率が高い場合のアラート
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s
```

## サポート

問題が発生した場合：
1. ログを確認（Cloud Console または gcloud コマンド）
2. GitHub Issues に報告
3. サポートチームに連絡

---

**重要**: 本番環境では必ずセキュリティベストプラクティスに従ってください：
- 強力なパスワードを使用
- Secret Manager で機密情報を管理
- 最小権限の原則に従う
- 定期的なセキュリティ更新