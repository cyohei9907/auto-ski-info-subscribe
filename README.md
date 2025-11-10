# Auto Ski Info Subscribe# Auto Ski Info Subscribe

**X（Twitter）账号推文订阅系统** - 基于 Cookie 认证的推文自动抓取与 MCP 资源分发 X（Twitter）スキー場情報自動監視システム - React + Django + Gemini AI

## 📋 项目简介## 📋 概要

本项目是一个自动化的 X（Twitter）推文订阅系统，通过使用**用户自己的 Cookie** 来绕过 API 限制，实现对特定账号推文的实时监控和收集。收集到的推文数据可以通过 **MCP（Model Context Protocol）** 协议推送给其他服务使用。このプロジェクトは、X（Twitter）上の特定のアカウントを監視し、スキー場に関する情報を自動収集・分析するシステムです。Gemini AI を使用してツイートの感情分析や重要度評価を行い、有用な情報を効率的に取得できます。

### 🎯 核心特性## 🚀 主な機能

- **🔐 Cookie 认证**：使用您自己的 X 账号 Cookie，无需申请官方 API### 🔧 コア機能

- **📡 自动监控**：定时（默认 15 分钟）自动抓取指定账号的最新推文

- **🤖 AI 分析**：集成 Google Gemini AI 进行情感分析、内容摘要和主题提取- **アカウント監視**: 指定した X アカウントを 15 分間隔で自動監視

- **🔌 MCP 集成**：将推文作为资源通过 MCP 协议暴露给其他服务- **リアルタイム収集**: 新しいツイートを自動的に取得・保存

- **🎨 可视化界面**：React 前端提供友好的账号管理和推文浏览界面- **AI 分析**: Gemini AI による感情分析、要約、トピック抽出

- **☁️ 云端部署**：支持 Google Cloud Run 一键部署- **重要度評価**: スキー場関連情報の重要度を自動判定

## 🏗️ 技术架构### 👤 ユーザー機能

### 前端- **ユーザー認証**: 登録・ログイン機能

- **React 18** + **Ant Design** - 现代化 UI- **アカウント管理**: 監視対象の追加・削除・設定変更

- **React Query** - 数据状态管理- **ツイート閲覧**: 収集したツイートと AI 分析結果の表示

- **フィルタリング**: 感情、重要度、アカウント別での絞り込み

### 后端- **ログ管理**: 監視実行履歴とエラー情報の確認

- **Django 4.2** + **Django REST Framework** - RESTful API

- **Playwright** - 无头浏览器，模拟真实用户访问 X### 🔍 AI 機能

- **Celery** + **Redis** - 定时任务调度

- **Google Gemini AI** - 推文内容智能分析- **感情分析**: ポジティブ・ネガティブ・ニュートラル判定

- **自動要約**: ツイート内容の簡潔な要約生成

### 部署- **トピック抽出**: 主要キーワードとトピックの自動抽出

- **Docker** + **Docker Compose** - 容器化部署- **重要度スコア**: スキー場情報の関連性と重要度の数値化

- **Nginx** - 反向代理和静态文件服务

- **Google Cloud Run** - 无服务器容器托管## 🏗️ システム構成

- **Cloud SQL** - 生产环境数据库（PostgreSQL）

### フロントエンド

## 🚀 快速开始

- **React 18**: モダンなユーザーインターフェース

### 前置要求- **Ant Design**: 統一された美しい UI コンポーネント

- **React Query**: 効率的なデータ取得・キャッシュ管理

- Docker & Docker Compose- **React Router**: SPA 用ルーティング

- 您的 X（Twitter）账号 Cookie

- Google Gemini API Key（可选，用于 AI 分析）### バックエンド

### 1. 获取 X Cookie- **Django 4.2**: 堅牢な Web フレームワーク

- **Django REST Framework**: RESTful API 構築

#### 方法 1：浏览器开发者工具- **Celery**: 非同期タスク処理（15 分間隔の監視）

- **Redis**: Celery メッセージブローカー

1. 登录 [X（Twitter）](https://twitter.com)- **drf-yasg**: Swagger API ドキュメント自動生成

2. 按 `F12` 打开开发者工具

3. 切换到 `Application` / `Storage` 标签### AI・外部サービス

4. 选择 `Cookies` → `https://twitter.com`

5. 找到以下关键 Cookie：- **Google Gemini AI**: 高度な自然言語処理

   - `auth_token` - 认证令牌（必需）- **X (Twitter) API v2**: ツイートデータ取得

   - `ct0` - CSRF 令牌（必需）- **PostgreSQL**: メインデータベース

- **Google Cloud SQL**: 本番環境データベース

#### 方法 2：使用浏览器插件

### インフラ・デプロイ

推荐使用 [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie) 等插件一键导出所有 Cookie。

- **Docker**: コンテナ化による環境統一

### 2. 配置环境变量- **Google Cloud Run**: サーバーレスコンテナホスティング

- **Google Cloud Build**: CI/CD パイプライン

复制环境变量模板并填入您的配置：- **Nginx**: フロントエンド用 Web サーバー

````bash## 📁 プロジェクト構成

# 后端配置

cp backend/.env.example backend/.env```

auto-ski-info-subscribe/

# 编辑 backend/.env├── README.md

```├── docker-compose.yml          # 開発環境用Docker設定

├── cloudbuild.yaml            # Cloud Build設定

**backend/.env 配置示例**：├── deploy.sh                  # デプロイスクリプト

├── .gitignore

```ini├──

# ===== X Cookie 认证（必需） =====├── backend/                   # Django バックエンド

X_COOKIE_AUTH_TOKEN=你的_auth_token_值│   ├── Dockerfile

X_COOKIE_CT0=你的_ct0_值│   ├── entrypoint.sh

│   ├── requirements.txt

# ===== AI 服务（可选） =====│   ├── manage.py

AI_API_KEY_GOOGLE=你的_Gemini_API_Key│   ├── .env.example

│   ├──

# ===== 数据库配置 =====│   ├── auto_ski_info/         # Django メイン設定

# 本地开发使用 SQLite，无需额外配置│   │   ├── __init__.py

USE_CLOUD_SQL=False│   │   ├── settings.py        # Django 設定

DATABASE_URL=sqlite:///data/db.sqlite3│   │   ├── urls.py           # URL ルーティング

│   │   ├── wsgi.py

# ===== Django 配置 =====│   │   ├── asgi.py

DEBUG=True│   │   └── celery.py         # Celery 設定

SECRET_KEY=your-secret-key-for-local-dev│   ├──

ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0│   ├── accounts/              # ユーザー認証アプリ

```│   │   ├── models.py         # User, UserProfile モデル

│   │   ├── serializers.py    # API シリアライザー

### 3. 启动服务│   │   ├── views.py          # 認証API エンドポイント

│   │   └── urls.py

```bash│   ├──

# 克隆仓库│   ├── x_monitor/             # X監視アプリ

git clone https://github.com/cyohei9907/auto-ski-info-subscribe.git│   │   ├── models.py         # XAccount, Tweet, MonitoringLog モデル

cd auto-ski-info-subscribe│   │   ├── services.py       # X API クライアント

│   │   ├── tasks.py          # Celery タスク（15分間隔実行）

# 启动所有服务（后端、前端、Redis、Celery）│   │   ├── serializers.py

docker-compose up -d│   │   ├── views.py          # 監視API エンドポイント

│   │   └── urls.py

# 查看启动日志│   └──

docker-compose logs -f│   └── ai_service/            # AI分析アプリ

│       ├── services.py       # Gemini AI サービス

# 等待服务就绪（约 30-60 秒）│       └── urls.py           # AI API エンドポイント

```├──

└── frontend/                  # React フロントエンド

### 4. 访问应用    ├── Dockerfile

    ├── nginx.conf            # Nginx 設定

- **前端界面**: http://localhost:3000    ├── package.json

- **后端 API**: http://localhost:8000    ├── .env.example

- **API 文档**: http://localhost:8000/swagger/    ├── public/

- **管理后台**: http://localhost:8000/admin/    │   └── index.html

  - 默认用户名: `admin`    └── src/

  - 默认密码: `admin@123`        ├── index.js          # アプリエントリーポイント

        ├── App.js           # メインアプリコンポーネント

## 📖 使用说明        ├── index.css        # グローバルスタイル

        ├──

### 添加监控账号        ├── components/       # 再利用可能コンポーネント

        │   └── MainLayout.js # メインレイアウト

1. 访问前端界面 http://localhost:3000        ├──

2. 注册/登录账号        ├── pages/           # ページコンポーネント

3. 进入"账号管理"页面        │   ├── LoginPage.js     # ログイン・登録ページ

4. 点击"添加账号"按钮        │   ├── DashboardPage.js # ダッシュボード

5. 填写表单：        │   ├── AccountsPage.js  # アカウント管理

   - **X 用户名**: 目标账号的 username（如 `@elonmusk` 填写 `elonmusk`）        │   ├── TweetsPage.js    # ツイート一覧

   - **显示名称**: 自定义备注名（可选）        │   └── LogsPage.js      # 監視ログ

   - **启用监控**: 勾选后系统会自动定时抓取        ├──

        ├── contexts/        # React Context

### 查看推文数据        │   └── AuthContext.js   # 認証状態管理

        └──

- **自动抓取**: 系统每 15 分钟自动抓取已启用账号的最新推文        └── services/        # API サービス

- **手动触发**: 在账号列表中点击"立即监控"按钮            └── api.js       # API クライアント

- **推文列表**: 查看所有收集的推文，支持筛选和搜索```

- **AI 分析**: 查看情感分析、自动摘要和主题标签

## 🛠️ 開発環境セットアップ

### MCP 资源接口

### 前提条件

推文数据通过 MCP（Model Context Protocol）协议暴露，可被支持 MCP 的客户端访问：

- Docker & Docker Compose

#### 获取单条推文资源- X (Twitter) API キー

- Google Gemini API キー

```http

GET /api/mcp/tweets/{tweet_id}/**注意**: ローカル開発環境では **SQLite** を使用します（PostgreSQL 不要）

````

### クイックスタート

**响应示例**：

#### 1. システム環境変数に API キーを設定

````json

{**Windows (PowerShell)**

  "uri": "mcp://tweets/1234567890",

  "name": "Tweet from @username",```powershell

  "description": "A tweet about skiing conditions",[System.Environment]::SetEnvironmentVariable('X_API_KEY', 'your-key', 'User')

  "mimeType": "application/json",[System.Environment]::SetEnvironmentVariable('X_API_SECRET', 'your-secret', 'User')

  "text": "Great snow conditions at the resort today! ❄️",[System.Environment]::SetEnvironmentVariable('X_ACCESS_TOKEN', 'your-token', 'User')

  "metadata": {[System.Environment]::SetEnvironmentVariable('X_ACCESS_TOKEN_SECRET', 'your-secret', 'User')

    "author": "username",[System.Environment]::SetEnvironmentVariable('X_BEARER_TOKEN', 'your-bearer', 'User')

    "author_name": "User Display Name",[System.Environment]::SetEnvironmentVariable('AI_API_KEY_GOOGLE', 'your-gemini-key', 'User')

    "created_at": "2025-11-10T12:00:00Z",# PowerShell を再起動

    "sentiment": "positive",```

    "sentiment_score": 0.85,

    "summary": "用户分享了今日雪场的良好雪况",**macOS/Linux (bash/zsh)**

    "topics": ["滑雪", "雪况", "度假村"],

    "tweet_url": "https://twitter.com/username/status/1234567890"```bash

  }export X_API_KEY="your-key"

}export X_API_SECRET="your-secret"

```export X_ACCESS_TOKEN="your-token"

export X_ACCESS_TOKEN_SECRET="your-secret"

#### 获取账号推文列表export X_BEARER_TOKEN="your-bearer"

export AI_API_KEY_GOOGLE="your-gemini-key"

```http# ~/.bashrc または ~/.zshrc に追加して永続化

GET /api/mcp/accounts/{account_id}/tweets/```

````

#### 2. リポジトリのクローンと起動

#### 搜索推文

````bash

```httpgit clone https://github.com/cyohei9907/auto-ski-info-subscribe.git

GET /api/mcp/tweets/search/?q=关键词&sentiment=positive&limit=10cd auto-ski-info-subscribe

````

# Docker Compose で全サービスを起動

**MCP 客户端示例**（Python）：docker-compose up -d

```python# ログを確認

import requestsdocker-compose logs -f

```

# 获取推文资源

response = requests.get('http://localhost:8000/api/mcp/tweets/1234567890/')#### 3. アクセス

tweet_resource = response.json()

- **フロントエンド**: http://localhost:3000

print(f"URI: {tweet_resource['uri']}")- **バックエンド API**: http://localhost:8000

print(f"内容: {tweet_resource['text']}")- **Swagger UI**: http://localhost:8000/swagger/

print(f"情感: {tweet_resource['metadata']['sentiment']}")- **Django Admin**: http://localhost:8000/admin/

print(f"摘要: {tweet_resource['metadata']['summary']}") - ユーザー名: `admin`

``` - パスワード:`admin@123`

## 🐳 开发调试### データベース

### Docker 容器内调试- **ローカル**: SQLite (`backend/data/db.sqlite3`)

- **本番**: Cloud SQL PostgreSQL (`ski-scrapy`)

项目支持在 Docker 容器内进行实时调试，代码修改即时生效：

詳細な手順は [LOCAL_SETUP.md](LOCAL_SETUP.md) を参照してください。

#### 使用 PowerShell 脚本（Windows）

## 🐛 Docker で実時調试（推荐）

```powershell

# 启动开发环境### VS Code 集成调试环境

.\docker-dev.ps1

本项目支持在 Docker 容器中运行并实时调试，无需本地安装 Python 和 Node.js：

# 选择操作：

# 1 - 首次构建#### 快速开始

# 2 - 启动服务

# 9 - 数据库迁移1. **使用 PowerShell 脚本**（推荐）：

```

```powershell

#### VS Code 调试配置   .\docker-dev.ps1

```

1. 按 `Ctrl+Shift+D` 打开调试面板

2. 选择 `🐳 Docker: Full Stack Debug` 选择操作：

3. 按 `F5` 开始调试

   - `1` - 首次构建镜像

支持的调试配置： - `2` - 启动服务

- **Docker: Full Stack Debug** - 前端 + 后端同时调试 - `9` - 运行数据库迁移

- **Docker: Backend (Remote)** - 后端 API 调试（端口 5678）

- **Docker: Celery Worker (Remote)** - Celery 任务调试（端口 5679）2. **VS Code 调试**：

- **Docker: Frontend (Chrome)** - React 前端调试 - 按 `Ctrl+Shift+D` 打开调试面板

  - 选择 `🐳 Docker: Full Stack Debug`

详细文档： - 按 `F5` 开始调试

- [DOCKER_DEBUG.md](DOCKER_DEBUG.md) - 完整调试指南

- [VSCODE_DEBUG.md](VSCODE_DEBUG.md) - VS Code 配置详解#### 功能特性

## ☁️ 生产环境部署 ✅ **代码热重载** - 修改代码立即生效，无需重启容器

✅ **实时断点调试** - 在容器中运行的代码设置断点

### Google Cloud Run 部署 ✅ **前后端同时调试** - 同时调试 Django 和 React

✅ **隔离环境** - 完全在容器中运行，不影响本地环境

#### 1. 准备 GCP 环境 ✅ **团队一致** - 所有开发者使用相同的环境

```bash#### 调试配置

# 安装 gcloud CLI

# https://cloud.google.com/sdk/docs/install- **🐳 Docker: Full Stack Debug** - 完整的前后端调试

- **🐳 Docker: All Services Debug** - 包含 Celery 的全部服务调试

# 认证并设置项目- **Docker: Backend (Remote)** - 仅调试后端（端口 5678）

gcloud auth login- **Docker: Celery Worker (Remote)** - 调试 Celery 任务（端口 5679）

gcloud config set project YOUR_PROJECT_ID- **Docker: Frontend (Chrome)** - 调试 React 前端



# 启用必要的 API#### 访问地址

gcloud services enable \

  cloudbuild.googleapis.com \- 前端：http://localhost:3000

  run.googleapis.com \- 后端：http://localhost:8000

  sqladmin.googleapis.com \- Swagger：http://localhost:8000/swagger/

  secretmanager.googleapis.com- 调试端口：5678 (Backend), 5679 (Celery), 5680 (Beat)

```

**详细文档**：

#### 2. 创建 Cloud SQL 数据库

- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - 快速开始指南

```bash- [DOCKER_DEBUG.md](DOCKER_DEBUG.md) - 完整调试文档

# 创建 PostgreSQL 实例- [VSCODE_DEBUG.md](VSCODE_DEBUG.md) - VS Code 本地调试配置

gcloud sql instances create ai-project-database \

  --database-version=POSTGRES_14 \## 🌐 本番環境デプロイ（Google Cloud）

  --tier=db-f1-micro \

  --region=asia-northeast1### 前提条件



# 创建数据库- Google Cloud プロジェクト: `gen-lang-client-0543160602`

gcloud sql databases create ski-scrapy \- Cloud SQL インスタンス: `ai-project-database`

  --instance=ai-project-database- データベース名: `ski-scrapy`

- gcloud CLI インストール・認証済み

# 设置密码

gcloud sql users set-password postgres \### デプロイ手順

  --instance=ai-project-database \

  --password=YOUR_PASSWORD#### 1. Secret Manager に API キーを設定

```

````bash

#### 3. 配置 Secret Manager# 自動セットアップスクリプトを実行

chmod +x setup-secrets.sh

```bash./setup-secrets.sh gen-lang-client-0543160602

# 运行自动配置脚本```

chmod +x setup-secrets.sh

./setup-secrets.sh YOUR_PROJECT_ID設定するシークレット:



# 按提示输入以下密钥：- `DATABASE_PASSWORD` - Cloud SQL パスワード

# - DATABASE_PASSWORD: Cloud SQL 数据库密码- `AI_API_KEY_GOOGLE` - Gemini API キー

# - AI_API_KEY_GOOGLE: Gemini API Key- `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`, `X_BEARER_TOKEN` - Twitter API 認証情報

# - X_COOKIE_AUTH_TOKEN: 您的 X auth_token

# - X_COOKIE_CT0: 您的 X ct0 token#### 2. アプリケーションをデプロイ

````

````bash

#### 4. 部署应用# デプロイスクリプトを実行

chmod +x deploy.sh

```bash./deploy.sh gen-lang-client-0543160602

# 一键部署（自动构建 + 部署）```

chmod +x deploy.sh

./deploy.sh YOUR_PROJECT_ID#### 3. 自動監視の設定



# 或使用 Cloud BuildCloud Scheduler が 15 分ごとに自動実行されます（cloudbuild.yaml で自動設定）

gcloud builds submit --config=cloudbuild.yaml

詳細な手順とトラブルシューティングは [DEPLOY.md](DEPLOY.md) を参照してください。

# 部署完成后会输出服务 URL

# 示例：https://auto-ski-info-backend-xxx-asia-northeast1.a.run.app## 📊 API ドキュメント

````

本番環境にデプロイ後、以下のエンドポイントで API ドキュメントにアクセス可能：

#### 5. 验证部署

- **Swagger UI**: https://your-backend-url.run.app/swagger/

````bash- **ReDoc**: https://your-backend-url.run.app/redoc/

# 检查服务健康状态

curl https://your-service-url.run.app/health### 主要エンドポイント



# 访问前端#### 認証

# 浏览器打开：https://your-service-url.run.app/

- `POST /api/auth/register/` - ユーザー登録

# 查看 API 文档- `POST /api/auth/login/` - ログイン

# https://your-service-url.run.app/swagger/- `POST /api/auth/logout/` - ログアウト

```- `GET /api/auth/user/` - ユーザー情報取得



#### 资源配置说明#### X 監視



当前配置（`cloudbuild.yaml`）：- `GET /api/monitor/accounts/` - 監視アカウント一覧

- **CPU**: 4 核- `POST /api/monitor/accounts/` - アカウント追加

- **内存**: 4Gi- `POST /api/monitor/accounts/{id}/monitor/` - 手動監視実行

- **超时**: 600 秒- `GET /api/monitor/tweets/` - ツイート一覧

- **实例数**: 0-10（自动扩缩容）- `POST /api/monitor/tweets/{id}/analyze/` - AI 分析実行



**预估成本**：#### AI サービス

- 无流量时：$0/月（实例缩容到 0）

- 低流量：~$10-20/月- `POST /api/ai/sentiment/` - 感情分析

- 中等流量：~$50-100/月- `POST /api/ai/summarize/` - テキスト要約

- `POST /api/ai/topics/` - トピック抽出

详细优化指南：[DEPLOYMENT_OPTIMIZATION.md](DEPLOYMENT_OPTIMIZATION.md)

## 🔧 設定とカスタマイズ

## 📁 项目结构

### 監視間隔の変更

````

auto-ski-info-subscribe/```python

├── README.md # 本文档# backend/auto_ski_info/celery.py

├── docker-compose.yml # 本地开发环境配置 app.conf.beat_schedule = {

├── cloudbuild.yaml # Cloud Build CI/CD 配置 'monitor-x-accounts': {

├── Dockerfile # 生产环境多阶段构建 'task': 'x_monitor.tasks.monitor_all_active_accounts',

├── nginx.combined.conf # Nginx 配置（前端服务 + API 代理） 'schedule': crontab(minute='\*/15'), # 15 分間隔を変更

├── supervisord.combined.conf # 进程管理器（Nginx + Gunicorn） },

│}

├── backend/ # Django 后端```

│ ├── manage.py

│ ├── requirements.txt # Python 依赖### AI プロンプトのカスタマイズ

│ ├── entrypoint.sh # 容器启动脚本

│ │```python

│ ├── auto_ski_info/ # Django 主配置# backend/ai_service/services.py の GeminiService クラス内

│ │ ├── settings.py # 项目设置# analyze_tweet_sentiment, summarize_tweet, extract_topics メソッド内の

│ │ ├── urls.py # 全局路由# プロンプト文字列を編集

│ │ └── celery.py # Celery 配置```

│ │

│ ├── accounts/ # 用户认证模块## 🐛 トラブルシューティング

│ │ ├── models.py # User, UserProfile

│ │ └── views.py # 注册、登录 API### よくある問題と解決方法

│ │

│ ├── x_monitor/ # X 监控模块（核心）#### 1. X API エラー

│ │ ├── models.py # XAccount, Tweet, MonitoringLog

│ │ ├── services/ ```bash

│ │ │ └── cookie_scraper.py # 基于 Cookie 的爬虫# API キーとレート制限を確認

│ │ ├── tasks.py # Celery 定时任务# .env ファイルの X\_\* 変数を確認

│ │ └── views.py # 监控 API```

│ │

│ ├── ai_service/ # AI 分析模块#### 2. Gemini API エラー

│ │ ├── services.py # Gemini AI 集成

│ │ └── views.py # 分析 API```bash

│ │# API キーと quota を確認

│ └── mcp_service/ # MCP 协议模块# AI_API_KEY_GOOGLE が正しく設定されているか確認

│ ├── views.py # MCP 资源接口```

│ └── serializers.py # MCP 格式序列化器

│#### 3. データベース接続エラー

└── frontend/ # React 前端

    ├── package.json```bash

    ├── public/# Cloud SQL インスタンスの状態確認

    └── src/# データベース認証情報の確認

        ├── pages/            # 页面组件```

        │   ├── LoginPage.js         # 登录注册

        │   ├── DashboardPage.js     # 仪表盘#### 4. Celery タスクが実行されない

        │   ├── AccountsPage.js      # 账号管理

        │   ├── TweetsPage.js        # 推文列表```bash

        │   └── LogsPage.js          # 监控日志# Redis の動作確認

        │# Celery worker の起動確認

        ├── services/docker-compose logs celery

        │   └── api.js        # API 客户端封装```

        │

        └── contexts/## 📈 監視・ログ

            └── AuthContext.js # 认证状态管理

````### ログの場所



## 🔧 配置与定制- **Django**: Cloud Run ログまたは stdout

- **Celery**: Redis キューと Cloud Run ログ

### 调整监控频率- **監視ログ**: データベース（MonitoringLog テーブル）



编辑 `backend/auto_ski_info/celery.py`：### メトリクス監視



```python- Google Cloud Monitoring での Cloud Run メトリクス

app.conf.beat_schedule = {- API エラー率とレスポンス時間

    'monitor-x-accounts': {- データベース接続状況

        'task': 'x_monitor.tasks.monitor_all_active_accounts',

        'schedule': crontab(minute='*/15'),  # 修改间隔：*/30 表示 30 分钟## 🤝 貢献

    },

}1. このリポジトリをフォーク

```2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)

3. 変更をコミット (`git commit -m 'Add amazing feature'`)

### 自定义 AI 提示词4. ブランチにプッシュ (`git push origin feature/amazing-feature`)

5. プルリクエストを作成

编辑 `backend/ai_service/services.py` 的 `GeminiService` 类：

## 📄 ライセンス

```python

def analyze_tweet_sentiment(self, text):このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

    prompt = f"""

    针对滑雪场信息推文，分析情感倾向：## 📞 サポート



    推文内容：{text}- 問題報告: [GitHub Issues](https://github.com/cyohei9907/auto-ski-info-subscribe/issues)

    - ドキュメント: この README と API ドキュメント

    返回：positive / negative / neutral- 連絡先: cyohei9907@example.com

    以及简短理由。

    """## 🔄 更新履歴

    # ...

```### v1.0.0 (2025-11-05)



### Cookie 过期处理- 初期リリース

- X (Twitter) アカウント監視機能

X Cookie 有效期通常为数周至数月。当出现认证错误时：- Gemini AI による分析機能

- React フロントエンド UI

1. 重新登录 X 获取新 Cookie- Google Cloud Run デプロイ対応

2. 更新 `backend/.env` 中的 `X_COOKIE_AUTH_TOKEN` 和 `X_COOKIE_CT0`
3. 重启服务：
   ```bash
   docker-compose restart backend celery
````

## 🛠️ 故障排查

### Cookie 认证失败

**症状**: 日志显示 `401 Unauthorized` 或 `Authentication failed`

**解决方案**:

1. 确认 Cookie 未过期（重新从浏览器获取）
2. 检查 `.env` 中的 `X_COOKIE_AUTH_TOKEN` 和 `X_COOKIE_CT0` 拼写
3. 查看详细日志：`docker-compose logs backend | grep -i auth`

### 无法抓取推文

**症状**: 监控执行但无推文数据

**解决方案**:

1. 确认目标账号为公开账号（私密账号需 Cookie 账号已关注）
2. 检查用户名是否正确（不含 `@` 符号）
3. 查看 Playwright 日志：`docker-compose logs backend | grep -i playwright`
4. 增加超时时间（编辑 `x_monitor/services/cookie_scraper.py`）

### Celery 任务不执行

**症状**: 定时监控未触发

**解决方案**:

1. 检查 Redis 状态：`docker-compose ps redis`
2. 查看 Celery Worker 日志：`docker-compose logs celery`
3. 查看 Celery Beat 日志：`docker-compose logs celery-beat`
4. 手动测试任务：
   ```bash
   docker-compose exec backend python manage.py shell
   >>> from x_monitor.tasks import monitor_all_active_accounts
   >>> monitor_all_active_accounts.delay()
   ```

### Cloud Run 部署超时

**症状**: `Container failed to start and listen on port`

**解决方案**:

1. 检查 `cloudbuild.yaml` 资源配置（建议 4CPU + 4Gi）
2. 增加超时时间：`--timeout=600`
3. 查看完整日志：点击 Cloud Build 错误日志中的 `Logs URL`
4. 参考优化文档：[DEPLOYMENT_OPTIMIZATION.md](DEPLOYMENT_OPTIMIZATION.md)

### 前端无法访问后端 API

**症状**: 前端显示网络错误

**解决方案**:

1. 检查 CORS 配置（`backend/auto_ski_info/settings.py` 的 `CORS_ALLOWED_ORIGINS`）
2. 确认 `ALLOWED_HOSTS` 包含前端域名
3. 检查 Nginx 配置（`nginx.combined.conf`）的代理设置

## 📚 相关文档

- **[QUICK_START.md](QUICK_START.md)** - 快速开始向导
- **[DEPLOYMENT_OPTIMIZATION.md](DEPLOYMENT_OPTIMIZATION.md)** - Cloud Run 部署优化
- **[DOCKER_DEBUG.md](DOCKER_DEBUG.md)** - Docker 容器调试
- **[VSCODE_DEBUG.md](VSCODE_DEBUG.md)** - VS Code 调试配置
- **[LOCAL_DEV_WINDOWS.md](LOCAL_DEV_WINDOWS.md)** - Windows 本地开发指南

## 🔐 安全与合规

### Cookie 安全最佳实践

- ⚠️ **切勿公开分享** 您的 `auth_token` 和 `ct0` Cookie
- ✅ 使用 `.env` 文件存储，并添加到 `.gitignore`
- ✅ 生产环境使用 Secret Manager 等密钥管理服务
- ✅ 定期更新 Cookie（建议每月）
- ✅ 使用专用小号进行抓取（避免主账号风险）

### 使用限制与合规

- **遵守服务条款**: 请遵守 X（Twitter）的服务条款和 robots.txt
- **合理抓取频率**: 建议间隔 15-30 分钟，避免过于频繁
- **仅限个人使用**: 本项目仅供个人学习和研究，不得用于商业目的
- **尊重隐私**: 仅抓取公开信息，不得抓取私密内容
- **流量限制**: 注意 Cookie 账号的流量限制，避免触发 rate limit

## 🤝 贡献指南

欢迎贡献代码、提交 Issue 或建议！

### 贡献流程

1. **Fork** 本仓库
2. **创建分支**: `git checkout -b feature/your-feature`
3. **提交代码**: `git commit -m 'Add some feature'`
4. **推送分支**: `git push origin feature/your-feature`
5. **创建 Pull Request**

### 代码规范

- **Python**: 遵循 PEP 8
- **JavaScript**: 使用 ESLint 和 Prettier
- **Commit**: 使用语义化提交信息（如 `feat:`, `fix:`, `docs:`）

## 📄 许可证

本项目基于 **MIT License** 开源。详见 [LICENSE](LICENSE) 文件。

## 📞 联系与支持

- **GitHub**: [@cyohei9907](https://github.com/cyohei9907)
- **Issues**: [提交问题](https://github.com/cyohei9907/auto-ski-info-subscribe/issues)
- **Discussions**: [参与讨论](https://github.com/cyohei9907/auto-ski-info-subscribe/discussions)

---

## ⚠️ 免责声明

**本项目仅供学习和技术研究使用。**

- 使用本工具需遵守 X（Twitter）的服务条款和相关法律法规
- 使用者需自行承担使用本工具产生的一切法律责任
- 开发者不对因使用本工具导致的账号封禁或其他后果负责
- 请勿将本工具用于任何违法或侵权行为

**使用本工具即表示您已阅读并同意上述免责声明。**
