#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot核心 - 重构后的Telegram Bot
混合架构: 命令模式 + GPT-4o自然语言理解
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("Error: python-telegram-bot not installed. Run: pip install python-telegram-bot")
    sys.exit(1)

from intent_layer import GPTIntentUnderstander, ExecutePlan
from executor import ActionExecutor
from context import ConversationContext
from utils import search_file, is_command, parse_command

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'bot_core.log')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MessageRouter:
    """消息路由器 - 决定使用命令模式还是NLP模式"""

    def __init__(self):
        """初始化路由器"""
        self.command_prefixes = ['/', 'status', 'ls', 'help', 'pwd', 'cd', 'run', 'get']

    def route(self, message: str) -> Dict[str, Any]:
        """路由消息

        Args:
            message: 用户消息

        Returns:
            路由结果 {mode: 'command'/'nlp', command: str}
        """
        message_stripped = message.strip()

        # 命令模式
        if message_stripped.startswith('/'):
            command, _ = parse_command(message_stripped)
            return {
                'mode': 'command',
                'command': command,
                'original': message
            }

        # 包含命令关键词
        message_lower = message_stripped.lower()
        for prefix in self.command_prefixes:
            if prefix == '/' or message_lower.startswith(prefix):
                return {
                    'mode': 'command',
                    'command': prefix,
                    'original': message
                }

        # NLP模式(使用GPT理解)
        return {
            'mode': 'nlp',
            'command': None,
            'original': message
        }


class TelegramBot:
    """重构后的Telegram Bot"""

    def __init__(self):
        """初始化Bot"""
        self.config = self.load_config()
        self.context = ConversationContext()
        self.router = MessageRouter()

        # 初始化意图理解层(完全依赖GPT-4o)
        self.intent_understander = self._init_intent_understander()

        # 初始化执行层
        self.executor = ActionExecutor(self.config)

        logger.info("TelegramBot initialized successfully")

    def _init_intent_understander(self) -> Optional[GPTIntentUnderstander]:
        """初始化GPT意图理解器"""
        try:
            # 加载LLM配置
            llm_config_path = os.path.join(os.path.dirname(__file__), 'llm_config.json')

            if not os.path.exists(llm_config_path):
                logger.warning("llm_config.json not found, using rule-based mode")
                return None

            with open(llm_config_path, 'r', encoding='utf-8') as f:
                llm_config = json.load(f)

            api_key = llm_config.get('openai_api_key')
            model = llm_config.get('openai_model', 'gpt-4o')

            if not api_key:
                logger.warning("No API key in llm_config.json, using rule-based mode")
                return None

            understander = GPTIntentUnderstander(api_key=api_key, model=model)
            logger.info(f"GPTIntentUnderstander initialized with model: {model}")
            return understander

        except Exception as e:
            logger.warning(f"Failed to initialize GPTIntentUnderstander: {e}")
            return None

    def load_config(self) -> Dict:
        """加载配置"""
        if not os.path.exists(CONFIG_FILE):
            logger.error(f"Config not found: {CONFIG_FILE}")
            sys.exit(1)

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def check_permission(self, user_id: int) -> bool:
        """检查用户权限"""
        allowed = self.config.get('allowed_users', [])
        if not allowed:
            # 白名单为空,只允许配置的chat_id
            configured_id = self.config.get('chat_id')
            if configured_id:
                return str(user_id) == str(configured_id) or int(user_id) == int(configured_id)
            return False
        return str(user_id) in allowed or int(user_id) in [int(x) for x in allowed]

    # ==================== 命令处理器 ====================

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/start命令"""
        if not self.check_permission(update.effective_user.id):
            await update.message.reply_text("No permission")
            return

        await update.message.reply_text(
            " Claude Code Bot 已启动!\n\n"
            "你可以用自然语言和我对话:\n"
            "• 查看状态 / status\n"
            "• 列出桌面文件\n"
            "• 把 report.pdf 发给我\n"
            "• 发送邮件给 friend@qq.com\n"
            "• 再来一次(重复上一次操作)\n\n"
            "发送 /help 查看更多命令"
        )

    async def help_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/help命令"""
        await self.executor.execute({
            'action': 'help',
            'params': {},
            'user_message': '',
            'confidence': 1.0
        }, update, context)

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/status命令"""
        await self.executor.execute({
            'action': 'status',
            'params': {},
            'user_message': '正在查看系统状态...',
            'confidence': 1.0
        }, update, context)

    async def ls(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/ls命令"""
        path = ' '.join(context.args) if context.args else self.context.data['working_dir']
        await self.executor.execute({
            'action': 'list_files',
            'params': {'path': path},
            'user_message': f'正在列出目录: {path}',
            'confidence': 1.0
        }, update, context)

    async def pwd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/pwd命令"""
        await update.message.reply_text(f" 当前目录: {self.context.data['working_dir']}")

    async def cd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/cd命令"""
        if not context.args:
            await update.message.reply_text("用法: /cd <路径>")
            return

        path = ' '.join(context.args)
        if not os.path.isabs(path):
            path = os.path.join(self.context.data['working_dir'], path)

        if os.path.isdir(path):
            self.context.set_working_dir(path)
            await update.message.reply_text(f"[OK] 切换到: {path}")
        else:
            await update.message.reply_text(f"[X] 目录不存在: {path}")

    async def run(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/run命令"""
        if not context.args:
            await update.message.reply_text("用法: /run <命令>")
            return

        command = ' '.join(context.args)
        await self.executor.execute({
            'action': 'run_command',
            'params': {'command': command},
            'user_message': f'执行命令: {command}',
            'confidence': 1.0
        }, update, context)

    async def get(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """/get命令"""
        if not context.args:
            await update.message.reply_text("用法: /get <文件路径>")
            return

        file_path = ' '.join(context.args)
        await self.executor.execute({
            'action': 'send_file',
            'params': {'file_path': file_path},
            'user_message': f'发送文件: {file_path}',
            'confidence': 1.0
        }, update, context)

    # ==================== 自然语言消息处理器 ====================

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理消息 - 核心逻辑"""
        text = update.message.text
        user_id = update.effective_user.id

        if not self.check_permission(user_id):
            await update.message.reply_text("No permission")
            return

        logger.info(f"Message received: {text}")

        # 路由决策
        route = self.router.route(text)

        if route['mode'] == 'command':
            # 命令模式 - 直接执行
            await self._handle_command(route['command'], update, context)
        else:
            # NLP模式 - 使用GPT理解
            await self._handle_nlp(text, update, context)

        # 保存到对话历史
        # (在执行后保存,这里简化处理)

    async def _handle_command(self, command: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理命令模式"""
        command_map = {
            '/start': self.start,
            '/help': self.help_cmd,
            '/status': self.status,
            '/ls': self.ls,
            '/pwd': self.pwd,
            '/cd': self.cd,
            '/run': self.run,
            '/get': self.get,
        }

        handler = command_map.get(command)
        if handler:
            await handler(update, context)
        else:
            await update.message.reply_text(f"❓ 未知命令: {command}\n发送 /help 查看帮助")

    async def _handle_nlp(self, message: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理NLP模式 - 完全依赖GPT-4o理解"""
        try:
            # 检查是否启用了GPT
            if not self.intent_understander:
                await update.message.reply_text(
                    "[!] AI未启用\n\n"
                    "请在 llm_config.json 中配置 OpenAI API Key\n"
                    "或者使用命令模式: /help"
                )
                return

            # 使用GPT-4o理解意图
            plan = self.intent_understander.understand(
                message,
                self.context.get_data()
            )

            # 转换为字典
            plan_dict = plan.to_dict()

            # 处理repeat操作
            if plan_dict['action'] == 'repeat':
                last_plan = self.context.get_last_plan()
                if last_plan:
                    plan_dict = last_plan
                    plan_dict['user_message'] = "好的,再次执行上一次操作"
                else:
                    await update.message.reply_text("[X] 没有上一次的操作记录")
                    return

            # 发送用户消息
            if plan_dict['user_message']:
                await update.message.reply_text(plan_dict['user_message'])

            # 检查是否需要澄清
            if plan_dict.get('needs_clarification'):
                # 已经在user_message中包含了问题
                return

            # 检查置信度
            if plan.confidence < 0.3:
                await update.message.reply_text(
                    "🤔 我没太理解你的意思\n\n"
                    "能否换个方式说？比如：\n"
                    "• \"查看系统状态\"\n"
                    "• \"列出桌面文件\"\n"
                    "• \"把 report.pdf 发给我\""
                )
                return

            # 执行计划
            await self.executor.execute(plan_dict, update, context)

            # 更新上下文
            self.context.update_from_plan(plan_dict)
            self.context.add_to_history(message, plan_dict['user_message'])

        except Exception as e:
            logger.error(f"Handle NLP failed: {e}")
            await update.message.reply_text(
                f"[X] 处理失败: {e}\n\n"
                f"请稍后重试或使用命令模式: /help"
            )

    # ==================== 文件处理器 ====================

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理接收的文件"""
        if not update.message.document:
            await update.message.reply_text("请发送一个文件")
            return

        document = update.message.document
        filename = document.file_name

        try:
            file = await document.get_file()
            save_path = os.path.join(self.context.data['working_dir'], filename)

            await file.download_to_drive(save_path)

            size_mb = os.path.getsize(save_path) / (1024 * 1024)

            await update.message.reply_text(
                f"[OK] 文件已保存\n\n"
                f" 文件名: {filename}\n"
                f" 路径: {save_path}\n"
                f" 大小: {size_mb:.1f}MB"
            )

            # 更新上下文
            self.context.data['last_file'] = save_path
            logger.info(f"File saved: {save_path}")

        except Exception as e:
            logger.error(f"Save file failed: {e}")
            await update.message.reply_text(f"[X] 保存文件失败: {e}")

    # ==================== 运行Bot ====================

    def run(self):
        """运行Bot"""
        bot_token = self.config['bot_token']
        application = Application.builder().token(bot_token).build()

        # 命令处理器
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_cmd))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(CommandHandler("pwd", self.pwd))
        application.add_handler(CommandHandler("ls", self.ls))
        application.add_handler(CommandHandler("cd", self.cd))
        application.add_handler(CommandHandler("run", self.run))
        application.add_handler(CommandHandler("get", self.get))

        # 消息处理器
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(MessageHandler(filters.Document, self.handle_document))

        logger.info("=" * 60)
        logger.info("  Claude Code Telegram Bot - 重构版")
        logger.info("  混合架构: 命令模式 + GPT-4o NLP")
        logger.info("=" * 60)
        logger.info(f"Intent Understander: {'GPT-4o' if self.intent_understander else 'Rule-based'}")
        logger.info("Bot started, polling...")

        application.run_polling()


def main():
    """主函数"""
    print("=" * 60)
    print("  Claude Code Telegram Bot - 重构版")
    print("  混合架构: 命令模式 + GPT-4o NLP")
    print("=" * 60)
    print("\nBot starting...\n")

    bot = TelegramBot()

    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped")
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == '__main__':
    main()
