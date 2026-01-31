# 配置OpenAI API - 快速指南

## 步骤1：获取OpenAI API Key

1. 访问 OpenAI 平台：https://platform.openai.com/api-keys
2. 登录你的 OpenAI 账号（如果没有账号，需要先注册）
3. 点击 "+ Create new secret key" 按钮
4. 给 key 起个名字（如 "Telegram Bot"）
5. 点击 "Create secret key"
6. **重要**：立即复制 key（格式：`sk-...`），因为它只显示一次！

## 步骤2：配置 API Key

编辑文件：`C:\Users\manke\.claude\skills\telegram-control\llm_config.json`

```json
{
  "llm_provider": "openai",
  "openai_api_key": "sk-你的key粘贴到这里",
  "openai_model": "gpt-3.5-turbo",
  "anthropic_api_key": "",
  "note": "已配置OpenAI API"
}
```

## 步骤3：重启 Bot

重启后 Bot 会自动使用 OpenAI 来理解你的意图！

## 支持的模型

- `gpt-3.5-turbo`（推荐，快速便宜）
- `gpt-4`（更智能，但稍慢且费用更高）

可以在配置文件中修改 `openai_model` 字段来切换模型。

## 费用说明

- GPT-3.5 Turbo：约 $0.001-0.002 / 次对话
- GPT-4：约 $0.03-0.06 / 次对话

通常使用 GPT-3.5 Turbo 就足够了！

## 配置示例

```json
{
  "llm_provider": "openai",
  "openai_api_key": "sk-proj-abc123xyz456...",
  "openai_model": "gpt-3.5-turbo"
}
```

## 测试

配置完成后，在 Telegram 中发送：

```
那个小说发我邮箱
```

Bot 应该能理解你想要发送"科幻小说.pdf"到邮箱！

---

**配置好后重启 Bot 即可使用智能意图理解功能！**
