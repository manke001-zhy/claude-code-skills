#!/bin/bash
echo "========================================"
echo "  启动 Claude Code Bot 系统"
echo "========================================"
echo ""

cd "$HOME/.claude/skills/telegram-control"

echo "[1/2] 启动 AI监听器..."
python claude_smart_listener.py &
LISTENER_PID=$!
sleep 2

echo "[2/2] 启动 Telegram Bot..."
python bot_forward.py &
BOT_PID=$!
sleep 2

echo ""
echo "========================================"
echo "  系统已启动！"
echo "========================================"
echo ""
echo "监听器 PID: $LISTENER_PID"
echo "Bot PID: $BOT_PID"
echo ""
echo "功能："
echo "- 创建文件: test.txt写入hello"
echo "- 读取文件: 读取test.txt"
echo "- 接收文件: 直接发送图片/文件"
echo "- 列出文件: 桌面有什么"
echo ""
echo "要停止系统，运行: stop.sh"
echo ""
