# 环境变量迁移指南：GEMINI_API_KEY → AI_API_KEY_GOOGLE

## 📋 变更概述

为了与 Google Cloud Secret Manager 保持一致，我们将所有环境变量从 `GEMINI_API_KEY` 重命名为 `AI_API_KEY_GOOGLE`。

## 🔄 需要更新的位置

### 1. 系统环境变量

#### Windows (PowerShell)

```powershell
# 删除旧的环境变量
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', $null, 'User')

# 设置新的环境变量
[System.Environment]::SetEnvironmentVariable('AI_API_KEY_GOOGLE', 'your-gemini-api-key', 'User')

# 重启 PowerShell 使其生效
```

#### macOS/Linux (bash/zsh)

```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
# 删除旧行：
# export GEMINI_API_KEY="your-key"

# 添加新行：
export AI_API_KEY_GOOGLE="your-gemini-api-key"

# 重新加载配置
source ~/.bashrc  # 或 source ~/.zshrc
```

### 2. 本地 .env 文件

更新 `backend/.env`:

```bash
# 旧配置 ❌
GEMINI_API_KEY=your-api-key

# 新配置 ✅
AI_API_KEY_GOOGLE=your-api-key
```

### 3. Docker Compose 环境变量

如果你在命令行传递环境变量：

```bash
# 旧方式 ❌
GEMINI_API_KEY=your-key docker-compose up

# 新方式 ✅
AI_API_KEY_GOOGLE=your-key docker-compose up
```

### 4. Google Cloud Secret Manager

如果已经在 GCP 创建了密钥，需要：

**选项 A: 重命名现有密钥（推荐）**

⚠️ **Secret Manager 不支持直接重命名**，需要创建新密钥并删除旧密钥：

```bash
# 1. 获取现有密钥值
OLD_VALUE=$(gcloud secrets versions access latest --secret=GEMINI_API_KEY)

# 2. 创建新密钥
echo -n "$OLD_VALUE" | gcloud secrets create AI_API_KEY_GOOGLE --data-file=-

# 3. 授予 Cloud Run 访问权限
gcloud secrets add-iam-policy-binding AI_API_KEY_GOOGLE \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor"

# 4. 验证新密钥
gcloud secrets versions access latest --secret=AI_API_KEY_GOOGLE

# 5. 删除旧密钥（谨慎操作！）
# gcloud secrets delete GEMINI_API_KEY
```

**选项 B: 保持两个密钥（过渡期）**

代码已经配置为优先使用 `AI_API_KEY_GOOGLE`，如果不存在则回退到 `GEMINI_API_KEY`：

```python
# backend/auto_ski_info/settings.py
GEMINI_API_KEY = config('AI_API_KEY_GOOGLE', default='')
```

这样可以在过渡期保持兼容性。

## ✅ 验证迁移

### 1. 验证系统环境变量

```bash
# Windows
echo $env:AI_API_KEY_GOOGLE

# macOS/Linux
echo $AI_API_KEY_GOOGLE
```

### 2. 验证 Django 配置

```bash
cd backend
python manage.py shell

>>> from django.conf import settings
>>> settings.GEMINI_API_KEY
'your-api-key-should-appear-here'
```

### 3. 验证 Docker 环境

```bash
docker-compose up -d backend
docker-compose exec backend env | grep AI_API_KEY_GOOGLE
```

### 4. 验证 GCP Secret Manager

```bash
gcloud secrets versions access latest --secret=AI_API_KEY_GOOGLE
```

## 🚀 部署到 Cloud Run

更新后的 `cloudbuild.yaml` 已经配置为使用 `AI_API_KEY_GOOGLE`：

```yaml
--set-secrets=AI_API_KEY_GOOGLE=AI_API_KEY_GOOGLE:latest
```

部署时会自动从 Secret Manager 读取。

## 📝 已更新的文件

以下文件已更新：

### 配置文件

- ✅ `.env.example`
- ✅ `backend/.env`
- ✅ `docker-compose.yml`
- ✅ `docker-compose.dev.yml`
- ✅ `cloudbuild.yaml` (已经使用 AI_API_KEY_GOOGLE)
- ✅ `cloudbuild.optimized.yaml` (已经使用 AI_API_KEY_GOOGLE)

### 文档文件

- ✅ `README.md`
- ✅ `LOCAL_SETUP.md`
- ✅ `LOCAL_DEV_WINDOWS.md`
- ✅ `CONFIGURATION.md`
- ✅ `VSCODE_DEBUG.md`

### 代码文件

- ✅ `backend/auto_ski_info/settings.py` (已经支持两个变量名)
- ✅ `backend/ai_service/services.py` (使用 settings.GEMINI_API_KEY)

## 🔍 向后兼容

`settings.py` 已配置为向后兼容：

```python
# 优先使用新变量名，如果不存在则保持为空
GEMINI_API_KEY = config('AI_API_KEY_GOOGLE', default='')
```

这意味着：

1. ✅ 优先读取 `AI_API_KEY_GOOGLE`
2. ✅ 如果都不存在，返回空字符串

## ⚠️ 注意事项

1. **系统环境变量需要重启**

   - Windows: 重启 PowerShell
   - macOS/Linux: 执行 `source ~/.bashrc`

2. **Docker 需要重新构建**

   ```bash
   docker-compose down
   docker-compose up --build
   ```

3. **GCP 部署需要重新部署**

   ```bash
   gcloud builds submit --config=cloudbuild.yaml
   ```

4. **确保 Secret Manager 中有正确的密钥**
   - 密钥名称：`AI_API_KEY_GOOGLE`
   - 值：你的 Gemini API Key

## 🆘 故障排查

### 问题 1: AI 服务无法工作

```bash
# 检查环境变量是否设置
echo $AI_API_KEY_GOOGLE

# 检查 Django 能否读取
cd backend
python manage.py shell -c "from django.conf import settings; print(settings.GEMINI_API_KEY)"
```

### 问题 2: Docker 容器无法读取环境变量

```bash
# 确保系统环境变量已设置
echo $AI_API_KEY_GOOGLE

# 重新启动容器
docker-compose down
docker-compose up -d
```

### 问题 3: GCP 部署失败

```bash
# 检查 Secret Manager 中是否有密钥
gcloud secrets list | grep AI_API_KEY_GOOGLE

# 检查权限
gcloud secrets get-iam-policy AI_API_KEY_GOOGLE
```

## 📚 相关文档

- [Google Cloud Secret Manager 文档](https://cloud.google.com/secret-manager/docs)
- [Django-decouple 文档](https://github.com/henriquebastos/python-decouple)
- [Docker Compose 环境变量](https://docs.docker.com/compose/environment-variables/)

---

**迁移完成后记得删除旧的环境变量和 GCP Secret！**
