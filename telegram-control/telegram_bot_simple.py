#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Bot - 简化测试版
基本功能：接收消息、执行命令、发送文件
"""

import os
import sys
import json
import subprocess
import logging

# 检查依赖
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("[ERROR] Missing dependency. Run: pip install python-telegram-bot")
    sys.exit(1)


CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'bot.log')

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SimpleBot:
    def __init__(self):
        self.config = self.load_config()
        self.working_dir = os.path.expanduser('~')

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            logger.error(f"Config not found: {CONFIG_FILE}")
            sys.exit(1)

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def check_permission(self, user_id):
        allowed = self.config.get('allowed_users', [])
        if not allowed:
            return True
        return str(user_id) in allowed or int(user_id) in [int(x) for x in allowed]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.check_permission(update.effective_user.id):
            await update.message.reply_text("No permission")
            return

        await update.message.reply_text(
            "Claude Code Bot Started!\n\n"
            "Commands:\n"
            "/status - System status\n"
            "/ls - List files\n"
            "/get <file> - Get file\n"
            "/run <cmd> - Run command\n\n"
            "Or just type naturally!"
        )

    async def help_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Available Commands:\n"
            "/status - Check system status\n"
            "/ls - List current directory\n"
            "/get <path> - Send file to you\n"
            "/run <command> - Execute command"
        )

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            msg = f"System Status:\nCPU: {cpu}%\nMemory: {memory.percent}%"
            await update.message.reply_text(msg)
        except ImportError:
            await update.message.reply_text("Install psutil: pip install psutil")

    async def ls(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            path = ' '.join(context.args) if context.args else self.working_dir
            files = os.listdir(path)[:20]

            if not files:
                await update.message.reply_text(f"{path} is empty")
                return

            msg = f"Files in {path}:\n" + "\n".join(files[:20])
            if len(files) > 20:
                msg += f"\n... and {len(files) - 20} more"

            await update.message.reply_text(msg)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def run_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /run <command>")
            return

        command = ' '.join(context.args)

        # Dangerous commands check
        if 'rm -rf' in command or 'format' in command:
            await update.message.reply_text("Dangerous command blocked!")
            return

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout or result.stderr
            if len(output) > 3000:
                output = output[:3000] + "\n... (truncated)"

            await update.message.reply_text(f"Result:\n{output}")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def get_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /get <file_path>")
            return

        file_path = ' '.join(context.args)

        if not os.path.isabs(file_path):
            file_path = os.path.join(self.working_dir, file_path)

        if not os.path.exists(file_path):
            await update.message.reply_text(f"File not found: {file_path}")
            return

        try:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if size_mb > 100:
                await update.message.reply_text(f"File too large: {size_mb:.1f}MB")
                return

            await update.message.reply_text(f"Sending: {os.path.basename(file_path)}")
            with open(file_path, 'rb') as f:
                await update.message.reply_document(f)

            logger.info(f"File sent: {file_path}")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        logger.info(f"Message: {text}")

        # Simple keyword matching
        text_lower = text.lower()

        if 'status' in text_lower or '状态' in text:
            await update.message.reply_text("Checking status...")
            await self.status(update, context)
        elif 'file' in text_lower or '文件' in text:
            await update.message.reply_text("Use /get <file_path> to get a file")
        elif 'help' in text_lower or '帮助' in text:
            await self.help_cmd(update, context)
        else:
            await update.message.reply_text(
                f"Received: {text}\n\n"
                f"Try:\n"
                f"- status\n"
                f"- ls\n"
                f"- help"
            )

    def run(self):
        bot_token = self.config['bot_token']
        application = Application.builder().token(bot_token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_cmd))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(CommandHandler("ls", self.ls))
        application.add_handler(CommandHandler("run", self.run_cmd))
        application.add_handler(CommandHandler("get", self.get_file))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logger.info("Bot started (Simple Mode)")
        application.run_polling()


def main():
    print("=" * 50)
    print("  Claude Code Telegram Bot")
    print("  Simple Test Version")
    print("=" * 50)

    bot = SimpleBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == '__main__':
    main()
