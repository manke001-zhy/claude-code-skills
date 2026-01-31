#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数 - 文件搜索、安全验证等
"""

import os
import re
import logging
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


def search_file(filename: str, search_dirs: Optional[List[str]] = None) -> Optional[str]:
    """智能文件搜索

    Args:
        filename: 文件名
        search_dirs: 搜索目录列表(默认Desktop和Downloads)

    Returns:
        找到的文件完整路径,如果找不到返回None
    """
    if not filename:
        logger.warning("search_file: filename is None")
        return None

    logger.info(f"Searching for file: {filename}")

    # 默认搜索目录
    if search_dirs is None:
        search_dirs = [
            Path.home() / 'Desktop',
            Path.home() / 'Downloads'
        ]

    # 1. 精确匹配
    for search_dir in search_dirs:
        if not isinstance(search_dir, Path):
            search_dir = Path(search_dir)

        if not search_dir.exists():
            logger.debug(f"Search dir not exists: {search_dir}")
            continue

        file_path = search_dir / filename
        logger.debug(f"Checking exact: {file_path}, exists: {file_path.exists()}")

        if file_path.exists():
            logger.info(f"Found by exact match: {file_path}")
            return str(file_path)

    # 2. 模糊匹配
    for search_dir in search_dirs:
        if not isinstance(search_dir, Path):
            search_dir = Path(search_dir)

        if not search_dir.exists():
            continue

        logger.debug(f"Fuzzy searching in {search_dir}...")

        try:
            for file_in_dir in search_dir.iterdir():
                if file_in_dir.is_file():
                    # 包含匹配
                    if filename.lower() in file_in_dir.name.lower():
                        logger.info(f"Found by fuzzy match: {file_in_dir}")
                        return str(file_in_dir)
        except Exception as e:
            logger.warning(f"Error searching in {search_dir}: {e}")

    logger.warning(f"File not found: {filename}")
    return None


def validate_path(path: str) -> bool:
    """验证文件路径是否安全

    Args:
        path: 文件路径

    Returns:
        是否安全
    """
    if not path:
        return False

    try:
        # 解析为绝对路径
        resolved = os.path.realpath(path)
        home = os.path.expanduser('~')

        # 不允许访问系统目录
        system_paths = ['/proc', '/sys', '/dev']
        if any(resolved.startswith(p) for p in system_paths):
            logger.warning(f"Path rejected (system path): {path}")
            return False

        # 允许用户目录和临时目录
        if resolved.startswith(home) or resolved.startswith('/tmp'):
            return True

        logger.warning(f"Path rejected (outside user dir): {path}")
        return False

    except Exception as e:
        logger.error(f"Path validation error: {e}")
        return False


class SecurityValidator:
    """安全验证器"""

    # 危险命令模式
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf',
        r'format\s+[a-z]:',
        r'mkfs',
        r'dd\s+if=',
        r'>\s+/dev/',
        r'shutdown',
        r'reboot',
        r'poweroff',
        r'halt',
        r'init\s+0'
    ]

    @staticmethod
    def validate_command(command: str) -> tuple[bool, Optional[str]]:
        """验证命令是否安全

        Args:
            command: 要执行的命令

        Returns:
            (是否安全, 错误消息)
        """
        if not command:
            return False, "命令为空"

        command_lower = command.lower()

        # 检查危险模式
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, command_lower):
                logger.warning(f"Dangerous command blocked: {command}")
                return False, f"危险命令已被阻止: {pattern}"

        return True, None

    @staticmethod
    def validate_file_operation(file_path: str, operation: str = 'read') -> tuple[bool, Optional[str]]:
        """验证文件操作是否安全

        Args:
            file_path: 文件路径
            operation: 操作类型(read/write/delete)

        Returns:
            (是否安全, 错误消息)
        """
        if not file_path:
            return False, "文件路径为空"

        # 路径验证
        if not validate_path(file_path):
            return False, "不允许访问系统目录"

        # 检查文件大小(针对发送操作)
        if operation in ['read', 'send']:
            if os.path.exists(file_path):
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if size_mb > 100:
                    return False, f"文件过大: {size_mb:.1f}MB (最大100MB)"

        return True, None


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def extract_filename_from_message(message: str) -> Optional[str]:
    """从消息中提取文件名

    Args:
        message: 用户消息

    Returns:
        提取的文件名或None
    """
    # 常见文件扩展名
    extensions = r'(?:pdf|doc|docx|xls|xlsx|ppt|pptx|txt|md|csv|rtf|odt|ods|odp|mp3|mp4|wav|png|jpg|jpeg|gif|bmp|zip|rar|7z)'

    # 匹配文件名模式
    file_pattern = rf'([\u4e00-\u9fff\w\-\.]+\.{extensions})'

    match = re.search(file_pattern, message, re.IGNORECASE)
    if match:
        filename = match.group(1)
        # 清理文件名(去除标点)
        filename = filename.rstrip('。给到发送邮箱邮寄上传，,、')
        filename = filename.lstrip('把将要')
        return filename

    return None


def extract_email_from_message(message: str) -> Optional[str]:
    """从消息中提取邮箱地址

    Args:
        message: 用户消息

    Returns:
        提取的邮箱地址或None
    """
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    match = re.search(email_pattern, message)
    return match.group(0) if match else None


def is_command(message: str) -> bool:
    """判断是否是命令(以/开头)

    Args:
        message: 用户消息

    Returns:
        是否是命令
    """
    return message.strip().startswith('/')


def parse_command(message: str) -> tuple[str, list[str]]:
    """解析命令

    Args:
        message: 用户消息

    Returns:
        (命令, 参数列表)
    """
    parts = message.strip().split()
    if not parts:
        return '', []

    command = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    return command, args
