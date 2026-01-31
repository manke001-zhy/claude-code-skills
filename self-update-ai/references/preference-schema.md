# 偏好配置结构说明

本文档详细说明了自更新 AI 偏好配置文件的结构和各个字段的含义。

## 配置文件位置

```
~/.claude/self-update-ai/preferences.json
```

## 完整配置结构

```json
{
  "version": "1.0",
  "created_at": "2026-01-24T10:00:00",
  "updated_at": "2026-01-24T10:00:00",
  "writing_style": {
    "sentence_length": "medium",
    "max_sentences_per_paragraph": 5,
    "prefer_short_sentences": false,
    "forbidden_words": [],
    "preferred_words": []
  },
  "content_structure": {
    "intro_max_sentences": 3,
    "conclusion_first": false,
    "use_transitions": true,
    "bullet_points_preferred": false,
    "use_subheadings": false
  },
  "tone": {
    "formality": "neutral",
    "verbosity": "medium"
  },
  "custom_rules": [],
  "feedback_history": []
}
```

## 字段说明

### 元数据

- `version` (string): 配置文件版本号
- `created_at` (ISO datetime): 配置文件创建时间
- `updated_at` (ISO datetime): 最后更新时间

### writing_style（写作风格）

#### sentence_length
- **类型**: string
- **可选值**: "short" | "medium" | "long"
- **默认值**: "medium"
- **说明**: 句子长度偏好
  - "short": 简短有力，10字以内
  - "medium": 中等长度，10-20字
  - "long": 较长句子，可以超过20字

#### max_sentences_per_paragraph
- **类型**: integer
- **默认值**: 5
- **说明**: 每段最大句子数
  - 1-3: 非常简洁，适合要点列表
  - 4-7: 标准段落
  - 8+: 较长段落

#### prefer_short_sentences
- **类型**: boolean
- **默认值**: false
- **说明**: 是否偏好短句
  - true: 优先使用短句
  - false: 句子长度可变

#### forbidden_words
- **类型**: array of strings
- **默认值**: []
- **说明**: 禁用词汇列表
  - 示例: ["首先", "其次", "总而言之"]

#### preferred_words
- **类型**: array of strings
- **默认值**: []
- **说明**: 优先使用词汇列表
  - 示例: ["关键", "核心", "重点"]

### content_structure（内容结构）

#### intro_max_sentences
- **类型**: integer
- **默认值**: 3
- **说明**: 开头部分最大句子数
  - 1: 直接进入主题
  - 2-3: 简短引入
  - 4+: 较长引入

#### conclusion_first
- **类型**: boolean
- **默认值**: false
- **说明**: 是否先说结论
  - true: 结论优先（BLUF - Bottom Line Up Front）
  - false: 按常规逻辑展开

#### use_transitions
- **类型**: boolean
- **默认值**: true
- **说明**: 是否使用过渡句
  - true: 段落之间使用过渡
  - false: 直接切换话题

#### bullet_points_preferred
- **类型**: boolean
- **默认值**: false
- **说明**: 是否偏好要点列表
  - true: 优先使用列表形式
  - false: 优先使用段落形式

#### use_subheadings
- **类型**: boolean
- **默认值**: false
- **说明**: 是否使用小标题
  - true: 长内容中使用小标题组织
  - false: 不使用小标题

### tone（语气）

#### formality
- **类型**: string
- **可选值**: "casual" | "neutral" | "formal"
- **默认值**: "neutral"
- **说明**: 正式程度
  - "casual": 随意，口语化
  - "neutral": 中性，平衡
  - "formal": 正式，专业

#### verbosity
- **类型**: string
- **可选值**: "concise" | "medium" | "detailed"
- **默认值**: "medium"
- **说明**: 详细程度
  - "concise": 简洁，只说重点
  - "medium": 适中，平衡细节和简洁
  - "detailed": 详细，包含更多背景和解释

### custom_rules（自定义规则）

- **类型**: array of objects
- **默认值**: []
- **说明**: 用户特定的自定义规则

每个规则对象包含：
```json
{
  "id": "rule_1",
  "description": "规则描述",
  "pattern": "匹配模式（可选）",
  "created_at": "2026-01-24T10:00:00"
}
```

### feedback_history（反馈历史）

- **类型**: array of objects
- **默认值**: []
- **说明**: 所有用户反馈的历史记录

每条反馈包含：
```json
{
  "timestamp": "2026-01-24T10:00:00",
  "category": "writing_style",
  "key": "forbidden_words",
  "value": "首先",
  "reason": "用户不喜欢用首先开头"
}
```

只保留最近 50 条反馈记录。

## 配置使用示例

### 读取配置

```python
from scripts.update_preferences import load_preferences

prefs = load_preferences()

# 检查是否应该使用短句
if prefs['writing_style']['prefer_short_sentences']:
    # 使用短句风格
    pass

# 获取禁用词汇列表
forbidden = prefs['writing_style']['forbidden_words']
```

### 更新配置

```python
from scripts.update_preferences import add_forbidden_word, add_feedback

# 添加禁用词
add_forbidden_word("首先", "用户不喜欢用首先")

# 更新配置项
add_feedback("writing_style", "sentence_length", "short", "用户偏好短句")
```

## 配置迁移

当配置结构需要更新时：

1. 增加 `version` 字段
2. 在 `load_preferences()` 中添加迁移逻辑
3. 保留向后兼容性
