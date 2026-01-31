#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code AI监听器 - 使用GPT-4o真正理解消息
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
    """处理请求文件"""

    def __init__(self, response_dir, openai_api_key):
        self.response_dir = Path(response_dir)
        self.client = OpenAI(api_key=openai_api_key)
        self.context = {
            'last_file': None,
            'last_action': None
        }

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

            # 使用GPT-4o理解并执行
            result = self.process_with_gpt4o(message)

            # 写入响应
            response_file = self.response_dir / f"{request_id}.txt"
            response_data = {
                'success': True,
                'result': result,
                'files': self.extract_files(result)
            }

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

    def extract_files(self, result):
        """从结果中提取文件路径"""
        import re
        files = []

        # 提取"路径: xxx"
        match = re.search(r'路径[::]\s*(.+?)(?:\n|$)', result)
        if match:
            file_path = match.group(1).strip()
            if os.path.exists(file_path):
                files.append(file_path)

        return files

    def process_with_gpt4o(self, message: str) -> str:
        """使用GPT-4o理解消息并执行"""
        try:
            # 构建上下文
            context_info = f"""
当前上下文:
- 上一次文件: {self.context.get('last_file', '无')}
- 上一次操作: {self.context.get('last_action', '无')}
- 桌面路径: {Path.home() / 'Desktop'}
"""

            # 调用GPT-4o
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""你是Claude Code，用户的智能助手。

{context_info}

用户会用中文和你聊天，描述他们想要做什么。

你的任务是:
1. 理解用户的真实意图
2. 直接执行操作
3. 返回简洁的结果

支持的操作:
- 创建文件: 在~/Desktop创建文件
- 列出文件: 列出目录内容
- 查看状态: CPU、内存等
- 其他: 尝试理解并执行

重要规则:
- 文件名中的空格和标点要保留
- 文件扩展名前的空格要移除: ". Txt" -> ".txt"
- 理解"那个文件"、"它"等指代词
- 如果不理解，礼貌地询问

返回格式:
直接返回执行结果，用简洁的中文描述。
"""
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0.1
            )

            result = response.choices[0].message.content

            # 尝试解析并执行（简单规则，主要靠GPT-4o理解）
            if '创建' in message or '新建' in message:
                # 让GPT-4o告诉我们要创建什么文件
                filename_response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "提取文件名。只返回文件名，不要其他内容。"
                        },
                        {
                            "role": "user",
                            "content": f"用户说: {message}\n\n如果要创建文件，文件名是什么？只返回文件名。"
                        }
                    ],
                    temperature=0
                )

                filename = filename_response.choices[0].message.content.strip()
                filename = filename.strip('"').strip("'").strip('.')

                # 清理文件名
                import re
                filename = re.sub(r'\.\s+(\w+)', r'.\1', filename)

                # 创建文件
                desktop = Path.home() / 'Desktop'
                file_path = desktop / filename
                file_path.touch()

                result = f"[OK] 已创建文件: {filename}\n路径: {file_path}"
                self.context['last_file'] = str(file_path)
                self.context['last_action'] = 'create_file'

            return result

        except Exception as e:
            return f"[X] 处理失败: {e}"


def main():
    print("=" * 60)
    print("  Claude Code AI监听器")
    print("  使用GPT-4o理解消息")
    print("=" * 60)

    # 加载API key
    llm_config_file = Path(__file__).parent / 'llm_config.json'
    with open(llm_config_file, 'r', encoding='utf-8') as f:
        llm_config = json.load(f)

    api_key = llm_config.get('openai_api_key')
    if not api_key:
        print("错误: 未配置OpenAI API Key")
        sys.exit(1)

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
    print("\nAI监听器已启动，等待消息...\n")

    # 创建监听器
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
