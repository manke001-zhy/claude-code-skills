#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文管理 - 对话上下文和记忆
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


class ConversationContext:
    """对话上下文管理器"""

    def __init__(self, max_history: int = 10):
        """初始化上下文管理器

        Args:
            max_history: 最大对话历史记录数
        """
        self.data = {
            'last_file': None,
            'last_action': None,
            'last_plan': None,
            'working_dir': os.path.expanduser('~'),
            'conversation_history': deque(maxlen=max_history)
        }

        logger.info("ConversationContext initialized")

    def update_from_plan(self, plan: Dict[str, Any]):
        """从执行计划更新上下文

        Args:
            plan: 执行计划字典
        """
        action = plan.get('action', '')
        params = plan.get('params', {})

        # 保存上一次的操作
        self.data['last_action'] = action
        self.data['last_plan'] = plan

        # 保存文件信息
        if action == 'send_file':
            file_path = params.get('file_path')
            if file_path:
                self.data['last_file'] = file_path
                logger.info(f"Context updated: last_file = {file_path}")

        elif action == 'send_email':
            file_path = params.get('file_path')
            if file_path:
                self.data['last_file'] = file_path
                logger.info(f"Context updated: last_file = {file_path}")

        elif action == 'list_files':
            path = params.get('path', '')
            if path and os.path.isdir(path):
                self.data['working_dir'] = path
                logger.info(f"Context updated: working_dir = {path}")

    def add_to_history(self, user_message: str, bot_response: str):
        """添加对话到历史记录

        Args:
            user_message: 用户消息
            bot_response: Bot响应
        """
        self.data['conversation_history'].append({
            'user': user_message,
            'bot': bot_response,
            'timestamp': datetime.now().isoformat()
        })

    def get_data(self) -> Dict[str, Any]:
        """获取上下文数据(用于传递给意图理解器)

        Returns:
            上下文字典
        """
        return {
            'last_file': self.data['last_file'],
            'last_action': self.data['last_action'],
            'working_dir': self.data['working_dir'],
            'conversation_history': list(self.data['conversation_history'])
        }

    def get_for_prompt(self) -> str:
        """生成用于prompt的上下文字符串

        Returns:
            格式化的上下文字符串
        """
        lines = [
            "## 当前上下文",
            f"- 工作目录: {self.data['working_dir']}",
            f"- 上一次文件: {self.data['last_file'] or '无'}",
            f"- 上一次操作: {self.data['last_action'] or '无'}"
        ]

        # 添加最近对话
        history = list(self.data['conversation_history'])
        if history:
            lines.append("\n## 最近对话")
            for item in history[-5:]:  # 只显示最近5条
                user_msg = item['user'][:50] + '...' if len(item['user']) > 50 else item['user']
                lines.append(f"- 用户: {user_msg}")

        return "\n".join(lines)

    def get_last_file(self) -> Optional[str]:
        """获取上一次的文件路径

        Returns:
            文件路径或None
        """
        return self.data['last_file']

    def get_last_plan(self) -> Optional[Dict[str, Any]]:
        """获取上一次的执行计划

        Returns:
            执行计划字典或None
        """
        return self.data['last_plan']

    def set_working_dir(self, path: str):
        """设置工作目录

        Args:
            path: 目录路径
        """
        if os.path.isdir(path):
            self.data['working_dir'] = os.path.abspath(path)
            logger.info(f"Working dir set to: {self.data['working_dir']}")

    def clear_history(self):
        """清空对话历史"""
        self.data['conversation_history'].clear()
        logger.info("Conversation history cleared")

    def reset(self):
        """重置上下文"""
        self.data['last_file'] = None
        self.data['last_action'] = None
        self.data['last_plan'] = None
        self.data['working_dir'] = os.path.expanduser('~')
        self.data['conversation_history'].clear()
        logger.info("Context reset")

    def __repr__(self) -> str:
        """字符串表示"""
        return (f"ConversationContext("
                f"last_file={self.data['last_file']}, "
                f"last_action={self.data['last_action']}, "
                f"working_dir={self.data['working_dir']}, "
                f"history_len={len(self.data['conversation_history'])})")
