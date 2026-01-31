# 🔐 技能包配置说明

## 概述

本仓库包含多个自动化技能，部分技能需要配置敏感信息（API密钥、授权码等）。为了保护您的账号安全，我们采用了**本地配置文件**的方案。

---

## 🚀 快速开始

### 步骤1：识别需要配置的技能

以下技能包含配置文件，需要单独设置：

| 技能包 | 配置文件 | 用途 |
|--------|----------|------|
| **file-share** | `email_config.local.json` | 文件邮件发送功能 |
| **telegram-control** | `config.local.json` | Telegram Bot令牌 |
| **telegram-control** | `llm_config.local.json` | LLM API密钥 |

### 步骤2：创建本地配置文件

每个需要配置的技能都提供了模板文件（`.json`），您需要：

1. 复制模板文件：
   ```bash
   cp email_config.json email_config.local.json
   cp config.json config.local.json
   cp llm_config.json llm_config.local.json
   ```

2. 编辑 `.local.json` 文件，填入真实信息

### 步骤3：填写配置信息

#### 📧 file-share/email_config.local.json

```json
{
  "sender": "your_email@qq.com",           // 您的QQ邮箱
  "password": "smtp_authorization_code",   // QQ邮箱SMTP授权码（非登录密码）
  "receiver": "receiver@qq.com",           // 接收文件的邮箱
  "type": "1"                              // 1=QQ邮箱
}
```

**如何获取QQ邮箱SMTP授权码：**
1. 登录QQ邮箱网页版
2. 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启"POP3/SMTP服务"
4. 生成授权码（不是QQ密码！）

---

#### 🤖 telegram-control/config.local.json

```json
{
  "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz",  // Telegram Bot Token
  "chat_id": "123456789",                               // 您的Telegram Chat ID
  "allowed_users": ["123456789"],                       // 允许使用的用户ID列表
  "default_receiver": "your_email@qq.com"               // 默认接收邮箱
}
```

**如何获取Telegram Bot Token：**
1. 在Telegram中搜索 @BotFather
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称
4. 保存返回的Token

**如何获取Chat ID：**
1. 在Telegram中搜索 @userinfobot
2. 发送任意消息
3. 机器人会返回您的Chat ID

---

#### 🧠 telegram-control/llm_config.local.json

```json
{
  "llm_provider": "openai",                    // 使用的LLM提供商
  "openai_api_key": "sk-proj-...",             // OpenAI API密钥
  "openai_model": "gpt-4o",                    // 使用的模型
  "anthropic_api_key": "",                     // Anthropic API密钥（可选）
  "max_tokens": 1000,                          // 最大token数
  "temperature": 0.1                           // 温度参数
}
```

**如何获取OpenAI API Key：**
1. 访问 https://platform.openai.com/api-keys
2. 登录账号
3. 点击"Create new secret key"
4. 复制并保存密钥（只显示一次！）

---

## ⚠️ 安全注意事项

### ✅ 安全实践

- ✅ 所有 `.local.json` 文件已被 `.gitignore` 排除，**不会上传到Git**
- ✅ 模板文件只包含占位符，**不包含真实敏感信息**
- ✅ 配置文件采用JSON格式，**易于管理和版本控制**

### 🚫 禁止行为

- ❌ **永远不要**将 `.local.json` 文件添加到Git
- ❌ **永远不要**在公开场合分享API密钥、密码或Token
- ❌ **不要**使用简单的密码作为授权码
- ❌ **不要**在代码中硬编码敏感信息

### 🔒 密钥泄露应急处理

如果您怀疑密钥已泄露：

1. **立即撤销密钥**
   - OpenAI: https://platform.openai.com/api-keys
   - Telegram: 通过 @BotFather 撤销
   - QQ邮箱: 重新生成SMTP授权码

2. **生成新密钥**
   - 按照上述步骤重新生成
   - 更新 `.local.json` 文件
   - 不要复用旧密钥

3. **检查使用记录**
   - 查看API调用日志
   - 确认是否有异常使用

---

## 📋 配置检查清单

使用前请确认：

- [ ] 所有 `.local.json` 文件已创建
- [ ] 配置信息已正确填写
- [ ] `.gitignore` 已生效（运行 `git check-ignore *.local.json` 测试）
- [ ] 敏感信息未出现在Git历史中
- [ ] 密钥权限设置正确（chmod 600）

---

## 🛠️ 故障排除

### 问题1：技能无法启动

**可能原因**：配置文件不存在或格式错误

**解决方案**：
```bash
# 检查文件是否存在
ls -la email_config.local.json

# 验证JSON格式
python -m json.tool email_config.local.json
```

### 问题2：认证失败

**可能原因**：密钥错误或过期

**解决方案**：
1. 检查密钥是否完整复制
2. 确认密钥未过期
3. 检查API权限是否正确

### 问题3：Git警告本地文件被跟踪

**可能原因**：.gitignore 配置无效

**解决方案**：
```bash
# 清除Git缓存
git rm -r --cached .

# 重新添加
git add .
git commit -m "修复：更新.gitignore规则"
```

---

## 📞 需要帮助？

如果您在配置过程中遇到问题：

1. 查看技能包的 `SKILL.md` 文档
2. 检查配置文件的注释说明
3. 确认API密钥权限和有效期

---

**最后更新**：2026-01-31
**维护者**：您的编剧小助理
