#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正的AI驱动Bot - 使用Function Calling
"""

import os
import sys
import json
import logging
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("Error: python-telegram-bot not installed")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai not installed")
    sys.exit(1)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
LLM_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'llm_config.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'bot_v2.log')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TrueAIBot:
    """真正的AI驱动Bot - 使用Function Calling"""

    def __init__(self):
        self.config = self.load_config()
        self.client = self.init_openai()
        self.context = {
            'last_file': None,
            'working_dir': os.path.expanduser('~')
        }

        # 定义可用的工具函数
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "在桌面或其他目录创建新文件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "文件名，例如: test.txt"
                            },
                            "content": {
                                "type": "string",
                                "description": "文件内容(可选)"
                            }
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "列出目录中的文件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "目录路径，例如: ~/Desktop"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_file",
                    "description": "发送文件到Telegram",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "文件路径"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_email",
                    "description": "发送文件到邮箱",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "文件路径"
                            },
                            "receiver": {
                                "type": "string",
                                "description": "收件人邮箱(可选)"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_status",
                    "description": "查看系统状态",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "执行系统命令",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "要执行的命令"
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]

        logger.info("TrueAIBot initialized with Function Calling")

    def load_config(self):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def init_openai(self):
        with open(LLM_CONFIG_FILE, 'r', encoding='utf-8') as f:
            llm_config = json.load(f)
        return OpenAI(api_key=llm_config['openai_api_key'])

    def check_permission(self, user_id):
        allowed = self.config.get('allowed_users', [])
        if not allowed:
            configured_id = self.config.get('chat_id')
            return str(user_id) == str(configured_id)
        return str(user_id) in allowed

    # ==================== 工具函数实现 ====================

    def create_file(self, filename: str, content: str = "") -> str:
        """创建文件"""
        try:
            import re
            # 清理文件名
            filename = re.sub(r'\.\s+(\w+)', r'.\1', filename)

            desktop = Path.home() / 'Desktop'
            file_path = desktop / filename

            if file_path.exists():
                return f"[!] 文件已存在: {filename}"

            file_path.touch()
            if content:
                file_path.write_text(content, encoding='utf-8')

            self.context['last_file'] = str(file_path)
            return f"[OK] 已创建文件: {filename}\n路径: {file_path}"

        except Exception as e:
            return f"[X] 创建文件失败: {e}"

    def list_files(self, directory: str = None) -> str:
        """列出文件"""
        try:
            if directory:
                if directory.startswith('~'):
                    directory = os.path.expanduser(directory)
            else:
                directory = os.path.expanduser('~/Desktop')

            if not os.path.exists(directory):
                return f"[X] 目录不存在: {directory}"

            files = os.listdir(directory)
            if not files:
                return f"目录为空: {os.path.basename(directory)}"

            result = [f"📁 {os.path.basename(directory)}:"]
            for f in files[:20]:
                path = os.path.join(directory, f)
                if os.path.isdir(path):
                    result.append(f"  📂 {f}/")
                else:
                    size = os.path.getsize(path)
                    size_str = f"{size/1024:.1f}KB" if size < 1024**2 else f"{size/(1024**2):.1f}MB"
                    result.append(f"  📄 {f} ({size_str})")

            return "\n".join(result)

        except Exception as e:
            return f"[X] 列出文件失败: {e}"

    def get_status(self) -> str:
        """获取系统状态"""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return f"""[PC] 系统状态
CPU: {cpu}%
内存: {memory.used/(1024**3):.1f}GB / {memory.total/(1024**3):.1f}GB
磁盘: {disk.used/(1024**3):.1f}GB / {disk.total/(1024**3):.1f}GB
当前目录: {self.context['working_dir']}"""

        except ImportError:
            return "[X] 需要安装 psutil"
        except Exception as e:
            return f"[X] 获取状态失败: {e}"

    def run_command(self, command: str) -> str:
        """执行命令"""
        dangerous = ['rm -rf', 'format', 'mkfs', 'dd if=', 'shutdown']
        if any(d in command for d in dangerous):
            return "[X] 危险命令已被阻止"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            if len(output) > 2000:
                output = output[:2000] + "\n...(已截断)"
            return f"结果:\n{output}"
        except subprocess.TimeoutExpired:
            return "[X] 命令超时"
        except Exception as e:
            return f"[X] 执行失败: {e}"

    # ==================== 消息处理 ====================

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理消息 - 使用Function Calling"""
        text = update.message.text

        if not self.check_permission(update.effective_user.id):
            await update.message.reply_text("No permission")
            return

        logger.info(f"Message: {text}")

        try:
            # 构建上下文信息
            context_info = f"""
当前上下文:
- 工作目录: {self.context['working_dir']}
- 上一次文件: {self.context.get('last_file', '无')}
"""

            # 调用GPT-4o (使用Function Calling)
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""你是Claude Code的智能助手，帮助用户控制电脑。

{context_info}

用户会像和人聊天一样和你说话。理解用户的意图，直接调用相应的工具函数完成任务。

注意:
- 文件路径中的波浪号~要展开
- 文件名中的空格要保留
- 文件扩展名前的空格要移除(如". Txt" -> ".txt")
- 回复要简洁友好
"""
                    },
                    {"role": "user", "content": text}
                ],
                tools=self.tools,
                tool_choice="auto"
            )

            # 处理响应
            message = response.choices[0].message

            # 如果有tool_calls，执行工具函数
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Calling function: {function_name} with args: {function_args}")

                    # 调用对应的函数
                    if hasattr(self, function_name):
                        func = getattr(self, function_name)
                        result = func(**function_args)

                        # 发送结果
                        await update.message.reply_text(result)

                        # 如果是send_file，需要特殊处理
                        if function_name == "send_file":
                            file_path = function_args.get('file_path')
                            if file_path and os.path.exists(file_path):
                                with open(file_path, 'rb') as f:
                                    await update.message.reply_document(f)
                    else:
                        await update.message.reply_text(f"[X] 未知函数: {function_name}")

            # 如果是直接文本回复
            elif message.content:
                await update.message.reply_text(message.content)

        except Exception as e:
            logger.error(f"Handle message failed: {e}")
            await update.message.reply_text(f"[X] 处理失败: {e}")

    # ==================== 命令处理 ====================

    async def start(self, update, context):
        await update.message.reply_text(
            " Claude Code Bot已启动!\n\n"
            "现在可以直接用自然语言和我对话:\n"
            "• 在桌面新建test.txt\n"
            "• 看看桌面有什么\n"
            "• 把报告.pdf发给我\n"
            "• 查看系统状态\n\n"
            "完全像和人聊天一样，不需要记命令格式!"
        )

    async def help_cmd(self, update, context):
        await update.message.reply_text(
            " 真正的AI助手\n\n"
            "直接说人话即可:\n"
            "• 新建一个文件\n"
            "• 列出桌面文件\n"
            "• 查看状态\n"
            "• 发送文件给我\n\n"
            "不需要记任何命令格式!"
        )

    def run(self):
        bot_token = self.config['bot_token']
        application = Application.builder().token(bot_token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_cmd))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        logger.info("Bot started with Function Calling")
        application.run_polling()


def main():
    print("=" * 60)
    print("  Claude Code Bot - 真正的AI驱动")
    print("  使用OpenAI Function Calling")
    print("=" * 60)

    bot = TrueAIBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped")

if __name__ == '__main__':
    main()
