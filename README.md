# Auto Ski Info Subscribe

X（Twitter）スキー場情報自動監視システム - React + Django + Gemini AI

## 📋 概要

このプロジェクトは、X（Twitter）上の特定のアカウントを監視し、スキー場に関する情報を自動収集・分析するシステムです。Gemini AIを使用してツイートの感情分析や重要度評価を行い、有用な情報を効率的に取得できます。

## 🚀 主な機能

### 🔧 コア機能
- **アカウント監視**: 指定したXアカウントを15分間隔で自動監視
- **リアルタイム収集**: 新しいツイートを自動的に取得・保存
- **AI分析**: Gemini AIによる感情分析、要約、トピック抽出
- **重要度評価**: スキー場関連情報の重要度を自動判定

### 👤 ユーザー機能
- **ユーザー認証**: 登録・ログイン機能
- **アカウント管理**: 監視対象の追加・削除・設定変更
- **ツイート閲覧**: 収集したツイートとAI分析結果の表示
- **フィルタリング**: 感情、重要度、アカウント別での絞り込み
- **ログ管理**: 監視実行履歴とエラー情報の確認

### 🔍 AI機能
- **感情分析**: ポジティブ・ネガティブ・ニュートラル判定
- **自動要約**: ツイート内容の簡潔な要約生成
- **トピック抽出**: 主要キーワードとトピックの自動抽出
- **重要度スコア**: スキー場情報の関連性と重要度の数値化

## 🏗️ システム構成

### フロントエンド
- **React 18**: モダンなユーザーインターフェース
- **Ant Design**: 統一された美しいUIコンポーネント
- **React Query**: 効率的なデータ取得・キャッシュ管理
- **React Router**: SPA用ルーティング

### バックエンド
- **Django 4.2**: 堅牢なWebフレームワーク
- **Django REST Framework**: RESTful API構築
- **Celery**: 非同期タスク処理（15分間隔の監視）
- **Redis**: Celeryメッセージブローカー
- **drf-yasg**: Swagger API ドキュメント自動生成

### AI・外部サービス
- **Google Gemini AI**: 高度な自然言語処理
- **X (Twitter) API v2**: ツイートデータ取得
- **PostgreSQL**: メインデータベース
- **Google Cloud SQL**: 本番環境データベース

### インフラ・デプロイ
- **Docker**: コンテナ化による環境統一
- **Google Cloud Run**: サーバーレスコンテナホスティング
- **Google Cloud Build**: CI/CD パイプライン
- **Nginx**: フロントエンド用Webサーバー

## 📁 プロジェクト構成

```
auto-ski-info-subscribe/
├── README.md
├── docker-compose.yml          # 開発環境用Docker設定
├── cloudbuild.yaml            # Cloud Build設定
├── deploy.sh                  # デプロイスクリプト
├── .gitignore
├── 
├── backend/                   # Django バックエンド
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── manage.py
│   ├── .env.example
│   ├── 
│   ├── auto_ski_info/         # Django メイン設定
│   │   ├── __init__.py
│   │   ├── settings.py        # Django 設定
│   │   ├── urls.py           # URL ルーティング
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── celery.py         # Celery 設定
│   ├── 
│   ├── accounts/              # ユーザー認証アプリ
│   │   ├── models.py         # User, UserProfile モデル
│   │   ├── serializers.py    # API シリアライザー
│   │   ├── views.py          # 認証API エンドポイント
│   │   └── urls.py
│   ├── 
│   ├── x_monitor/             # X監視アプリ
│   │   ├── models.py         # XAccount, Tweet, MonitoringLog モデル
│   │   ├── services.py       # X API クライアント
│   │   ├── tasks.py          # Celery タスク（15分間隔実行）
│   │   ├── serializers.py
│   │   ├── views.py          # 監視API エンドポイント
│   │   └── urls.py
│   └── 
│   └── ai_service/            # AI分析アプリ
│       ├── services.py       # Gemini AI サービス
│       └── urls.py           # AI API エンドポイント
├── 
└── frontend/                  # React フロントエンド
    ├── Dockerfile
    ├── nginx.conf            # Nginx 設定
    ├── package.json
    ├── .env.example
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js          # アプリエントリーポイント
        ├── App.js           # メインアプリコンポーネント
        ├── index.css        # グローバルスタイル
        ├── 
        ├── components/       # 再利用可能コンポーネント
        │   └── MainLayout.js # メインレイアウト
        ├── 
        ├── pages/           # ページコンポーネント
        │   ├── LoginPage.js     # ログイン・登録ページ
        │   ├── DashboardPage.js # ダッシュボード
        │   ├── AccountsPage.js  # アカウント管理
        │   ├── TweetsPage.js    # ツイート一覧
        │   └── LogsPage.js      # 監視ログ
        ├── 
        ├── contexts/        # React Context
        │   └── AuthContext.js   # 認証状態管理
        └── 
        └── services/        # API サービス
            └── api.js       # API クライアント
```

## 🛠️ 開発環境セットアップ

### 前提条件
- Docker & Docker Compose
- X (Twitter) API キー
- Google Gemini API キー

**注意**: ローカル開発環境では **SQLite** を使用します（PostgreSQL 不要）

### クイックスタート

#### 1. システム環境変数にAPIキーを設定

**Windows (PowerShell)**
```powershell
[System.Environment]::SetEnvironmentVariable('X_API_KEY', 'your-key', 'User')
[System.Environment]::SetEnvironmentVariable('X_API_SECRET', 'your-secret', 'User')
[System.Environment]::SetEnvironmentVariable('X_ACCESS_TOKEN', 'your-token', 'User')
[System.Environment]::SetEnvironmentVariable('X_ACCESS_TOKEN_SECRET', 'your-secret', 'User')
[System.Environment]::SetEnvironmentVariable('X_BEARER_TOKEN', 'your-bearer', 'User')
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-key', 'User')
# PowerShell を再起動
```

**macOS/Linux (bash/zsh)**
```bash
export X_API_KEY="your-key"
export X_API_SECRET="your-secret"
export X_ACCESS_TOKEN="your-token"
export X_ACCESS_TOKEN_SECRET="your-secret"
export X_BEARER_TOKEN="your-bearer"
export GEMINI_API_KEY="your-key"
# ~/.bashrc または ~/.zshrc に追加して永続化
```

#### 2. リポジトリのクローンと起動
```bash
git clone https://github.com/cyohei9907/auto-ski-info-subscribe.git
cd auto-ski-info-subscribe

# Docker Compose で全サービスを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

#### 3. アクセス
- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/swagger/
- **Django Admin**: http://localhost:8000/admin/
  - ユーザー名: `admin`
  - パスワード: `admin@123`

### データベース
- **ローカル**: SQLite (`backend/data/db.sqlite3`)
- **本番**: Cloud SQL PostgreSQL (`ski-scrapy`)

詳細な手順は [LOCAL_SETUP.md](LOCAL_SETUP.md) を参照してください。

## 🌐 本番環境デプロイ（Google Cloud）

### 前提条件
- Google Cloud プロジェクト: `gen-lang-client-0543160602`
- Cloud SQL インスタンス: `ai-project-database`
- データベース名: `ski-scrapy`
- gcloud CLI インストール・認証済み

### デプロイ手順

#### 1. Secret Manager にAPIキーを設定
```bash
# 自動セットアップスクリプトを実行
chmod +x setup-secrets.sh
./setup-secrets.sh gen-lang-client-0543160602
```

設定するシークレット:
- `DATABASE_PASSWORD` - Cloud SQL パスワード
- `AI_API_KEY_GOOGLE` - Gemini API キー
- `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`, `X_BEARER_TOKEN` - Twitter API認証情報

#### 2. アプリケーションをデプロイ
```bash
# デプロイスクリプトを実行
chmod +x deploy.sh
./deploy.sh gen-lang-client-0543160602
```

#### 3. 自動監視の設定
Cloud Scheduler が15分ごとに自動実行されます（cloudbuild.yaml で自動設定）

詳細な手順とトラブルシューティングは [DEPLOY.md](DEPLOY.md) を参照してください。

## 📊 API ドキュメント

本番環境にデプロイ後、以下のエンドポイントでAPI ドキュメントにアクセス可能：

- **Swagger UI**: https://your-backend-url.run.app/swagger/
- **ReDoc**: https://your-backend-url.run.app/redoc/

### 主要エンドポイント

#### 認証
- `POST /api/auth/register/` - ユーザー登録
- `POST /api/auth/login/` - ログイン
- `POST /api/auth/logout/` - ログアウト
- `GET /api/auth/user/` - ユーザー情報取得

#### X監視
- `GET /api/monitor/accounts/` - 監視アカウント一覧
- `POST /api/monitor/accounts/` - アカウント追加
- `POST /api/monitor/accounts/{id}/monitor/` - 手動監視実行
- `GET /api/monitor/tweets/` - ツイート一覧
- `POST /api/monitor/tweets/{id}/analyze/` - AI分析実行

#### AI サービス
- `POST /api/ai/sentiment/` - 感情分析
- `POST /api/ai/summarize/` - テキスト要約
- `POST /api/ai/topics/` - トピック抽出

## 🔧 設定とカスタマイズ

### 監視間隔の変更
```python
# backend/auto_ski_info/celery.py
app.conf.beat_schedule = {
    'monitor-x-accounts': {
        'task': 'x_monitor.tasks.monitor_all_active_accounts',
        'schedule': crontab(minute='*/15'),  # 15分間隔を変更
    },
}
```

### AI プロンプトのカスタマイズ
```python
# backend/ai_service/services.py の GeminiService クラス内
# analyze_tweet_sentiment, summarize_tweet, extract_topics メソッド内の
# プロンプト文字列を編集
```

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. X API エラー
```bash
# APIキーとレート制限を確認
# .env ファイルの X_* 変数を確認
```

#### 2. Gemini API エラー
```bash
# API キーと quota を確認
# GEMINI_API_KEY が正しく設定されているか確認
```

#### 3. データベース接続エラー
```bash
# Cloud SQL インスタンスの状態確認
# データベース認証情報の確認
```

#### 4. Celery タスクが実行されない
```bash
# Redis の動作確認
# Celery worker の起動確認
docker-compose logs celery
```

## 📈 監視・ログ

### ログの場所
- **Django**: Cloud Run ログまたは stdout
- **Celery**: Redis キューとCloud Run ログ
- **監視ログ**: データベース（MonitoringLog テーブル）

### メトリクス監視
- Google Cloud Monitoring での Cloud Run メトリクス
- API エラー率とレスポンス時間
- データベース接続状況

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 📞 サポート

- 問題報告: [GitHub Issues](https://github.com/cyohei9907/auto-ski-info-subscribe/issues)
- ドキュメント: このREADME と API ドキュメント
- 連絡先: cyohei9907@example.com

## 🔄 更新履歴

### v1.0.0 (2025-11-05)
- 初期リリース
- X (Twitter) アカウント監視機能
- Gemini AI による分析機能
- React フロントエンド UI
- Google Cloud Run デプロイ対応