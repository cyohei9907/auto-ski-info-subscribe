# VS Code Dockerデバッグガイド

このガイドでは、VS CodeからDjango BackendをDockerコンテナ内でデバッグする方法を説明します。

## 前提条件

- Docker Desktop がインストールされ、起動していること
- VS Code に Python 拡張機能がインストールされていること
- 環境変数が設定されていること(LOCAL_SETUP.md参照)

## デバッグの開始方法

### 1. Dockerコンテナを起動する

デバッグモードでコンテナを起動します:

```bash
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up -d
```

または、VS Codeのタスクから実行:
- `Ctrl+Shift+P` → `Tasks: Run Task` → `docker-compose-debug-up` を選択

### 2. デバッガーをアタッチする

VS Codeのデバッグビューから:
1. サイドバーの「実行とデバッグ」アイコンをクリック(Ctrl+Shift+D)
2. ドロップダウンから `Docker: Django Backend` を選択
3. 緑色の再生ボタンをクリックするか、`F5` キーを押す

### 3. ブレークポイントを設定する

デバッグしたいPythonファイル(.py)を開き、行番号の左側をクリックしてブレークポイントを設定します。

例:
- `backend/x_monitor/views.py` の `list` メソッド
- `backend/ai_service/services.py` の `analyze_tweet_comprehensive` メソッド

### 4. APIをテストする

ブレークポイントを設定したら、以下の方法でAPIをトリガーします:
- ブラウザで http://localhost:3000 からフロントエンドを操作
- Swagger UI (http://localhost:8000/swagger/) からAPIを直接呼び出す
- curlやPostmanなどのツールを使用

実行がブレークポイントで停止し、変数の検査やステップ実行が可能になります。

## デバッグ構成の詳細

### 利用可能なデバッグ設定

#### 1. Docker: Django Backend
Django バックエンドをDockerコンテナ内でデバッグします。

**使用するポート**: 5678 (debugpy)

**パスマッピング**:
- ローカル: `${workspaceFolder}/backend`
- コンテナ: `/app`

#### 2. Chrome: React Frontend
React フロントエンドをChromeでデバッグします。

**使用するポート**: 3000 (React dev server)

**ブレークポイント**: JSX/TSXファイル内のJavaScript/TypeScriptコード

#### 3. Full Stack
バックエンドとフロントエンドを同時にデバッグします。

## トラブルシューティング

### デバッガーが接続できない

**症状**: "Cannot connect to runtime process" エラー

**解決方法**:
1. バックエンドコンテナが起動しているか確認:
   ```bash
   docker-compose ps
   ```

2. debugpyがリッスンしているか確認:
   ```bash
   docker-compose logs backend
   ```
   "Debugger is active" というメッセージが表示されるはずです。

3. ポート5678が他のプロセスで使用されていないか確認:
   ```bash
   netstat -ano | findstr :5678
   ```

4. コンテナを再起動:
   ```bash
   docker-compose restart backend
   ```

### ブレークポイントで停止しない

**症状**: ブレークポイントを設定しても実行が停止しない

**解決方法**:
1. ブレークポイントが実行されるコードパスにあるか確認
2. デバッガーが正常にアタッチされているか確認(デバッグコンソールにメッセージが表示される)
3. パスマッピングが正しいか確認:
   - ローカルファイルパス: `d:\workspace\project021_x_scraper\auto-ski-info-subscribe\backend\...`
   - コンテナ内パス: `/app/...`

### コードの変更が反映されない

**症状**: コードを変更してもデバッガーが古いコードを実行する

**解決方法**:
1. Djangoの自動リロードを待つ(数秒)
2. バックエンドコンテナを再起動:
   ```bash
   docker-compose restart backend
   ```
3. デバッガーを再アタッチ(F5)

## 便利なVS Codeタスク

以下のタスクは `Ctrl+Shift+P` → `Tasks: Run Task` から実行できます:

- **docker-compose-debug-up**: デバッグモードでコンテナを起動
- **docker-compose-down**: すべてのコンテナを停止
- **docker-compose-logs**: バックエンドのログを表示
- **docker-compose-restart-backend**: バックエンドコンテナを再起動
- **docker-exec-migrate**: データベースマイグレーションを実行
- **docker-exec-makemigrations**: マイグレーションファイルを生成
- **docker-exec-shell**: Django shellを起動

## デバッグのベストプラクティス

### 1. ログ出力と併用する

デバッガーだけでなく、ログ出力も活用しましょう:

```python
import logging
logger = logging.getLogger(__name__)

def my_view(request):
    logger.debug(f"Request data: {request.data}")
    # デバッグ処理...
```

ログを確認:
```bash
docker-compose logs -f backend
```

### 2. 条件付きブレークポイント

特定の条件でのみ停止するブレークポイントを設定できます:
1. ブレークポイントを右クリック
2. "ブレークポイントの編集"を選択
3. 条件式を入力(例: `user.id == 123`)

### 3. ウォッチ式

変数の値を追跡するには:
1. デバッグビューの「ウォッチ」セクション
2. 「+」ボタンをクリック
3. 変数名や式を入力(例: `len(tweets)`, `user.is_active`)

### 4. デバッグコンソール

デバッグ中に式を評価するには:
1. デバッグコンソールタブを開く
2. Python式を入力して実行
3. 変数の値を確認したり、関数を呼び出したりできます

## 参考リンク

- [VS Code Python Debugging](https://code.visualstudio.com/docs/python/debugging)
- [debugpy Documentation](https://github.com/microsoft/debugpy)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
