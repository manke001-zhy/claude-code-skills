#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行层 - 统一的动作执行器
"""

import os
import sys
import subprocess
import asyncio
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# 技能目录
SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ActionExecutor:
    """统一的动作执行器"""

    def __init__(self, config: Dict):
        """初始化执行器

        Args:
            config: Bot配置字典
        """
        self.config = config
        self.working_dir = os.path.expanduser('~')

    async def execute(self, plan: Dict, update, context):
        """执行计划

        Args:
            plan: 执行计划字典(action, params, user_message, confidence等)
            update: Telegram update对象
            context: Telegram context对象
        """
        action = plan.get('action', 'unknown')
        params = plan.get('params', {})

        # 获取对应的执行方法
        handler_name = f'_exec_{action}'
        handler = getattr(self, handler_name, self._exec_unknown)

        # 执行
        try:
            return await handler(params, update, context)
        except Exception as e:
            logger.error(f"Execution failed for {action}: {e}")
            await update.message.reply_text(f"[X] 执行失败: {e}")

    async def _exec_send_file(self, params: Dict, update, context):
        """执行发送文件"""
        file_path = params.get('file_path')

        if not file_path:
            await update.message.reply_text("[X] 请指定文件路径")
            return

        # 展开路径
        if file_path.startswith('~'):
            file_path = os.path.expanduser(file_path)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            await update.message.reply_text(f"[X] 文件不存在: {file_path}")
            return

        # 检查文件大小
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > 100:
            await update.message.reply_text(f"[X] 文件过大: {size_mb:.1f}MB (最大100MB)")
            return

        try:
            await update.message.reply_text(f"正在发送: {os.path.basename(file_path)} ({size_mb:.1f}MB)...")

            with open(file_path, 'rb') as f:
                await update.message.reply_document(f)

            logger.info(f"File sent: {file_path}")

        except Exception as e:
            logger.error(f"Send file failed: {e}")
            await update.message.reply_text(f"[X] 发送文件失败: {e}")

    async def _exec_send_email(self, params: Dict, update, context):
        """执行发送邮件 - 调用file-share技能"""
        file_path = params.get('file_path')
        receiver = params.get('receiver', self.config.get('default_receiver', 'manke_zhy@qq.com'))

        if not file_path:
            await update.message.reply_text("[X] 请指定文件路径")
            return

        # 展开路径
        if file_path.startswith('~'):
            file_path = os.path.expanduser(file_path)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            await update.message.reply_text(f"[X] 文件不存在: {file_path}")
            return

        # 获取file-share脚本路径
        file_share_dir = os.path.join(SKILLS_DIR, 'file-share')
        send_email_script = os.path.join(file_share_dir, 'send_email.py')

        if not os.path.exists(send_email_script):
            await update.message.reply_text("[X] file-share技能未安装")
            return

        # 构建命令
        cmd = [sys.executable, send_email_script, '--file', file_path, '--receiver', receiver]

        logger.info(f"Email command: {' '.join(cmd)}")

        try:
            await update.message.reply_text(f"正在发送邮件: {os.path.basename(file_path)}...")

            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                await update.message.reply_text(
                    f"[OK] 邮件发送成功!\n\n"
                    f" 文件: {os.path.basename(file_path)}\n"
                    f"📮 收件人: {receiver}"
                )
                logger.info(f"Email sent: {file_path} to {receiver}")
            else:
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else 'Unknown error'
                logger.error(f"Email script failed: {error_msg}")
                await update.message.reply_text(f"[X] 邮件发送失败\n\n错误: {error_msg}")

        except Exception as e:
            logger.error(f"Email send exception: {e}")
            await update.message.reply_text(f"[X] 发送邮件时出错: {e}")

    async def _exec_list_files(self, params: Dict, update, context):
        """执行列出文件"""
        path = params.get('path', self.working_dir)

        # 展开路径
        if path.startswith('~'):
            path = os.path.expanduser(path)

        # 检查目录是否存在
        if not os.path.exists(path):
            await update.message.reply_text(f"[X] 目录不存在: {path}")
            return

        if not os.path.isdir(path):
            await update.message.reply_text(f"[X] 不是目录: {path}")
            return

        try:
            files = os.listdir(path)

            if not files:
                await update.message.reply_text(f" 目录为空: {os.path.basename(path)}")
                return

            # 限制显示数量
            file_list = []
            for f in files[:25]:
                full_path = os.path.join(path, f)
                if os.path.isdir(full_path):
                    file_list.append(f" {f}/")
                else:
                    size = os.path.getsize(full_path)
                    size_str = f"{size / 1024:.1f}KB" if size < 1024**2 else f"{size / (1024**2):.1f}MB"
                    file_list.append(f" {f} ({size_str})")

            if len(files) > 25:
                file_list.append(f"\n... 还有 {len(files) - 25} 个文件")

            msg = f" 目录: {os.path.basename(path)}\n\n" + "\n".join(file_list)
            await update.message.reply_text(msg)

        except Exception as e:
            logger.error(f"List files failed: {e}")
            await update.message.reply_text(f"[X] 列出文件失败: {e}")

    async def _exec_run_command(self, params: Dict, update, context):
        """执行系统命令"""
        command = params.get('command', '')

        if not command:
            await update.message.reply_text("[X] 请指定命令")
            return

        # 安全检查
        dangerous = ['rm -rf', 'format', 'mkfs', 'dd if=', '> /dev/', 'shutdown', 'reboot']
        if any(d in command for d in dangerous):
            await update.message.reply_text("[X] 危险命令已被阻止")
            return

        try:
            await update.message.reply_text(f"执行命令: {command}")

            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout if result.stdout else result.stderr

            # 限制输出长度
            if len(output) > 3000:
                output = output[:3000] + "\n... (已截断)"

            await update.message.reply_text(f"结果:\n{output}")

        except subprocess.TimeoutExpired:
            await update.message.reply_text("[X] 命令超时(60s)")
        except Exception as e:
            logger.error(f"Run command failed: {e}")
            await update.message.reply_text(f"[X] 执行命令失败: {e}")

    async def _exec_call_skill(self, params: Dict, update, context):
        """调用其他技能"""
        skill_name = params.get('skill', '')
        source = params.get('source', '')

        if not skill_name:
            await update.message.reply_text("[X] 请指定技能名称")
            return

        # 检查技能是否存在
        skill_dir = os.path.join(SKILLS_DIR, skill_name)
        if not os.path.exists(skill_dir):
            await update.message.reply_text(f"[X] 技能不存在: {skill_name}")
            return

        await update.message.reply_text(
            f" 调用技能: {skill_name}\n\n"
            f"参数: {source or '无'}\n\n"
            f"提示: 技能调用需要在本地手动完成"
        )

        logger.info(f"Skill called: {skill_name} with params: {params}")

    async def _exec_create_file(self, params: Dict, update, context):
        """创建新文件"""
        filename = params.get('filename', '')
        location = params.get('location', 'Desktop')

        if not filename:
            await update.message.reply_text("[X] 请指定文件名")
            return

        try:
            # 清理文件名（移除非法字符和多余空格）
            import re
            # 移除扩展名前后的空格，但保留文件名中的空格
            # 例如: "T1 S T. Txt" -> "T1 S T.txt"
            filename = re.sub(r'\.\s+(\w+)', r'.\1', filename)

            logger.info(f"Creating file: {filename} in {location}")

            # 确定创建目录
            if location == 'Desktop':
                target_dir = Path.home() / 'Desktop'
            elif location == 'Downloads':
                target_dir = Path.home() / 'Downloads'
            else:
                target_dir = Path.home() / 'Desktop'

            # 创建完整路径
            file_path = target_dir / filename

            # 检查文件是否已存在
            if file_path.exists():
                await update.message.reply_text(
                    f"[!] 文件已存在: {filename}\n\n"
                    f"位置: {file_path}"
                )
                return

            # 创建文件
            file_path.touch()

            await update.message.reply_text(
                f"[OK] 文件创建成功!\n\n"
                f"文件名: {filename}\n"
                f"位置: {location}\n"
                f"路径: {file_path}"
            )

            logger.info(f"File created: {file_path}")

        except PermissionError:
            await update.message.reply_text(f"[X] 权限不足，无法创建文件")
            logger.error(f"Permission denied creating file: {filename}")
        except OSError as e:
            await update.message.reply_text(f"[X] 文件名不合法或路径错误: {e}")
            logger.error(f"OS error creating file: {filename}, error: {e}")
        except Exception as e:
            logger.error(f"Create file failed: {e}")
            await update.message.reply_text(f"[X] 创建文件失败: {e}")

    async def _exec_status(self, params: Dict, update, context):
        """查看系统状态"""
        try:
            import psutil
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            msg = f"💻 系统状态\n\n" \
                  f"CPU: {cpu}%\n" \
                  f"内存: {memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB\n" \
                  f"磁盘: {disk.used / (1024**3):.1f}GB / {disk.total / (1024**3):.1f}GB\n\n" \
                  f" 当前目录: {self.working_dir}"

            await update.message.reply_text(msg)

        except ImportError:
            await update.message.reply_text("[X] 需要安装 psutil: pip install psutil")
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            await update.message.reply_text(f"[X] 获取状态失败: {e}")

    async def _exec_repeat(self, params: Dict, update, context):
        """重复上一次操作"""
        # 这个方法不应该被直接调用
        # repeat逻辑在bot_core中处理,通过重新执行上一次的计划
        await update.message.reply_text("[X] repeat操作需要在Bot层处理")

    async def _exec_help(self, params: Dict, update, context):
        """显示帮助"""
        help_text = """ Claude Code Bot - 自然语言控制

自然语言示例:
• 查看系统状态
• 列出桌面文件
• 把 report.pdf 发给我
• 发送邮件给 friend@qq.com
• 在桌面新建 test.txt

命令列表:
/status - 系统状态
/ls - 列出文件
/get <file> - 获取文件
/help - 显示帮助

提示: 直接用自然语言说话即可!
"""
        await update.message.reply_text(help_text)

    async def _exec_unknown(self, params: Dict, update, context):
        """未知动作"""
        await update.message.reply_text(
            "❓ 我没太理解你的意思\n\n"
            "试试这样:\n"
            "• 查看状态\n"
            "• 列出文件\n"
            "• 发送文件\n"
            "• 发送 /help"
        )
