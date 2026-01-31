#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能Claude Code监听器 - 真正理解并执行
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

try:
    from openai import OpenAI
except ImportError:
    print("需要安装: pip install openai")
    sys.exit(1)

logger = logging.getLogger(__name__)


class RequestHandler(FileSystemEventHandler):
    """处理请求文件 - 使用GPT-4o理解"""

    def __init__(self, response_dir, openai_api_key):
        self.response_dir = Path(response_dir)
        self.client = OpenAI(api_key=openai_api_key)

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

            logger.info(f"消息: {message}")

            # 使用GPT-4o理解和执行
            result = self.execute_with_gpt4o(message)

            # 写入响应
            response_file = self.response_dir / f"{request_id}.txt"
            response_data = {
                'success': True,
                'result': result.get('text', ''),
                'send_file': result.get('send_file', None),  # 要发送的文件路径
                'file_list': result.get('file_list', None),  # 文件列表（用于创建按钮）
                'files': []
            }

            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, ensure_ascii=False, indent=2)

            logger.info(f"响应已写入")

        except Exception as e:
            logger.error(f"处理失败: {e}")
            response_file = self.response_dir / f"{request_id}.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'success': False,
                    'error': str(e)
                }, f, ensure_ascii=False, indent=2)

    def execute_with_gpt4o(self, message: str) -> dict:
        """使用GPT-4o理解并执行"""
        try:
            desktop = Path.home() / 'Desktop'

            # 先让GPT-4o分析用户的意图
            analysis = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """分析用户的意图，返回JSON格式。
支持的操作:
1. create_file - 创建文件
2. write_file - 写入文件内容
3. read_file - 读取文件
4. list_files - 列出文件
5. delete_file - 删除文件
6. send_file - 发送文件到Telegram
7. copy_file - 复制文件（生成副本，文件名加_copy）
8. status - 查看状态

返回格式(JSON):
{
    "action": "操作类型",
    "filename": "文件名(如果需要)",
    "content": "内容(如果需要)",
    "explanation": "解释"
}

重要:
- 文件名要提取准确，不要包含操作词
- 如果用户说"ai助手.txt写入123"，filename是"ai助手.txt"，content是"123"
- 如果用户说"把视频.mp4发给我"，filename是"视频.mp4"，action是"send_file"
- 如果用户说"复制test.txt"或"test.txt复制一份"，action是"copy_file"，filename是"test.txt"
- 中文文件名要保留
- 文件扩展名前的空格要移除"""
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0
            )

            intent = json.loads(analysis.choices[0].message.content)
            logger.info(f"GPT-4o理解的意图: {intent}")

            action = intent.get('action')
            filename = intent.get('filename', '')
            content = intent.get('content', '')

            # 执行操作
            if action == 'create_file' or action == 'write_file':
                if not filename:
                    return {'text': "[!] 无法识别文件名，请重新描述"}

                # 清理文件名
                import re
                filename = re.sub(r'\.\s+(\w+)', r'.\1', filename)

                file_path = desktop / filename

                # 写入内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    if content:
                        f.write(content)
                    # 如果没有内容，创建空文件

                return {'text': f"[OK] 文件已处理\n文件: {filename}\n路径: {file_path}\n内容: {content if content else '(空文件)'}"}

            elif action == 'copy_file':
                """复制文件"""
                if not filename:
                    return {'text': "[!] 请指定要复制的文件名"}

                # 在桌面查找文件
                file_path = desktop / filename

                # 如果找不到，尝试模糊搜索
                if not file_path.exists():
                    for f in desktop.iterdir():
                        if filename.lower() in f.name.lower() and f.is_file():
                            file_path = f
                            logger.info(f"找到文件: {file_path}")
                            break

                if file_path.exists():
                    # 生成新的文件名（添加_copy后缀）
                    import shutil
                    name = file_path.stem
                    ext = file_path.suffix
                    new_name = f"{name}_copy{ext}"
                    new_path = desktop / new_name

                    # 如果文件已存在，添加数字后缀
                    counter = 1
                    while new_path.exists():
                        new_name = f"{name}_copy{counter}{ext}"
                        new_path = desktop / new_name
                        counter += 1

                    # 复制文件
                    shutil.copy2(file_path, new_path)

                    # 获取文件大小
                    size = new_path.stat().st_size
                    size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"

                    return {'text': f"[OK] 文件已复制\n原文件: {file_path.name}\n新文件: {new_name}\n路径: {new_path}\n大小: {size_str}"}
                else:
                    return {'text': f"[!] 文件不存在: {filename}"}

            elif action == 'send_file':
                """发送文件到Telegram"""
                if not filename:
                    return {'text': "[!] 请指定要发送的文件名"}

                # 在桌面查找文件
                file_path = desktop / filename

                # 如果找不到，尝试模糊搜索
                if not file_path.exists():
                    for f in desktop.iterdir():
                        if filename.lower() in f.name.lower() and f.is_file():
                            file_path = f
                            logger.info(f"找到文件: {file_path}")
                            break

                if file_path.exists():
                    # 检查文件大小（Telegram限制50MB，Bot限制100MB）
                    file_size = file_path.stat().st_size
                    if file_size > 100 * 1024 * 1024:
                        return {'text': f"[!] 文件过大: {file_size/(1024*1024):.1f}MB (最大100MB)"}

                    file_size_str = f"{file_size/1024:.1f}KB" if file_size < 1024*1024 else f"{file_size/(1024*1024):.1f}MB"

                    return {
                        'text': f"[OK] 正在发送文件: {file_path.name} ({file_size_str})",
                        'send_file': str(file_path)
                    }
                else:
                    return {'text': f"[!] 文件不存在: {filename}"}

            elif action == 'list_files':
                files = list(desktop.iterdir())
                result = [f"[列表] {os.path.basename(desktop)}: (共{len(files)}项)"]
                file_list = []  # 结构化文件列表

                # 只显示文件，不显示文件夹（简化）
                for f in files:
                    if f.is_file():  # 只处理文件
                        size = f.stat().st_size
                        size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/(1024*1024):.1f}MB"
                        result.append(f"  [文件] {f.name} ({size_str})")
                        file_list.append({
                            'name': f.name,
                            'type': 'file',
                            'path': str(f),
                            'size': size_str,
                            'ext': f.suffix.lower()
                        })

                return {
                    'text': "\n".join(result),
                    'file_list': file_list  # 添加结构化文件列表
                }

            elif action == 'read_file':
                if not filename:
                    return {'text': "[!] 请指定文件名"}

                file_path = desktop / filename
                if not file_path.exists():
                    # 尝试模糊搜索
                    for f in desktop.iterdir():
                        if filename.lower() in f.name.lower():
                            file_path = f
                            break

                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    return {'text': f"[OK] 文件内容:\n\n{file_content}"}
                else:
                    return {'text': f"[!] 文件不存在: {filename}"}

            elif action == 'delete_file':
                if not filename:
                    return {'text': "[!] 请指定文件名"}

                file_path = desktop / filename
                if file_path.exists():
                    file_path.unlink()
                    return {'text': f"[OK] 已删除: {filename}"}
                else:
                    return {'text': f"[!] 文件不存在: {filename}"}

            elif action == 'status':
                try:
                    import psutil
                    cpu = psutil.cpu_percent()
                    memory = psutil.virtual_memory()
                    return {'text': f"[PC状态] CPU: {cpu}% | 内存: {memory.used/(1024**3):.1f}GB / {memory.total/(1024**3):.1f}GB"}
                except:
                    return {'text': "[!] 需要安装 psutil"}

            else:
                return {'text': f"[?] 未完全理解: {intent.get('explanation', '无解释')}"}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'text': f"[X] 执行失败: {e}"}


def main():
    print("=" * 60)
    print("  Claude Code智能监听器")
    print("  真正理解并执行")
    print("=" * 60)

    # 加载API key
    llm_config_file = Path(__file__).parent / 'llm_config.json'
    with open(llm_config_file, 'r', encoding='utf-8') as f:
        llm_config = json.load(f)

    api_key = llm_config.get('openai_api_key')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    request_dir = Path(tempfile.gettempdir()) / 'claude_requests'
    response_dir = Path(tempfile.gettempdir()) / 'claude_responses'
    request_dir.mkdir(exist_ok=True)
    response_dir.mkdir(exist_ok=True)

    print(f"请求目录: {request_dir}")
    print(f"响应目录: {response_dir}")
    print("\n监听器已启动\n")

    event_handler = RequestHandler(response_dir, api_key)
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
