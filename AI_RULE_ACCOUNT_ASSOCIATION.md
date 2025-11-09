# AI 推荐规则账号关联功能

## 功能概述

现在 AI 推荐规则可以关联到特定的 Twitter 账号，允许你为不同的账号设置不同的推荐规则。

## 数据库变更

### 新增字段

- `AIPromptRule.target_accounts`: 多对多关系字段，关联到`XAccount`
- 如果`target_accounts`为空，规则将应用到用户的所有监控账号
- 如果设置了特定账号，规则仅应用到这些账号

### 迁移文件

- `0007_aipromptrule_target_accounts.py`: 添加账号关联字段

## API 变更

### AIPromptRuleSerializer

**新增字段**:

```json
{
  "id": 1,
  "name": "白马47滑雪场推文",
  "prompt": "筛选白马47相关推文...",
  "target_accounts": [1, 3, 5], // 账号ID数组
  "target_account_details": [
    // 只读字段，显示账号详情
    {
      "id": 1,
      "username": "hakuba47",
      "display_name": "白马47スキー場",
      "avatar_url": "https://..."
    }
  ],
  "is_active": true,
  "recommended_count": 15
}
```

## 前端功能

### AI 规则管理页面 (`AIRulesPage.js`)

#### 新增功能

1. **账号选择器**: 创建/编辑规则时可以选择要应用的账号
2. **应用账号列显示**: 表格中显示规则关联的账号
3. **全部账号标识**: 如果没有选择账号，显示"全部账号"标签

#### 使用方法

**创建规则时**:

1. 点击"新建规则"
2. 填写规则名称和提示词
3. 在"应用账号"下拉框中选择要应用的账号（可多选）
4. 留空表示应用到所有账号
5. 点击确定

**编辑规则时**:

- 已选择的账号会自动填充到表单中
- 可以添加或删除账号

## 后端逻辑

### AIRecommendationService.apply_rule_to_user_tweets()

**逻辑改进**:

```python
# 如果规则指定了target_accounts，只使用这些账户
target_accounts = prompt_rule.target_accounts.all()
if target_accounts.exists():
    accounts = target_accounts.filter(user=user)
    # 只对指定账号的推文进行筛选
else:
    accounts = user.x_accounts.all()
    # 对所有账号的推文进行筛选
```

## 使用场景

### 场景 1: 滑雪场特定账号

```
规则名称: 白马47滑雪场推文
应用账号: @hakuba47, @hakuba_info
提示词: 筛选白马47滑雪场相关信息...
```

### 场景 2: 新闻类账号

```
规则名称: 滑雪新闻推荐
应用账号: @ski_news_jp, @snow_japan
提示词: 筛选日本滑雪相关新闻...
```

### 场景 3: 通用规则

```
规则名称: 降雪信息
应用账号: (留空 - 应用到所有账号)
提示词: 筛选所有提到降雪的推文...
```

## 测试步骤

1. **创建多个监控账号**

   - 添加至少 3 个 Twitter 账号到监控列表

2. **创建特定账号规则**

   - 创建规则 A，选择账号 1 和账号 2
   - 创建规则 B，选择账号 3
   - 创建规则 C，不选择账号（应用到全部）

3. **应用规则并验证**

   - 应用规则 A，验证只筛选账号 1 和 2 的推文
   - 应用规则 B，验证只筛选账号 3 的推文
   - 应用规则 C，验证筛选所有账号的推文

4. **查看推荐结果**
   - 在"AI 推荐推文"页面查看结果
   - 验证每条推荐的来源账号正确

## API 端点

### 创建规则

```http
POST /api/monitor/ai/rules/
Content-Type: application/json

{
  "name": "白马47滑雪场推文",
  "prompt": "筛选白马47相关推文...",
  "target_accounts": [1, 3, 5],  // 可选，账号ID数组
  "is_active": true
}
```

### 更新规则

```http
PATCH /api/monitor/ai/rules/{id}/
Content-Type: application/json

{
  "target_accounts": [1, 2]  // 更新关联账号
}
```

### 应用规则

```http
POST /api/monitor/ai/rules/{id}/apply/
Content-Type: application/json

{
  "date_filter": "today"  // today, week, all
}
```

响应会只包含从规则关联账号筛选出的推文。

## 注意事项

1. **账号权限**: 只能选择当前用户自己监控的账号
2. **空值处理**: `target_accounts`为空数组`[]`表示应用到所有账号
3. **编辑规则**: 修改`target_accounts`会立即生效，下次应用规则时使用新的账号列表
4. **已有推荐**: 修改账号关联不会影响已经生成的推荐记录

## 数据库查询优化

- 使用`select_related`和`prefetch_related`优化查询
- 序列化器中使用`SerializerMethodField`展示账号详情
- 避免 N+1 查询问题

## 未来改进

- [ ] 添加账号标签/分组功能
- [ ] 批量设置规则的应用账号
- [ ] 规则模板功能
- [ ] 账号推荐规则统计
