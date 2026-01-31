#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试创建文件功能
"""

import asyncio
import sys
import os
from pathlib import Path
from unittest.mock import Mock

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from executor import ActionExecutor
from context import ConversationContext

async def test_create():
    print("=" * 60)
    print("  测试创建文件功能")
    print("=" * 60)

    # 加载配置
    import json
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 创建executor
    executor = ActionExecutor(config)
    context = ConversationContext()

    # 测试用例
    test_cases = [
        {
            'action': 'create_file',
            'params': {'filename': 'test.txt', 'location': 'Desktop'},
            'user_message': '测试创建test.txt',
            'confidence': 0.95
        },
        {
            'action': 'create_file',
            'params': {'filename': 'T1 S T. Txt', 'location': 'Desktop'},
            'user_message': '测试创建T1 S T. Txt',
            'confidence': 0.95
        },
        {
            'action': 'create_file',
            'params': {'filename': '测试文档.txt', 'location': 'Desktop'},
            'user_message': '测试创建中文文件名',
            'confidence': 0.95
        }
    ]

    # 创建mock对象
    class MockUpdate:
        class Message:
            async def reply_text(self, msg):
                print(f"Bot回复: {msg}")

        message = Message()

    update = MockUpdate()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['params']['filename']}")
        print("-" * 40)

        try:
            await executor.execute(test_case, update, None)
            print(f"✅ 测试 {i} 完成")
        except Exception as e:
            print(f"❌ 测试 {i} 失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("  检查桌面文件")
    print("=" * 60)

    desktop = Path.home() / 'Desktop'
    files = ['test.txt', 'T1 S T.Txt', '测试文档.txt']

    for filename in files:
        file_path = desktop / filename
        if file_path.exists():
            print(f"✅ {filename} 存在")
        else:
            print(f"❌ {filename} 不存在")

if __name__ == '__main__':
    asyncio.run(test_create())
