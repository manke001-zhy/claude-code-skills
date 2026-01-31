#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意图理解层 - 使用GPT-4o理解自然语言意图
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("Warning: openai package not installed. Run: pip install openai")

logger = logging.getLogger(__name__)


@dataclass
class ExecutePlan:
    """执行计划"""
    action: str  # 动作类型: send_file, send_email, list_files, run_command, call_skill, create_file, status, repeat
    params: Dict[str, Any]  # 参数
    user_message: str  # 给用户的响应消息
    confidence: float  # 置信度 0-1
    needs_clarification: bool = False  # 是否需要澄清

    def to_dict(self) -> Dict:
        return {
            'action': self.action,
            'params': self.params,
            'user_message': self.user_message,
            'confidence': self.confidence,
            'needs_clarification': self.needs_clarification
        }


class GPTIntentUnderstander:
    """使用GPT-4o理解自然语言意图"""

    SYSTEM_PROMPT = """你是Claude Code的智能助手,通过Telegram帮助用户控制电脑。用户会像和朋友聊天一样和你对话,你需要理解他们的真实意图。

## 你的工作
用户说的话可能是模糊的、口语化的、甚至是不完整的,你需要:
1. 理解用户的**真实意图**
2. 从上下文中推断缺失信息
3. 返回清晰的执行计划

## 支持的操作
1. **send_file** - 发送文件到Telegram
   用户说: "发给我"、"给我那个文件"、"发送xx.pdf"
   params: {file_path: "文件路径"}

2. **send_email** - 发送文件到邮箱
   用户说: "发邮箱"、"发邮件"、"上传到邮箱"、"发给xx@qq.com"
   params: {file_path: "...", receiver: "邮箱地址"}

3. **list_files** - 列出目录文件
   用户说: "看看有什么"、"查看文件"、"显示一下"、"ls"
   params: {path: "目录路径"}

4. **run_command** - 执行系统命令
   用户说: "运行xx"、"执行xx命令"
   params: {command: "命令"}

5. **create_file** - 创建新文件
   用户说: "新建xx文件"、"创建一个xx"、"建立一个txt"
   params: {filename: "文件名", location: "位置"}
   注意: 文件名要保持标准格式(如"test.txt",不是"test. txt")

6. **status** - 查看系统状态
   用户说: "状态怎么样"、"怎么样了"、"如何"、"state"
   params: {}

7. **repeat** - 重复上一次操作
   用户说: "再来一次"、"重复"、"再"、"再执行一次"
   params: {}

## 智能推断规则

**文件推断**:
- 优先使用上下文中的"上一次文件"
- "那个文件"、"它"、"这个" → 指代上一次的文件
- "桌面的xx"、"下载的xx" → 在对应目录搜索
- 只提到文件名(如"报告.pdf") → 在Desktop/Downloads搜索

**收件人推断**:
- "发给我"、"给我"、"发送"、"发" → send_file(发送到Telegram)
- "发邮箱"、"发邮件"、"邮件"、"email" → send_email
- 如果提到具体邮箱地址 → send_email

**目录推断**:
- "桌面"、"desktop" → ~/Desktop
- "下载"、"downloads" → ~/Downloads
- "文档"、"documents" → ~/Documents
- "这里"、"当前"、"这个目录" → working_dir

**操作推断**:
- "看看"、"查看"、"显示"、"列出"、"有什么" → list_files
- "状态"、"怎么样"、"如何" → status
- "新建"、"创建"、"建立"、"make"、"new" → create_file

## 返回格式(纯JSON,不要用markdown包裹)
{
    "action": "操作类型",
    "params": {参数},
    "user_message": "给用户的友好回复",
    "confidence": 0.0-1.0,
    "needs_clarification": false
}

## 重要提示
- 置信度<0.3时,在user_message中礼貌地请用户澄清
- 理解不了时,设置needs_clarification:true
- 始终返回有效的JSON
- user_message要自然、友好,像真人对话
"""

    EXAMPLES = """
## 示例对话 - 学习如何理解用户

### 场景1: 发送文件
用户: 把那个科幻小说发我
助手: {
    "action": "send_file",
    "params": {"file_path": "~/Desktop/科幻小说.pdf"},
    "user_message": "好的,正在发送科幻小说.pdf给你...",
    "confidence": 0.85,
    "needs_clarification": false
}

### 场景2: 上下文指代
用户: 把它发我邮箱 (上一次文件=~/Desktop/科幻小说.pdf)
助手: {
    "action": "send_email",
    "params": {"file_path": "~/Desktop/科幻小说.pdf", "receiver": "manke_zhy@qq.com"},
    "user_message": "好的,正在把科幻小说.pdf发送到邮箱...",
    "confidence": 0.90,
    "needs_clarification": false
}

### 场景3: 重复操作
用户: 再来一次
助手: {
    "action": "repeat",
    "params": {},
    "user_message": "好的,再发一次",
    "confidence": 0.95,
    "needs_clarification": false
}

### 场景4: 口语化表达
用户: 桌面有什么
助手: {
    "action": "list_files",
    "params": {"path": "~/Desktop"},
    "user_message": "帮你看看桌面有什么...",
    "confidence": 0.95,
    "needs_clarification": false
}

### 场景5: 极简表达
用户: 看看状态
助手: {
    "action": "status",
    "params": {},
    "user_message": "正在查看系统状态...",
    "confidence": 0.95,
    "needs_clarification": false
}

### 场景6: 模糊文件名
用户: 发给我那个报告 (上一次文件=~/Desktop/季度报告.pdf)
助手: {
    "action": "send_file",
    "params": {"file_path": "~/Desktop/季度报告.pdf"},
    "user_message": "好的,正在发送季度报告.pdf...",
    "confidence": 0.88,
    "needs_clarification": false
}

### 场景7: 创建文件
用户: 新建一个test.txt
助手: {
    "action": "create_file",
    "params": {"filename": "test.txt", "location": "Desktop"},
    "user_message": "好的,在桌面创建test.txt",
    "confidence": 0.95,
    "needs_clarification": false
}

### 场景8: 不完整表达需要澄清
用户: 发给他
助手: {
    "action": "unknown",
    "params": {},
    "user_message": "请问要发送哪个文件?发到哪里?",
    "confidence": 0.2,
    "needs_clarification": true
}

### 场景9: 口语化命令
用户: 帮我看看下载文件夹
助手: {
    "action": "list_files",
    "params": {"path": "~/Downloads"},
    "user_message": "正在查看Downloads文件夹...",
    "confidence": 0.92,
    "needs_clarification": false
}

### 场景10: 指代词+操作
用户: 把这个发邮箱 (上一次文件=~/Desktop/数据.xlsx)
助手: {
    "action": "send_email",
    "params": {"file_path": "~/Desktop/数据.xlsx", "receiver": "manke_zhy@qq.com"},
    "user_message": "好的,正在把数据.xlsx发送到邮箱...",
    "confidence": 0.90,
    "needs_clarification": false
}
"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """初始化GPT意图理解器

        Args:
            api_key: OpenAI API key
            model: 模型名称(默认gpt-4o)
        """
        if not OpenAI:
            raise ImportError("openai package not installed. Run: pip install openai")

        self.api_key = api_key
        self.model = model
        self.client = None

        if api_key:
            try:
                self.client = OpenAI(api_key=api_key)
                logger.info(f"GPTIntentUnderstander initialized with model: {model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")

        # 简单的缓存机制
        self._cache = {}

    def understand(self, message: str, context: Dict[str, Any]) -> ExecutePlan:
        """理解用户消息的意图

        Args:
            message: 用户消息
            context: 上下文信息(包含last_file, last_action, working_dir等)

        Returns:
            ExecutePlan: 执行计划
        """
        # 检查缓存
        cache_key = f"{message}_{context.get('last_file', '')}"
        if cache_key in self._cache:
            cached_plan, timestamp = self._cache[cache_key]
            # 缓存1小时有效
            if (datetime.now() - timestamp).seconds < 3600:
                logger.info(f"Using cached intent for: {message}")
                return cached_plan

        if not self.client:
            # 如果没有初始化客户端,返回空计划(会触发规则降级)
            return ExecutePlan(
                action="unknown",
                params={},
                user_message="",
                confidence=0.0,
                needs_clarification=False
            )

        try:
            # 构建完整的prompt
            context_str = self._format_context(context)
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{context_str}\n\n{self.EXAMPLES}\n\n用户: {message}\n助手:"

            # 调用OpenAI API(使用JSON mode)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=1000
            )

            # 解析响应
            content = response.choices[0].message.content
            result = json.loads(content)

            # 创建ExecutePlan
            plan = ExecutePlan(
                action=result.get('action', 'unknown'),
                params=result.get('params', {}),
                user_message=result.get('user_message', ''),
                confidence=result.get('confidence', 0.5),
                needs_clarification=result.get('needs_clarification', False)
            )

            # 缓存结果
            self._cache[cache_key] = (plan, datetime.now())

            logger.info(f"GPT understood: {plan.action} (confidence: {plan.confidence})")
            return plan

        except Exception as e:
            logger.error(f"GPT understanding failed: {e}")
            # 返回低置信度计划,触发规则降级
            return ExecutePlan(
                action="unknown",
                params={},
                user_message="",
                confidence=0.0,
                needs_clarification=False
            )

    def _format_context(self, context: Dict[str, Any]) -> str:
        """格式化上下文信息"""
        lines = [
            "## 当前上下文",
            f"- 工作目录: {context.get('working_dir', '~')}",
            f"- 上一次文件: {context.get('last_file', '无')}",
            f"- 上一次操作: {context.get('last_action', '无')}"
        ]

        # 添加最近对话历史
        history = context.get('conversation_history', [])
        if history:
            lines.append("\n## 最近对话")
            for item in history[-5:]:  # 只显示最近5条
                lines.append(f"- {item}")

        return "\n".join(lines)


class RuleFallback:
    """规则降级处理器 - 当GPT不可用时使用"""

    def __init__(self):
        """初始化规则处理器"""
        self.keywords_map = {
            'send_file': ['send', 'get', 'transfer', '发', '送', '传', '要'],
            'send_email': ['email', 'mail', '邮箱', '邮件'],
            'list_files': ['list', 'ls', 'file', 'dir', '文件', '目录', '有什么', 'show', '查看', '列出'],
            'status': ['status', '状态', '怎么样', 'how', 'system', '系统'],
            'create_file': ['create', 'new', '新建', '创建', 'make'],
            'help': ['help', '帮助', '怎么用', 'how to']
        }

    def understand(self, message: str, context: Dict[str, Any]) -> ExecutePlan:
        """使用规则匹配理解意图

        Args:
            message: 用户消息
            context: 上下文信息

        Returns:
            ExecutePlan: 执行计划
        """
        message_lower = message.lower()

        # 检查命令模式
        if message.startswith('/'):
            return self._handle_command(message, context)

        # 检查关键词
        for action, keywords in self.keywords_map.items():
            if any(kw in message_lower for kw in keywords):
                return self._build_simple_plan(action, message, context)

        # 无法理解
        return ExecutePlan(
            action="unknown",
            params={},
            user_message="我没太理解,能详细说一下吗?",
            confidence=0.3,
            needs_clarification=True
        )

    def _handle_command(self, message: str, context: Dict[str, Any]) -> ExecutePlan:
        """处理命令模式"""
        command = message.split()[0]

        command_map = {
            '/status': ('status', {}, '正在查看系统状态...'),
            '/ls': ('list_files', {'path': context.get('working_dir', '~')}, '正在列出文件...'),
            '/help': ('help', {}, '正在显示帮助...'),
        }

        if command in command_map:
            action, params, msg = command_map[command]
            return ExecutePlan(
                action=action,
                params=params,
                user_message=msg,
                confidence=0.95,
                needs_clarification=False
            )

        return ExecutePlan(
            action="unknown",
            params={},
            user_message=f"未知命令: {command}",
            confidence=0.0,
            needs_clarification=True
        )

    def _build_simple_plan(self, action: str, message: str, context: Dict[str, Any]) -> ExecutePlan:
        """构建简单的执行计划"""
        # 这里只做简单的意图识别,实际参数解析留给executor
        return ExecutePlan(
            action=action,
            params={},
            user_message=f"识别到意图: {action}",
            confidence=0.6,
            needs_clarification=False
        )
