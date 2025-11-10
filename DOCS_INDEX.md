# 文档索引

本项目的文档结构已经过精简和优化，保留了最核心和最有用的文档。

## 📚 核心文档

### [README.md](README.md) - 项目主文档 ⭐

**必读文档**，包含项目的完整介绍、架构说明、使用指南和配置方法。

**适合人群**: 所有用户

**内容概览**:

- 项目简介和核心特性
- 技术架构详解
- 快速开始指南
- Cookie 获取方法
- MCP 资源接口说明
- 故障排查指南
- 安全与合规说明

---

## 🚀 快速开始

### [QUICK_START.md](QUICK_START.md) - 5 分钟快速部署指南

**新手友好**的快速上手教程，手把手教您部署系统。

**适合人群**: 第一次使用本项目的用户

**内容概览**:

- 详细的 Cookie 获取步骤（含截图说明）
- 环境变量配置示例
- Docker Compose 启动流程
- 添加监控账号的操作步骤
- 常见问题解答

---

## 🛠️ 开发与调试

### [DOCKER_DEBUG.md](DOCKER_DEBUG.md) - Docker 容器调试指南

在 Docker 容器内进行实时调试，支持代码热重载。

**适合人群**: 需要修改代码或调试的开发者

**内容概览**:

- Docker 开发环境配置
- 容器内调试方法
- 代码热重载设置
- 日志查看技巧

### [VSCODE_DEBUG.md](VSCODE_DEBUG.md) - VS Code 调试配置

VS Code 编辑器的调试配置和使用方法。

**适合人群**: 使用 VS Code 的开发者

**内容概览**:

- VS Code 调试配置文件
- 断点调试技巧
- 前端和后端联合调试
- 调试面板使用指南

### [LOCAL_DEV_WINDOWS.md](LOCAL_DEV_WINDOWS.md) - Windows 本地开发指南

在 Windows 环境下不使用 Docker 的本地开发配置。

**适合人群**: Windows 用户，不想使用 Docker

**内容概览**:

- Windows 本地环境搭建
- Python 虚拟环境配置
- Node.js 前端开发环境
- 常见 Windows 特定问题

### [LOCAL_SETUP.md](LOCAL_SETUP.md) - 本地开发完整设置

跨平台的本地开发环境配置详解。

**适合人群**: 需要深入了解本地配置的开发者

**内容概览**:

- 前置依赖安装
- 数据库配置
- 服务启动顺序
- 环境变量详解

---

## ☁️ 生产部署

### [DEPLOYMENT_OPTIMIZATION.md](DEPLOYMENT_OPTIMIZATION.md) - Cloud Run 部署优化指南

Google Cloud Run 生产环境部署的详细说明和优化建议。

**适合人群**: 需要部署到云端的用户

**内容概览**:

- Cloud Run 资源配置优化
- 启动流程优化方案
- 成本估算和优化
- 部署故障排查
- 监控和日志查看

---

## 📖 文档使用建议

### 如果您是第一次使用：

1. ✅ 阅读 [README.md](README.md) 了解项目
2. ✅ 按照 [QUICK_START.md](QUICK_START.md) 快速部署
3. ✅ 遇到问题查看对应文档的故障排查章节

### 如果您想修改代码：

1. ✅ 参考 [DOCKER_DEBUG.md](DOCKER_DEBUG.md) 或 [VSCODE_DEBUG.md](VSCODE_DEBUG.md)
2. ✅ 根据操作系统选择 [LOCAL_DEV_WINDOWS.md](LOCAL_DEV_WINDOWS.md) 或 [LOCAL_SETUP.md](LOCAL_SETUP.md)

### 如果您想部署到生产环境：

1. ✅ 完整阅读 [DEPLOYMENT_OPTIMIZATION.md](DEPLOYMENT_OPTIMIZATION.md)
2. ✅ 参考其中的部署步骤和优化建议
3. ✅ 关注成本和监控配置

---

## 🗑️ 已清理的文档

以下文档已被删除或合并到新文档中：

### 开发过程临时文档（已删除）

- `AI_RULE_ACCOUNT_ASSOCIATION.md`
- `AUTHENTICATED_SCRAPER_GUIDE.md`
- `COOKIE_FIX_COMPLETE.md`
- `DEBUG.md`
- `DELETE_TWEETS_FEATURE.md`
- `ENV_MIGRATION_GUIDE.md`
- `ENV_UPDATE_REPORT.md`
- `FEATURE_SUMMARY.md`
- `FETCH_LATEST_FEATURE.md`
- `FIX_COOKIE_UPLOAD.md`
- `FIXED_SETTINGS_PAGE.md`
- `FRONTEND_INTEGRATION_COMPLETE.md`
- `GCP_PERMISSION_FIX.md`
- `GOOGLE_LOGIN_SOLUTIONS.md`
- `IMPLEMENTATION_SUMMARY.md`
- `MIGRATION_CHECKLIST.md`
- `MIGRATION_COMPLETE.md`
- `MONITORING_CONTROL_GUIDE.md`
- `MONITORING_QUICKSTART.md`
- `MONITORING_SCHEDULE.md`
- `MONITORING_UI_DEMO.md`
- `QUICK_FIX.md`
- `QUICK_TEST_GUIDE.md`
- `QUICK_TEST_WEB_LOGIN.md`
- `SCRAPER_SOLUTIONS_SUMMARY.md`
- `SMART_SCHEDULING_DEPLOYMENT.md`
- `TIMEOUT_FIX_AND_COOKIE_UPLOAD.md`
- `TWEET_FIXES.md`
- `TWITTER_SCRAPING.md`
- `UI_VISUALIZATION.md`
- `WEB_BUTTON_LOGIN_GUIDE.md`
- `WEB_LOGIN_ARCHITECTURE.md`
- `WEB_LOGIN_README.md`

### 重复或过时文档（已删除）

- `CLOUD_DEPLOYMENT_COST_OPTIMIZATION.md` - 已合并到 `DEPLOYMENT_OPTIMIZATION.md`
- `CONFIGURATION.md` - 已整合到 `README.md`
- `MINIMAL_DEPLOY_GUIDE.md` - 已合并到 `DEPLOYMENT_OPTIMIZATION.md`
- `START_HERE.md` - 已被 `QUICK_START.md` 替代
- `DEPLOY.md` - 已被 `DEPLOYMENT_OPTIMIZATION.md` 替代
- `DOCKER_QUICKSTART.md` - 已整合到 `DOCKER_DEBUG.md`

---

## 💡 文档维护原则

本项目的文档遵循以下原则：

1. **简洁明了** - 只保留必要的文档，避免信息冗余
2. **用户友好** - 为不同用户群体提供对应的文档
3. **持续更新** - 随着项目发展更新文档内容
4. **实用至上** - 聚焦实际使用场景和常见问题

---

## 📞 反馈与建议

如果您觉得文档有需要改进的地方，欢迎：

- 提交 [Issue](https://github.com/cyohei9907/auto-ski-info-subscribe/issues)
- 提交 [Pull Request](https://github.com/cyohei9907/auto-ski-info-subscribe/pulls)
- 参与 [讨论](https://github.com/cyohei9907/auto-ski-info-subscribe/discussions)

---

**最后更新**: 2025-11-10
