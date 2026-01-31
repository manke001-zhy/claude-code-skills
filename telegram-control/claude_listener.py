#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code监听器 - 接收Telegram消息并调用Claude Code处理
"""

import os
import sys
import json
import logging
import tempfile
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class RequestHandler(FileSystemEventHandler):
    """处理请求文件"""

    def __init__(self, response_dir):
        self.response_dir = Path(response_dir)

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if not file_path.suffix == '.txt':
            return

        logger.info(f"发现新请求: {file_path}")

        try:
            # 读取请求
            with open(file_path, 'r', encoding='utf-8') as f:
                request_data = json.load(f)

            message = request_data.get('message', '')
            request_id = file_path.stem

            logger.info(f"消息内容: {message}")

            # 调用Claude Code处理
            result = self.process_with_claude(message)

            # 写入响应
            response_file = self.response_dir / f"{request_id}.txt"
            response_data = {
                'success': True,
                'result': result,
                'files': []
            }

            # 如果有文件路径，添加到响应
            if '文件已创建' in result or '已发送' in result:
                # 尝试提取文件路径
                import re
                file_match = re.search(r'路径: (.+)', result)
                if file_match:
                    file_path = file_match.group(1).strip()
                    if os.path.exists(file_path):
                        response_data['files'].append(file_path)

            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)

            logger.info(f"响应已写入: {response_file}")

        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            # 写入错误响应
            response_file = self.response_dir / f"{request_id}.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'success': False,
                    'error': str(e)
                }, f, ensure_ascii=False, indent=2)

    def process_with_claude(self, message: str) -> str:
        """调用Claude Code处理消息"""
        try:
            import subprocess

            # 尝试理解消息并执行
            result = f"[Claude Code] 收到消息: {message}\n\n"

            # 如果是创建文件
            if '新建' in message or '创建' in message or '建立' in message:
                import re
                # 更好的文件名提取
                # 匹配: xxx.txt, xxx.docx等
                filename_match = re.search(r'([a-zA-Z0-9_\u4e00-\u9fff]+\.[a-zA-Z0-9]+)', message)
                if filename_match:
                    filename = filename_match.group(1)
                    # 清理文件名
                    filename = re.sub(r'\.\s+(\w+)', r'.\1', filename)

                    from pathlib import Path
                    desktop = Path.home() / 'Desktop'
                    file_path = desktop / filename

                    file_path.touch()
                    result += f"[OK] 已创建文件: {filename}\n路径: {file_path}"
                else:
                    result += "[!] 无法识别文件名，请重新描述"

            # 如果是列出文件
            elif '有什么' in message or '列出' in message or '看看' in message or '显示' in message:
                from pathlib import Path
                desktop = Path.home() / 'Desktop'
                files = list(desktop.iterdir())[:20]

                result += f"📁 Desktop:\n"
                for f in files:
                    if f.is_dir():
                        result += f"  📂 {f.name}/\n"
                    else:
                        result += f"  📄 {f.name}\n"

            # 如果是查看状态
            elif '状态' in message or '怎么样' in message:
                try:
                    import psutil
                    cpu = psutil.cpu_percent()
                    memory = psutil.virtual_memory()
                    result += f"[PC] CPU:{cpu}% 内存:{memory.used/(1024**3):.1f}GB"
                except:
                    result += "[!] 需要安装 psutil"

            else:
                result += f"[?] 未完全理解，但已收到: {message}"

            return result

        except Exception as e:
            return f"[X] 处理失败: {e}"


def main():
    print("=" * 60)
    print("  Claude Code监听器")
    print("  监听Telegram消息并处理")
    print("=" * 60)

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建目录
    request_dir = Path(tempfile.gettempdir()) / 'claude_requests'
    response_dir = Path(tempfile.gettempdir()) / 'claude_responses'
    request_dir.mkdir(exist_ok=True)
    response_dir.mkdir(exist_ok=True)

    print(f"请求目录: {request_dir}")
    print(f"响应目录: {response_dir}")
    print("\n监听器已启动，等待消息...\n")

    # 创建监听器
    event_handler = RequestHandler(response_dir)
    observer = Observer()
    observer.schedule(event_handler, str(request_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n监听器已停止")

    observer.join()


if __name__ == '__main__':
    main()
