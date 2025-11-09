# 环境变量迁移 Checklist

## ✅ 已完成的更改（开发者已完成）

- [x] 更新 `.env.example`
- [x] 更新 `backend/.env`
- [x] 更新 `docker-compose.yml`
- [x] 更新 `docker-compose.dev.yml`
- [x] 验证 `cloudbuild.yaml` 使用 `AI_API_KEY_GOOGLE`
- [x] 验证 `cloudbuild.optimized.yaml` 使用 `AI_API_KEY_GOOGLE`
- [x] 更新 `README.md`
- [x] 更新 `LOCAL_SETUP.md`
- [x] 更新 `LOCAL_DEV_WINDOWS.md`
- [x] 更新 `CONFIGURATION.md`
- [x] 更新 `VSCODE_DEBUG.md`
- [x] 更新 `backend/auto_ski_info/settings.py`
- [x] 创建 `ENV_MIGRATION_GUIDE.md`
- [x] 创建 `ENV_UPDATE_REPORT.md`
- [x] 创建验证脚本 `verify_env.ps1`
- [x] 创建验证脚本 `backend/verify_env.py`

## 📋 用户需要执行的操作

### 步骤 1: 设置新的环境变量

#### Windows (PowerShell - 管理员权限)

```powershell
# 设置新的环境变量
[System.Environment]::SetEnvironmentVariable('AI_API_KEY_GOOGLE', 'your-gemini-api-key', 'User')

# 验证设置
echo $env:AI_API_KEY_GOOGLE

# 重启 PowerShell
```

#### macOS/Linux (bash/zsh)

```bash
# 编辑配置文件
nano ~/.bashrc  # 或 nano ~/.zshrc

# 添加以下行
export AI_API_KEY_GOOGLE="your-gemini-api-key"

# 保存后重新加载
source ~/.bashrc  # 或 source ~/.zshrc

# 验证设置
echo $AI_API_KEY_GOOGLE
```

- [ ] 已设置系统环境变量 `AI_API_KEY_GOOGLE`
- [ ] 已验证环境变量设置成功

### 步骤 2: 运行验证脚本

#### Windows

```powershell
# 在项目根目录运行
.\verify_env.ps1
```

#### macOS/Linux + Python

```bash
cd backend
python verify_env.py
```

- [ ] 验证脚本运行成功
- [ ] 没有警告或错误信息

### 步骤 3: 删除旧的环境变量（可选但推荐）

#### Windows

```powershell
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', $null, 'User')
```

#### macOS/Linux

```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
# 删除或注释掉这一行：
# export GEMINI_API_KEY="your-key"

source ~/.bashrc  # 或 source ~/.zshrc
```

- [ ] 已删除旧的环境变量 `GEMINI_API_KEY`

### 步骤 4: 重启本地服务

#### 如果使用 Docker

```bash
# 停止所有容器
docker-compose down

# 重新启动（会自动读取新的环境变量）
docker-compose up -d

# 查看日志确认启动成功
docker-compose logs backend
```

#### 如果直接运行 Python

```bash
# 重启终端或重新加载环境变量后
cd backend
python manage.py runserver
```

- [ ] 服务已重启
- [ ] 没有环境变量相关的错误

### 步骤 5: 测试 AI 功能

```bash
# 访问前端
# http://localhost:3000

# 测试 AI 推荐功能
# 1. 登录系统
# 2. 进入 "AI推荐规则" 页面
# 3. 创建一个新规则
# 4. 应用规则到推文
```

- [ ] AI 推荐功能正常工作
- [ ] 没有 API 密钥相关的错误

### 步骤 6: GCP 部署（如需要）

#### 创建 Secret Manager 密钥

```bash
# 创建 AI_API_KEY_GOOGLE
echo -n "your-gemini-api-key" | gcloud secrets create AI_API_KEY_GOOGLE --data-file=-

# 创建 DATABASE_PASSWORD
echo -n "your-database-password" | gcloud secrets create DATABASE_PASSWORD --data-file=-

# 授予访问权限（替换 YOUR_SERVICE_ACCOUNT）
gcloud secrets add-iam-policy-binding AI_API_KEY_GOOGLE \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding DATABASE_PASSWORD \
  --member="serviceAccount:YOUR_SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### 验证 Secret

```bash
# 列出所有 secrets
gcloud secrets list

# 验证值
gcloud secrets versions access latest --secret=AI_API_KEY_GOOGLE
gcloud secrets versions access latest --secret=DATABASE_PASSWORD
```

#### 部署到 Cloud Run

```bash
# 使用优化后的配置部署
gcloud builds submit --config=cloudbuild.optimized.yaml

# 或使用标准配置
gcloud builds submit --config=cloudbuild.yaml
```

- [ ] Secret Manager 中已创建 `AI_API_KEY_GOOGLE`
- [ ] Secret Manager 中已创建 `DATABASE_PASSWORD`
- [ ] 已授予正确的访问权限
- [ ] Cloud Run 部署成功
- [ ] 生产环境 AI 功能正常

## 🔍 故障排查

### 问题 1: 环境变量未生效

**症状**: `verify_env.ps1` 显示环境变量未设置

**解决方案**:

```powershell
# 确认设置到了正确的作用域
[System.Environment]::GetEnvironmentVariable('AI_API_KEY_GOOGLE', 'User')
[System.Environment]::GetEnvironmentVariable('AI_API_KEY_GOOGLE', 'Process')

# 重启 PowerShell 或终端
```

### 问题 2: Docker 容器无法读取环境变量

**症状**: `docker-compose logs backend` 显示 API key 为空

**解决方案**:

```bash
# 检查 docker-compose 是否继承了环境变量
docker-compose config

# 确保系统环境变量已设置
echo $AI_API_KEY_GOOGLE

# 重新构建并启动
docker-compose down
docker-compose up --build -d
```

### 问题 3: AI 功能报错

**症状**: 应用 AI 规则时出错

**解决方案**:

```bash
# 检查 Django 是否读取到了 API key
cd backend
python manage.py shell

>>> from django.conf import settings
>>> print(settings.GEMINI_API_KEY)

# 如果为空，检查 .env 文件
cat .env | grep AI_API_KEY_GOOGLE
```

### 问题 4: GCP 部署失败

**症状**: Cloud Build 或 Cloud Run 报错

**解决方案**:

```bash
# 检查 Secret 是否存在
gcloud secrets list | grep AI_API_KEY_GOOGLE

# 检查 Service Account 权限
gcloud secrets get-iam-policy AI_API_KEY_GOOGLE

# 查看 Cloud Run 日志
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

## 📚 相关文档

- 📖 [完整迁移指南](./ENV_MIGRATION_GUIDE.md)
- 📖 [更新报告](./ENV_UPDATE_REPORT.md)
- 📖 [配置说明](./CONFIGURATION.md)
- 📖 [本地开发设置](./LOCAL_SETUP.md)

## ✨ 完成确认

当所有复选框都被勾选后，环境变量迁移即完成！

- [ ] 所有步骤都已完成
- [ ] 本地开发环境正常
- [ ] Docker 环境正常（如使用）
- [ ] GCP 生产环境正常（如已部署）
- [ ] AI 功能测试通过
- [ ] 没有任何环境变量相关的错误

**🎉 恭喜！环境变量迁移成功完成！**
