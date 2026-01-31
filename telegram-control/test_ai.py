#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试GPT-4o自然语言理解
"""

import json
from intent_layer import GPTIntentUnderstander
from context import ConversationContext

# 初始化
print("=" * 60)
print("  测试GPT-4o自然语言理解")
print("=" * 60)

# 加载配置
import os
config_path = os.path.join(os.path.dirname(__file__), 'llm_config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    llm_config = json.load(f)

# 初始化理解器
understander = GPTIntentUnderstander(
    api_key=llm_config['openai_api_key'],
    model=llm_config['openai_model']
)

# 初始化上下文
context = ConversationContext()

# 测试用例
test_cases = [
    "查看系统状态",
    "桌面有什么文件",
    "把那个报告发给我",
    "把它发邮箱",
    "再来一次",
    "看看下载文件夹",
    "新建一个test.txt",
    "帮我看状态",
]

print("\n开始测试...\n")

for i, message in enumerate(test_cases, 1):
    print(f"[测试 {i}] 用户说: {message}")
    print("-" * 40)

    try:
        # 理解意图
        plan = understander.understand(message, context.get_data())

        # 显示结果
        print(f"动作: {plan.action}")
        print(f"参数: {plan.params}")
        print(f"回复: {plan.user_message}")
        print(f"置信度: {plan.confidence:.2f}")

        # 更新上下文(模拟)
        if plan.action in ['send_file', 'send_email']:
            if plan.params.get('file_path'):
                context.data['last_file'] = plan.params['file_path']
        context.data['last_action'] = plan.action

    except Exception as e:
        print(f"错误: {e}")

    print()

print("=" * 60)
print("测试完成!")
print("=" * 60)
