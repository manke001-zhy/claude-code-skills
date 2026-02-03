---
name: self-update-ai
description: 自更新 AI 技能 - 让 AI 记住并应用用户的反馈和偏好。当用户给出反馈时（如"开头太长"、"不要用首先"、"喜欢短句"等），自动记录这些偏好并在后续对话中应用。支持实时反馈记录、偏好持久化、热加载自动生效。用于需要 AI 适应个人写作风格、沟通习惯、专业偏好的场景。
---

# 自更新 AI

让 AI 记住你的反馈，越用越懂你。

## 核心原理

**自更新** = 把用户的反馈变成 AI 的习惯。你说一次，它记一辈子。

传统 AI 的痛点：每次对话从零开始，你的积累全部清零。
自更新 AI 的优势：每次反馈都被记录，形成复利效应，越用越顺手。

## 使用方式

### 方式一：自然反馈（推荐）

在使用过程中随时给出反馈，AI 会自动识别并记录：

**写作风格反馈**：
- "开头太长了，控制在 3 句以内"
- "不要用'首先'、'其次'这种词"
- "我喜欢用短句，不要长段落"
- "这段太啰嗦了，简洁一点"

**内容结构反馈**：
- "先说结论，再解释原因"
- "用要点列表，不要大段文字"
- "每段要有小标题"

**语气偏好**：
- "太正式了，随意一点"
- "要专业一点，不要太口语化"
- "简洁明了，不要啰嗦"

### 方式二：明确命令

使用 `/自更新` 命令明确固化反馈：

```
/自更新 开头控制在 3 句以内
/自更新 不要用"首先"、"其次"
/自更新 用短句，不要长段落
/自更新 禁用词汇：总之、因此
```

### 方式三：查看当前配置

```
查看我的偏好
显示当前配置
我的偏好设置
```

## 技术实现

### 配置文件位置

```
~/.claude/self-update-ai/preferences.json
```

### 配置结构

偏好配置包含以下类别：

1. **writing_style**（写作风格）
   - sentence_length: 句子长度
   - max_sentences_per_paragraph: 每段最大句数
   - prefer_short_sentences: 偏好短句
   - forbidden_words: 禁用词汇
   - preferred_words: 优先词汇

2. **content_structure**（内容结构）
   - intro_max_sentences: 开头最大句数
   - conclusion_first: 先说结论
   - bullet_points_preferred: 偏好要点列表
   - use_subheadings: 使用小标题

3. **tone**（语气）
   - formality: 正式程度 (casual/neutral/formal)
   - verbosity: 详细程度 (concise/medium/detailed)

4. **custom_rules**（自定义规则）
   - 用户特定的个性化规则

### 热加载机制

配置文件修改后，下次对话自动生效，无需重启。

### 脚本工具

使用 `scripts/update_preferences.py` 管理配置：

```bash
# 显示当前配置
python scripts/update_preferences.py show

# 添加配置
python scripts/update_preferences.py add writing_style prefer_short_sentences true

# 添加禁用词
python scripts/update_preferences.py forbid "首先" "用户不喜欢"

# 添加自定义规则
python scripts/update_preferences.py rule "函数名用驼峰命名法"
```

## 工作流程

### 第一次使用

1. 用户首次给出反馈
2. AI 自动创建配置文件（使用默认值）
3. 记录用户反馈到相应类别
4. 立即应用到当前和后续对话

### 后续使用

1. 每次对话开始时，自动加载配置文件
2. 根据配置调整输出风格
3. 用户新的反馈被追加记录
4. 配置文件持续优化

### 反馈处理

当识别到用户反馈时：

1. **识别类别**：判断反馈属于哪个类别（写作风格、内容结构、语气、自定义）
2. **提取信息**：从反馈中提取具体的偏好设置
3. **更新配置**：使用脚本更新配置文件
4. **确认应用**：告知用户已记录，并在后续中应用

示例对话：

```
用户：开头太长了，控制在 3 句以内
AI：✓ 已记录：开头最多 3 句。以后我会注意控制开头长度。

用户：不要用"首先"、"其次"这种词
AI：✓ 已添加禁用词：首先、其次。我会避免使用这些词。
```

## 反馈模式参考

详细的反馈模式和配置映射关系，参考：[references/feedback-patterns.md](references/feedback-patterns.md)

## 配置结构说明

完整的配置结构和字段说明，参考：[references/preference-schema.md](references/preference-schema.md)

## 安全注意事项

### 敏感信息管理

当用户反馈涉及"登录"、"保存状态"等功能时，需要特别注意敏感信息的保护。

**详细的安全最佳实践**：[references/security-best-practices.md](references/security-best-practices.md)

#### 核心原则

**永远不要将敏感信息硬编码到代码中或提交到版本控制系统。**

#### 敏感信息类型

1. **登录凭证**：cookies、tokens、sessions
2. **用户数据**：用户名、密码、个人信息
3. **缓存数据**：storage state、localStorage
4. **API 密钥**：api keys、secret keys、access tokens

#### 推荐方案：.env 文件模式

适用场景：需要存储 API 密钥、数据库凭证等敏感信息

```
my-skill/
├── .env.example          # 模板文件（✅ 可提交）
├── .env.local            # 实际配置（❌ 不可提交）
├── .gitignore            # 包含 .env.local
└── script.js
```

**使用方式**：
```bash
# 1. 复制模板
cp .env.example .env.local

# 2. 填入实际值
vim .env.local

# 3. 代码中读取
const apiKey = process.env.API_KEY;
```

#### Cookies 缓存模式

适用场景：浏览器自动化、需要保持登录状态

**目录结构**：
```
my-skill/
├── .cache/
│   ├── weibo-cookies.json      # 登录 cookies
│   └── weibo-storage.json      # localStorage
├── .gitignore
└── script.js
```

**必须添加到 .gitignore**：
```
.cache/
*.cookies.json
*-storage.json
sessions/
```

#### Git 安全检查

每次提交代码前，必须检查：

```bash
# 查看暂存文件
git status

# 查看暂存文件列表
git diff --cached --name-only

# 检查是否包含敏感关键词
git diff --cached | grep -i "password\|secret\|token\|cookie\|session\|credential"
```

如果发现敏感文件：
```bash
# 从暂存区移除
git reset HEAD [敏感文件路径]

# 确保已在 .gitignore 中
echo "敏感文件模式" >> .gitignore
```

#### 清理登录状态

如需清除登录状态：
```bash
# 删除缓存目录
rm -rf ~/.claude/skills/[skill-name]/.cache/

# 或删除特定文件
rm ~/.claude/skills/[skill-name]/.cache/*.cookies.json
```

#### 不要记录到偏好

- ❌ 不要在 preferences.json 中存储密码、token
- ❌ 不要在 custom_rules 中包含具体凭证
- ✅ 只记录"需要支持登录缓存"这样的行为偏好

### 最佳实践

### 给用户的建议

1. **具体明确**：越具体的反馈，效果越好
   - 好："开头控制在 3 句以内"
   - 差："开头不要太长"

2. **持续反馈**：每次对话中发现不符合习惯的地方，及时反馈
   - "这里不对，应该这样"
   - "这个风格我喜欢，以后都这样"

3. **分步固化**：先用 `/自更新` 命令固化关键偏好
   - "开头太长" → `/自更新 开头控制在 3 句内`
   - "喜欢短句" → `/自更新 优先使用短句`

### 给 AI 的建议

1. **主动识别**：在对话中主动识别用户的反馈意图
2. **确认记录**：记录后明确告知用户已记住
3. **立即应用**：在当前对话中就开始应用新记录的偏好
4. **定期回顾**：在长期对话中，回顾和确认偏好是否符合用户期望

## 示例场景

### 场景一：写作助手

用户：帮我写一篇文章介绍人工智能

AI：（生成文章，使用默认风格）

用户：开头太长了，控制在 3 句以内

AI：✓ 已记录：开头最多 3 句。让我重新写：

（重新生成，开头控制在 3 句内）

用户：对了，不要用"首先"、"其次"这种词

AI：✓ 已添加禁用词：首先、其次。好的，我会注意。

（后续文章自动应用这些偏好）

### 场景二：代码审查

用户：帮我 review 这段代码

AI：（给出建议）

用户：函数名要用驼峰命名法，不要用下划线

AI：✓ 已记录规则：函数名用驼峰命名法。我会记住这个偏好。

（后续代码审查自动应用此规则）

### 场景三：日常对话

用户：太正式了，随意一点

AI：✓ 已记录：语气设为 casual（随意）。好的，那我们就轻松一点聊。

用户：对，就这样，简洁明了

AI：✓ 已记录：详细程度设为 concise（简洁）。了解！

（后续对话保持这个风格）

## 优势总结

1. **复利效应**：每次反馈都在让 AI 更懂你
2. **无需重复**：说一次就记住，不用每次重复
3. **热加载**：改了立即生效，无需重启
4. **持续进化**：AI 随着你的习惯变化而变化

未来不是人和 AI 的竞争，是「人+AI」和「人+AI」的竞争。差距在于你的 AI 有没有在成长。自更新让你的 AI 持续进化，积累竞争优势。
