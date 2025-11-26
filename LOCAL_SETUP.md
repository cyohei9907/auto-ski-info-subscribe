# ローカル開発環境セットアップガイド

## 前提条件

### 必要なソフトウェア

- Docker Desktop
- Git
- テキストエディタ (VS Code 推奨)

### 必要な API キー

**Google Gemini API キー**

- https://makersuite.google.com/app/apikey でキーを作成
- API Key を取得

## セットアップ手順

### 1. システム環境変数の設定

#### Windows (PowerShell)

```powershell
# システム環境変数に追加
[System.Environment]::SetEnvironmentVariable('AI_API_KEY_GOOGLE', 'your-gemini-api-key', 'User')

# PowerShell を再起動して反映
```

#### macOS / Linux (bash/zsh)

```bash
# ~/.bashrc または ~/.zshrc に追加
export AI_API_KEY_GOOGLE="your-gemini-api-key"

# 設定を反映
source ~/.bashrc  # または source ~/.zshrc
```

### 2. プロジェクトのクローン

```bash
git clone https://github.com/cyohei9907/auto-ski-info-subscribe.git
cd auto-ski-info-subscribe
```

### 3. 環境変数ファイルの作成

```bash
# バックエンド環境変数（オプション - システム環境変数を優先）
cp backend/.env.example backend/.env

# フロントエンド環境変数
cp frontend/.env.example frontend/.env
```

### 4. Docker Compose で起動

```bash
# すべてのサービスを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### 5. データベース初期化

```bash
# Djangoマイグレーション実行
docker-compose exec backend python manage.py migrate

# スーパーユーザー作成
docker-compose exec backend python manage.py createsuperuser
```

### 6. アクセス確認

- **フロントエンド**: http://localhost:3000
- **バックエンド API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/swagger/
- **Django Admin**: http://localhost:8000/admin/

## サービス構成（ローカル開発）

### 起動するコンテナ

1. **backend** - Django アプリケーション (ポート 8000)

   - SQLite データベース使用
   - `/app/data/db.sqlite3` に保存

2. **frontend** - React アプリケーション (ポート 3000)

   - 開発サーバー

3. **redis** - Celery メッセージブローカー (ポート 6379)

4. **celery** - バックグラウンドタスクワーカー

   - ツイート取得処理

5. **celery-beat** - 定期タスクスケジューラー
   - 15 分ごとに監視タスクを実行

## よくある問題と解決方法

### 環境変数が読み込まれない

```bash
# 環境変数を確認
docker-compose exec backend env | grep API_KEY

# システム環境変数が設定されているか確認
# Windows
echo $env:AI_API_KEY_GOOGLE

# macOS/Linux
echo $AI_API_KEY_GOOGLE
```

### Celery タスクが実行されない

```bash
# Celery ワーカーのログを確認
docker-compose logs celery

# Redis接続を確認
docker-compose exec redis redis-cli ping
```

### データベースをリセットしたい

```bash
# コンテナを停止
docker-compose down

# SQLiteファイルを削除
rm -rf backend/data/db.sqlite3

# 再起動とマイグレーション
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

### ポートが使用中

```bash
# 使用中のポートを確認
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000

# docker-compose.yml でポート番号を変更
```

## 開発ワークフロー

### 1. コード変更の反映

- **フロントエンド**: ホットリロード自動適用
- **バックエンド**: ボリュームマウント済み、自動リロード

### 2. 新しいパッケージの追加

```bash
# バックエンド
docker-compose exec backend pip install package-name
docker-compose exec backend pip freeze > requirements.txt

# フロントエンド
docker-compose exec frontend npm install package-name
```

### 3. マイグレーション

```bash
# マイグレーションファイル作成
docker-compose exec backend python manage.py makemigrations

# マイグレーション適用
docker-compose exec backend python manage.py migrate
```

### 4. テスト実行

```bash
# バックエンドテスト
docker-compose exec backend python manage.py test

# フロントエンドテスト
docker-compose exec frontend npm test
```

## データのバックアップ

### SQLite データベース

```bash
# データベースファイルをコピー
docker-compose exec backend cp /app/data/db.sqlite3 /app/db_backup.sqlite3

# ホストにコピー
docker cp auto-ski-info-backend-1:/app/db_backup.sqlite3 ./backup/
```

## サービスの停止

```bash
# すべてのコンテナを停止
docker-compose down

# ボリュームも削除（データもクリア）
docker-compose down -v
```

## 次のステップ

1. ✅ ローカル開発環境の動作確認
2. ✅ X アカウントを追加して監視テスト
3. ✅ AI 分析機能のテスト
4. 📤 本番環境へのデプロイ（DEPLOY.md 参照）
