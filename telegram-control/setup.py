#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot 快速配置脚本
"""

import os
import sys
import json


CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')


def main():
    """配置向导"""
    print("=" * 60)
    print("  Claude Code Telegram Bot - 配置向导")
    print("=" * 60)
    print("\n请按以下步骤配置Bot：\n")

    print("步骤 1/3: 创建 Telegram Bot")
    print("-" * 60)
    print("1. 在Telegram中搜索 @BotFather")
    print("2. 发送命令: /newbot")
    print("3. 按提示设置bot名称和用户名")
    print("4. 复制Bot Token（格式：123456789:ABCdefGHI...）\n")

    bot_token = input("请输入Bot Token: ").strip()

    if not bot_token or ':' not in bot_token:
        print("[ERROR] Bot Token格式不正确")
        sys.exit(1)

    print("\n步骤 2/3: 获取你的 Chat ID")
    print("-" * 60)
    print("1. 在Telegram中搜索 @userinfobot")
    print("2. 发送任意消息")
    print("3. 复制你的Chat ID（纯数字）\n")

    chat_id = input("请输入Chat ID: ").strip()

    if not chat_id or not chat_id.isdigit():
        print("[ERROR] Chat ID格式不正确")
        sys.exit(1)

    print("\n步骤 3/3: 完成配置")
    print("-" * 60)

    # 创建配置
    config = {
        "bot_token": bot_token,
        "chat_id": chat_id,
        "allowed_users": [chat_id],  # 只允许自己使用
        "welcome_message": "Claude Code Bot已启动！可以开始对话了。"
    }

    # 保存配置
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"[OK] 配置已保存到: {CONFIG_FILE}")

        print("\n下一步：")
        print("1. 安装依赖: pip install python-telegram-bot")
        print("2. 启动Bot: python telegram_bot.py")
        print("3. 在Telegram中给你的bot发送 /start")

        print("\n" + "=" * 60)
        print("  配置完成！")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] 保存配置失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
