# 真正的AI助手架构

## 🎯 架构设计

```
你的消息(中文) → Telegram Bot → 文件传递 → Claude Code监听器 → Claude Code执行 → 返回结果
                  (只转发)        (不处理)        (理解并执行)
```

## 📋 工作流程

### 1. 发送消息
```
你: "在桌面新建一个test.txt"
```

### 2. Telegram Bot (bot_forward.py)
```python
# 不做任何理解，直接转发
request_data = {
    'message': "在桌面新建一个test.txt",
    'user_id': ...,
    'chat_id': ...
}
# 保存到请求文件
```

### 3. 文件传递
```python
# 请求文件
/tmp/claude_requests/req_123.txt

# Claude Code监听器监控这个目录
```

### 4. Claude Code监听器 (claude_listener.py)
```python
# 发现新请求文件
# 读取消息
# 调用Claude Code处理
# 保存响应到 /tmp/claude_responses/req_123.txt
```

### 5. Telegram Bot获取响应
```python
# 轮询响应文件
# 发送回Telegram
```

## ✅ 关键特点

1. **Telegram Bot不思考**
   - 只负责转发消息
   - 不做任何意图理解
   - 不调用任何LLM

2. **Claude Code是大脑**
   - 理解你的需求
   - 决定如何执行
   - 可以返回问题继续沟通

3. **通过文件通信**
   - 请求文件: `/tmp/claude_requests/req_*.txt`
   - 响应文件: `/tmp/claude_responses/req_*.txt`

## 🧪 测试

在Telegram中发送：
```
在桌面新建一个test.txt
```

流程：
1. Bot创建请求文件
2. 监听器发现文件
3. Claude Code创建文件
4. Bot发送结果给你

## 🚀 启动命令

**启动监听器**：
```bash
cd ~/.claude/skills/telegram-control
python claude_listener.py
```

**启动Bot**：
```bash
cd ~/.claude/skills/telegram-control
python bot_forward.py
```

## 💡 优势

- ✅ 真正的理解，不是翻译
- ✅ Claude Code可以追问澄清
- ✅ 上下文记忆在Claude Code端
- ✅ Bot只是一个信使
- ✅ 可以不断优化Claude Code，Bot不需要改

这才是真正的"让AI干活"！
