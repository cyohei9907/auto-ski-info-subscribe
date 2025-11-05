# 配置概要

## 環境別の設定

### ローカル開発環境

#### データベース
- **種類**: SQLite
- **場所**: `backend/data/db.sqlite3`
- **設定**: 自動（設定不要）

#### APIキー取得方法
- **環境変数**から自動取得
- システム環境変数に設定:
  - `GEMINI_API_KEY`
  - `X_API_KEY`
  - `X_API_SECRET`
  - `X_ACCESS_TOKEN`
  - `X_ACCESS_TOKEN_SECRET`
  - `X_BEARER_TOKEN`

#### 設定ファイル
```bash
# backend/.env（オプション）
USE_CLOUD_SQL=False
DEBUG=True
```

### 本番環境（Google Cloud Run）

#### データベース
- **種類**: Cloud SQL (PostgreSQL)
- **インスタンス**: `gen-lang-client-0543160602:asia-northeast1:ai-project-database`
- **データベース名**: `ski-scrapy`
- **接続**: Unix ソケット (`/cloudsql/...`)

#### APIキー取得方法
- **Secret Manager**から自動取得
- 必要なシークレット:
  - `AI_API_KEY_GOOGLE` - Gemini APIキー
  - `DATABASE_PASSWORD` - データベースパスワード
  - `X_API_KEY` - Twitter API Key
  - `X_API_SECRET` - Twitter API Secret
  - `X_ACCESS_TOKEN` - Twitter Access Token
  - `X_ACCESS_TOKEN_SECRET` - Twitter Token Secret
  - `X_BEARER_TOKEN` - Twitter Bearer Token

#### 設定
- `USE_CLOUD_SQL=True`（自動設定）
- `DEBUG=False`（自動設定）
- Cloud Build の `cloudbuild.yaml` で自動設定

## 設定の切り替え

### settings.py の動作

```python
# 環境変数 USE_CLOUD_SQL で自動切り替え
if USE_CLOUD_SQL:
    # 本番環境: Cloud SQL (PostgreSQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': '/cloudsql/...',
            'NAME': 'ski-scrapy',
            'PASSWORD': config('DATABASE_PASSWORD'),  # Secret Manager
        }
    }
else:
    # ローカル環境: SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Gemini APIキー - 環境に応じて自動切り替え
GEMINI_API_KEY = config('AI_API_KEY_GOOGLE',  # Cloud: Secret Manager
                       default=config('GEMINI_API_KEY', default=''))  # Local: 環境変数
```

## 起動方法

### ローカル開発

```bash
# 1. システム環境変数にAPIキーを設定
export GEMINI_API_KEY="your-key"
export X_BEARER_TOKEN="your-token"
# ... 他のキーも同様

# 2. Docker Compose で起動
docker-compose up -d

# 3. アクセス
# http://localhost:3000
```

### 本番デプロイ

```bash
# 1. Secret Manager にシークレットを設定
./setup-secrets.sh gen-lang-client-0543160602

# 2. デプロイ実行
./deploy.sh gen-lang-client-0543160602

# Cloud Build が自動的に:
# - Docker イメージをビルド
# - Cloud Run にデプロイ
# - Secret Manager からシークレットを注入
# - Cloud SQL に接続
```

## サービス構成

### ローカル開発
```
├── backend (Django + SQLite)
├── frontend (React)
├── redis (Celery broker)
├── celery (Worker)
└── celery-beat (Scheduler - 15分ごと)
```

### 本番環境
```
├── auto-ski-info-backend (Cloud Run)
│   ├── Django API
│   └── Cloud SQL 接続
├── auto-ski-info-frontend (Cloud Run)
│   └── React SPA
└── Cloud Scheduler
    └── 15分ごとに監視API呼び出し
```

## チェックリスト

### ローカル開発開始前
- [ ] Docker Desktop インストール
- [ ] X API キー取得
- [ ] Gemini API キー取得
- [ ] システム環境変数に設定
- [ ] リポジトリクローン
- [ ] `docker-compose up -d` 実行

### 本番デプロイ前
- [ ] gcloud CLI インストール・認証
- [ ] プロジェクトIDが `gen-lang-client-0543160602` であることを確認
- [ ] Cloud SQL インスタンス `ai-project-database` 存在確認
- [ ] データベース `ski-scrapy` 作成済み確認
- [ ] すべてのAPIキー準備済み
- [ ] `./setup-secrets.sh` 実行
- [ ] `./deploy.sh` 実行

## トラブルシューティング

### ローカル: APIキーが認識されない
```bash
# 環境変数を確認
docker-compose exec backend env | grep API_KEY

# システム環境変数を確認
echo $GEMINI_API_KEY  # Linux/Mac
echo $env:GEMINI_API_KEY  # Windows PowerShell
```

### 本番: Secret Managerエラー
```bash
# シークレット一覧を確認
gcloud secrets list

# 特定のシークレットを確認
gcloud secrets versions access latest --secret=AI_API_KEY_GOOGLE

# IAM権限を確認
gcloud secrets get-iam-policy AI_API_KEY_GOOGLE
```

### ローカル: データベースリセット
```bash
# SQLiteファイルを削除
docker-compose down
rm -rf backend/data/db.sqlite3
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

## セキュリティ注意事項

### ローカル開発
- ✅ システム環境変数にAPIキーを保存（リポジトリに含めない）
- ✅ `.env` ファイルは `.gitignore` に含まれている
- ❌ APIキーをコードにハードコードしない

### 本番環境
- ✅ Secret Manager で機密情報を管理
- ✅ Cloud Run のサービスアカウントで権限制御
- ✅ 環境変数に直接シークレットを設定しない
- ✅ Cloud SQL は Unix ソケット接続（暗号化）

## 参考ドキュメント

- ローカル開発: `LOCAL_SETUP.md`
- 本番デプロイ: `DEPLOY.md`
- プロジェクト概要: `README.md`