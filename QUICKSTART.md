# Quick Start Guide

快速开始指南 / Quick Start Guide

## 快速设置 (Quick Setup)

### 1. 环境准备 (Prerequisites)

```bash
# Python 3.8+
python --version

# MongoDB (可选本地或使用云服务)
# MongoDB (optional local or use cloud service)
```

### 2. 安装依赖 (Install Dependencies)

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量 (Configure Environment)

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
# Edit .env file and add your API keys
nano .env
```

必需的配置项 (Required Configuration):
- `OPENAI_API_KEY`: OpenAI API 密钥
- `TWITTER_BEARER_TOKEN`: Twitter Bearer Token
- `MONGODB_URI`: MongoDB 连接字符串
- `TWITTER_TARGET_USERS`: 要监控的 Twitter 用户名（逗号分隔）

### 4. 启动服务 (Start Service)

```bash
# 使用启动脚本 (需要先设置执行权限)
chmod +x run.sh
./run.sh

# 或直接运行
python app.py
```

服务将在 http://localhost:5000 启动

### 5. 测试 API (Test API)

```bash
# 检查服务状态
curl http://localhost:5000/health

# 获取最新研究结果
curl http://localhost:5000/api/research/latest

# 手动触发 Twitter 爬取
curl -X POST http://localhost:5000/api/crawl/twitter

# 分析自定义内容
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your post content here", "platform": "Twitter"}'
```

## 使用 Docker (Using Docker)

### 快速启动 (Quick Start)

```bash
# 使用 docker-compose 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f crawler

# 停止服务
docker-compose down
```

### 仅运行爬虫服务 (Run Crawler Only)

```bash
# 构建镜像
docker build -t ski-info-crawler .

# 运行容器
docker run -d \
  --env-file .env \
  -p 5000:5000 \
  --name crawler \
  ski-info-crawler
```

## API 端点说明 (API Endpoints)

### GET /
服务信息和端点列表

### GET /health
健康检查

### GET /api/research/latest?limit=50
获取最新的研究结果

### GET /api/research/platform/{platform}
按平台筛选研究结果
- `platform`: Twitter, Xiaohongshu

### GET /api/research/user/{username}
按用户名筛选研究结果

### POST /api/crawl/twitter
手动触发 Twitter 爬取

### POST /api/crawl/xiaohongshu
手动触发小红书爬取

### POST /api/analyze
分析自定义文本
```json
{
  "text": "要分析的文本内容",
  "platform": "Twitter"
}
```

## 配置选项 (Configuration Options)

### 爬取频率 (Crawling Interval)
```
SCRAPE_INTERVAL_HOURS=6  # 每6小时爬取一次
```

### 目标用户 (Target Users)
```
TWITTER_TARGET_USERS=user1,user2,user3
XIAOHONGSHU_TARGET_USERS=user1,user2,user3
```

### AI 模型选择 (AI Model)
```
OPENAI_MODEL=gpt-4  # 或 gpt-3.5-turbo
```

### 启用/禁用调度器 (Enable/Disable Scheduler)
```
ENABLE_SCHEDULER=true  # 设为 false 禁用自动爬取
```

## 故障排除 (Troubleshooting)

### MongoDB 连接失败
```bash
# 检查 MongoDB 是否运行
docker ps | grep mongo

# 或安装本地 MongoDB
brew install mongodb-community  # Mac
sudo apt install mongodb  # Ubuntu
```

### Twitter API 错误
- 确认 API 凭证正确
- 检查 API 访问级别
- 注意速率限制

### OpenAI API 错误
- 确认 API 密钥有效
- 检查账户余额
- 监控 token 使用量

## 运行测试 (Run Tests)

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api.py

# 显示详细输出
pytest -v

# 显示代码覆盖率
pytest --cov=.
```

## 生产部署建议 (Production Deployment)

### 使用 Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用进程管理器
```bash
# 使用 systemd 或 supervisor 管理进程
```

## 获取帮助 (Getting Help)

- 查看完整文档: README.md
- 提交问题: GitHub Issues
- 查看日志: `logs/` 目录

## 下一步 (Next Steps)

1. 配置你要监控的社交媒体账户
2. 调整爬取频率和 AI 分析参数
3. 集成到你的应用程序中
4. 设置告警和监控
5. 定制化开发新功能

---

祝使用愉快！ / Happy Crawling! 🚀
