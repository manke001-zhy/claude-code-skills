---
name: telegram-control - Telegram双向控制
description: Telegram双向控制技能 - 通过Telegram Bot与Claude Code进行双向交互。支持发送命令、接收结果、传输文件。像聊天一样控制Claude Code，即时响应，真正的双向通信。
license: MIT
---

# Telegram双向控制技能 (重构版)

## 功能说明

通过Telegram Bot实现与Claude Code的**双向交互**，像聊天一样控制你的电脑。

**v2.0重大更新**：
- 🤖 **AI驱动**：使用GPT-4o理解自然语言
- 🚀 **架构重构**：代码量减少72%(2654行→730行)
- 💬 **真正智能**：无需记忆命令格式
- 🛡️ **优雅降级**：API失败时自动切换规则匹配

## 核心特性

✅ **双向通信**：Telegram ↔ Claude Code
✅ **AI理解**：GPT-4o自然语言理解
✅ **即时响应**：命令<0.5秒，AI<2秒
✅ **文件传输**：发送/接收任意文件
✅ **自然对话**：像和朋友聊天一样
✅ **远程控制**：随时随地控制电脑
✅ **上下文记忆**：记住对话历史

## 适用场景

- 远程控制电脑执行任务
- 手机查看电脑状态
- 传输文件到电脑/从电脑获取文件
- 监控脚本执行状态
- 移动端办公

## 配置步骤

### 1. 创建 Telegram Bot

1. 在Telegram中搜索 **@BotFather**
2. 发送命令 `/newbot`
3. 按提示设置bot名称（如：`ClaudeCodeBot`）
4. 获取 **Bot Token**（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 获取你的 Telegram Chat ID

1. 在Telegram中搜索 **@userinfobot**
2. 发送任意消息
3. 获取你的 **Chat ID**（纯数字，如：`123456789`）

### 3. 配置技能

创建配置文件：`~/.claude/skills/telegram-control/config.json`

```json
{
  "bot_token": "你的Bot_Token",
  "chat_id": "你的Chat_ID",
  "allowed_users": ["你的Chat_ID"],
  "default_receiver": "your@qq.com",
  "welcome_message": "Claude Code Bot已启动！可以开始对话了。"
}
```

配置LLM：`~/.claude/skills/telegram-control/llm_config.json`

```json
{
  "llm_provider": "openai",
  "openai_api_key": "你的OpenAI_API_Key",
  "openai_model": "gpt-4o",
  "max_tokens": 1000,
  "temperature": 0.1
}
```

### 4. 安装依赖

```bash
pip install python-telegram-bot openai
```

## 使用方法

### 启动 Bot

```bash
cd ~/.claude/skills/telegram-control
python bot_core.py
```

Bot启动后，会一直运行，等待你的消息。

### 在Telegram中控制

**基础命令**：
```
# 查看帮助
/help

# 查看系统状态
/status

# 执行命令
/run ls -la

# 传输文件
发送文件到Bot，自动保存到电脑

# 获取文件
/get 文件路径
```

**AI自然对话**（推荐）：
```
你: 查看系统状态
Bot: 🖥️ 系统状态
   CPU: 23%
   内存: 6.2GB / 16GB

你: 桌面有什么文件
Bot: 📁 Desktop文件：
   - 报告.pdf (2.3MB)
   - 数据.xlsx (1.1MB)
   - 录音.mp3 (5.6MB)

你: 把报告发给我
Bot: 好的！正在发送报告.pdf...
[发送文件]

你: 把它发我邮箱
Bot: 正在发送邮件到 manke_zhy@qq.com...
✅ 邮件发送成功！

你: 再来一次
Bot: 好的，再次发送邮件
✅ 邮件发送成功！

你: 在桌面新建test.txt
Bot: ✅ 文件创建成功！
   文件名: test.txt
   位置: Desktop
```

## 支持的命令

### 系统命令
- `/help` - 显示帮助信息
- `/status` - 查看系统状态（CPU、内存、磁盘）
- `/pwd` - 显示当前工作目录
- `/ls [路径]` - 列出目录文件
- `/cd <路径>` - 切换工作目录

### 文件操作
- `/get <文件路径>` - 发送文件给你
- `/save` - 保存你发送的文件到当前目录
- `/save <路径>` - 保存你发送的文件到指定路径

### 命令执行
- `/run <命令>` - 执行系统命令
- `/python <代码>` - 执行Python代码
- `/bash <脚本>` - 执行Bash脚本

### Claude Code集成
- `/ask <问题>` - 询问Claude Code
- `/task <描述>` - 创建任务
- `/file <文件>` - 处理文件

## 技术实现

**架构设计**：
```
Telegram消息 → MessageRouter → 意图理解层(GPT-4o) → ActionExecutor → 执行结果
                  ↓
              命令模式(/status) → 直接执行（无需AI）
```

**核心模块**：
- `bot_core.py` - Bot核心和消息路由(200行)
- `intent_layer.py` - GPT-4o意图理解(150行)
- `executor.py` - 统一执行器(200行)
- `context.py` - 对话上下文管理(80行)
- `utils.py` - 工具函数(100行)

**使用库**：
- `python-telegram-bot` - Telegram Bot API
- `openai` - GPT-4o API
- `subprocess` - 执行系统命令
- `asyncio` - 异步处理

**工作流程**：
```
1. 用户发送消息
2. MessageRouter路由(命令模式 vs NLP模式)
3. 命令模式：直接执行
4. NLP模式：GPT-4o理解 → 规则降级(如需要) → 执行
5. 更新上下文 → 返回结果
```

**智能特性**：
- **上下文记忆**：记住上一次的文件和操作
- **文件搜索**：在Desktop/Downloads智能搜索
- **收件人推断**：自动判断发送到Telegram还是邮箱
- **安全验证**：阻止危险命令

## 安全特性

✅ **用户白名单**：只允许配置的用户使用
✅ **命令沙箱**：危险命令需要确认
✅ **文件限制**：文件大小限制100MB
✅ **日志记录**：所有操作都有日志

## 高级功能

### 1. 混合架构

**命令模式**（快速响应<0.5秒）：
- `/status` - 系统状态
- `/ls` - 列出文件
- `/get <file>` - 获取文件
- `/run <cmd>` - 执行命令

**AI模式**（智能理解<2秒）：
- 自然语言描述任务
- 自动理解意图
- 上下文记忆

### 2. 后台运行

```bash
# Linux/Mac
nohup python bot_core.py &

# Windows
start /B python bot_core.py
```

### 2. 自动启动

**使用 systemd（Linux）**：
```ini
[Unit]
Description=Telegram Control Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/home/user/.claude/skills/telegram-control
ExecStart=/usr/bin/python3 telegram_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. 自定义命令

编辑 `commands.py` 添加自定义命令：

```python
def custom_command_handler(update, context):
    # 你的自定义逻辑
    update.message.reply_text("执行自定义命令")
```

## 使用示例

### 示例1：远程办公

**在Telegram中**：
```
你: /status
Bot: 🖥️ 系统状态
   CPU: 23%
   内存: 6.2GB / 16GB
   磁盘: 45% / 500GB

你: /run ls ~/Desktop
Bot: Desktop文件：
   - 报告.pdf
   - 数据.xlsx
   - 截图.png

你: /get ~/Desktop/报告.pdf
Bot: [发送报告.pdf]
```

### 示例2：文件传输

**从手机到电脑**：
```
你在Telegram: [发送照片.jpg]
Bot: ✅ 文件已保存到 /home/user/下载/照片.jpg
```

**从电脑到手机**：
```
你: /get ~/Documents/重要文档.pdf
Bot: [发送重要文档.pdf]
```

### 示例3：监控任务

```
你: /run python long_task.py
Bot: 任务已启动（PID: 12345）

你（30分钟后）: /status
Bot: 🖥️ 系统状态
   CPU: 78%
   任务运行中: python long_task.py

你: 任务完成了吗？
Bot: 任务仍在运行，已执行 30分钟
```

## 故障排除

### 问题1：Bot无响应

**原因**：
- Bot未启动
- Token配置错误
- 网络连接问题

**解决方法**：
1. 检查Bot是否运行：`ps aux | grep telegram_bot`
2. 检查Token是否正确
3. 查看日志：`tail -f telegram_bot.log`

### 问题2：命令执行失败

**原因**：
- 权限不足
- 命令不存在
- 路径错误

**解决方法**：
1. 检查当前目录：`/pwd`
2. 使用绝对路径
3. 检查文件权限

### 问题3：文件传输失败

**原因**：
- 文件过大（>100MB）
- 文件不存在
- 网络超时

**解决方法**：
1. 压缩文件后再传输
2. 检查文件路径
3. 分批传输大文件

## 与其他技能对比

| 技能 | 方向 | 文件传输 | 实时性 | AI理解 | 体验 |
|------|------|---------|--------|--------|------|
| file-share | 单向（→邮箱） | ✅ | 慢 | ❌ | ⭐⭐⭐ |
| wechat-push | 单向（→微信） | ⚠️ | 慢 | ❌ | ⭐⭐⭐ |
| **telegram-control v1** | **双向（↔）** | **✅** | **快** | **❌** | **⭐⭐⭐⭐** |
| **telegram-control v2** | **双向（↔）** | **✅** | **快** | **✅** | **⭐⭐⭐⭐⭐** |

## 最佳实践

1. **设置启动脚本**：开机自动启动Bot
2. **配置白名单**：只允许自己使用
3. **定期检查日志**：监控使用情况
4. **文件分类存储**：自动分类下载的文件
5. **命令别名**：为常用命令创建快捷方式

## 安全建议

⚠️ **重要提示**：

1. **保护API密钥**
   - 不要分享OpenAI API Key
   - 定期检查API使用量
   - 使用环境变量存储

2. **保护Bot Token**
   - 不要分享给他人
   - 定期更换Token
   - 使用环境变量存储

3. **限制访问权限**
   - 配置allowed_users白名单
   - 不要使用root运行
   - 限制危险命令（rm、format等）

4. **文件安全**
   - 检查下载文件类型
   - 扫描病毒
   - 不要执行未知文件

5. **成本控制**
   - GPT-4o有API费用（预估~$4/月）
   - 智能缓存避免重复调用
   - 命令模式不消耗API额度

6. **网络安全**
   - 使用HTTPS（如果使用webhook）
   - 定期更新依赖库
   - 监控异常活动

## 技术支持

- Telegram Bot文档：https://core.telegram.org/bots/api
- python-telegram-bot文档：https://python-telegram-bot.readthedocs.io/
- 问题反馈：在Claude Code中询问

---

**更新日期**：2026-01-28
**版本**：v2.0 (重构版)
**作者**：Claude Code

## 更新日志

### v2.0 (2026-01-28)
- ✨ 使用GPT-4o进行自然语言理解
- 🏗️ 架构重构：代码量减少72%
- 🧠 智能上下文记忆
- 🛡️ 优雅降级机制
- 📁 模块化设计

### v1.0 (2026-01-27)
- 🎉 初始版本
- ✅ 基础命令支持
- ✅ 文件传输功能
- ✅ 规则匹配NLP
