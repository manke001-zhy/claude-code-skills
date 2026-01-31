# 自更新反馈模式参考

本文档描述了常见的用户反馈模式以及如何在自更新系统中处理这些反馈。

## 反馈分类

### 1. 写作风格反馈

**模式**：用户对写作风格、用词、句式等的偏好

**示例**：
- "开头太长了，控制在 3 句以内"
- "不要用'首先'、'其次'这种词"
- "我喜欢用短句，不要长段落"
- "这段太啰嗦了"

**处理方式**：
- `writing_style.sentence_length`: "short" / "medium" / "long"
- `writing_style.max_sentences_per_paragraph`: 数字
- `writing_style.forbidden_words`: 字符串数组
- `writing_style.preferred_words`: 字符串数组

### 2. 内容结构反馈

**模式**：用户对内容组织、结构安排的偏好

**示例**：
- "先说结论，再解释原因"
- "用要点列表，不要大段文字"
- "每段要有小标题"

**处理方式**：
- `content_structure.conclusion_first`: true/false
- `content_structure.bullet_points_preferred`: true/false
- `content_structure.use_subheadings`: true/false

### 3. 语气和正式程度

**模式**：用户对语气、正式程度的偏好

**示例**：
- "太正式了，随意一点"
- "要专业一点，不要太口语化"
- "简洁明了，不要啰嗦"

**处理方式**：
- `tone.formality`: "casual" / "neutral" / "formal"
- `tone.verbosity`: "concise" / "medium" / "detailed"

### 4. 自定义规则

**模式**：用户提出的特定、个性化的要求

**示例**：
- "代码注释要用中文"
- "函数名要用驼峰命名法"
- "每行代码不超过 80 字符"

**处理方式**：
- `custom_rules`: 数组，包含规则对象
  ```json
  {
    "id": "rule_1",
    "description": "函数名用驼峰命名法",
    "pattern": "function_names",
    "created_at": "2026-01-24T10:00:00"
  }
  ```

## 常见反馈短语映射

| 用户短语 | 配置字段 | 值 |
|---------|---------|---|
| "开头太长" | `content_structure.intro_max_sentences` | 3 |
| "不要用首先其次" | `writing_style.forbidden_words` | ["首先", "其次"] |
| "用短句" | `writing_style.prefer_short_sentences` | true |
| "不要太啰嗦" | `tone.verbosity` | "concise" |
| "用要点列表" | `content_structure.bullet_points_preferred` | true |
| "随意一点" | `tone.formality` | "casual" |
| "专业一点" | `tone.formality` | "formal" |

## 反馈处理流程

1. **识别反馈类别**：判断用户反馈属于哪个类别
2. **提取关键信息**：从用户语言中提取具体的偏好设置
3. **更新配置**：使用脚本更新偏好配置文件
4. **确认应用**：告知用户已记录，并在后续中应用

## 模糊反馈处理

当用户的反馈不够明确时，应该：

1. **询问澄清**：主动询问用户具体要求
2. **提供选项**：给出几个可能的选项供用户选择
3. **记录意图**：即使不够具体，也记录用户的意图方向

示例：
- 用户："这里不太好"
- AI："您是指内容、结构还是表达方式？可以具体说明一下吗？"
