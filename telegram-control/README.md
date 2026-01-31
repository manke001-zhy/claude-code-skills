# Telegram Bot - 快速开始

## 1. 安装依赖

```bash
pip install python-telegram-bot
```

## 2. 配置Bot

**方式1：使用配置向导（推荐）**
```bash
python setup.py
```

按提示输入Bot Token和Chat ID。

**方式2：手动配置**
1. 在Telegram中搜索 `@BotFather`，发送 `/newbot` 创建Bot，获取Token
2. 在Telegram中搜索 `@userinfobot`，获取你的Chat ID
3. 编辑 `config.json`，填写Bot Token和Chat ID

## 3. 启动Bot

```bash
python telegram_bot.py
```

## 4. 开始使用

在Telegram中给你的Bot发送 `/start` 即可开始对话。

## 常用命令

- `/help` - 查看帮助
- `/status` - 查看系统状态
- `/ls` - 列出当前目录文件
- `/get <文件路径>` - 获取文件
- `/run <命令>` - 执行命令

## 示例

```
你: /status
Bot: 🖥️ 系统状态
   CPU: 23%
   内存: 6.2GB / 16GB

你: /ls Desktop
Bot: Desktop文件：
   - 报告.pdf (2.3MB)
   - 数据.xlsx (1.1MB)

你: /get Desktop/报告.pdf
Bot: [发送报告.pdf]

你: /run python script.py
Bot: ⏳ 正在执行: python script.py...
Bot: ✅ 执行成功
```

## 故障排除

**问题：Bot无响应**
- 检查Bot是否运行
- 检查Token是否正确
- 查看日志：telegram_bot.log

**问题：权限不足**
- 检查config.json中的allowed_users
- 确保你的Chat ID在白名单中

## 技术支持

查看完整文档：SKILL.md
