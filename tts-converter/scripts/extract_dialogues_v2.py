#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用对话提取工具 v2.0
支持多种广播剧脚本格式，自动识别角色列表
"""

import re
import sys
import argparse

class DialogueExtractor:
    def __init__(self, skip_role_list=True, min_dialogue_len=80):
        """
        初始化提取器

        Args:
            skip_role_list: 是否跳过角色列表部分
            min_dialogue_len: 判断为对话的最小长度（小于此长度视为角色描述）
        """
        self.skip_role_list = skip_role_list
        self.min_dialogue_len = min_dialogue_len
        self.in_role_list = True  # 是否在角色列表部分

    def extract_dialogues(self, input_file):
        """从脚本中提取对话"""
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        dialogues = []

        for line in lines:
            line = line.strip()

            # 匹配【角色名】对话内容格式
            match = re.match(r'^【(.+?)】(.+)$', line)
            if match:
                role = match.group(1)
                dialogue = match.group(2)

                # 检查是否是角色列表部分
                if self.skip_role_list and self.in_role_list:
                    # 遇到第一个长对话，说明角色列表结束
                    if len(dialogue) >= self.min_dialogue_len:
                        self.in_role_list = False
                    else:
                        # 仍在角色列表部分，跳过
                        continue

                # 替换冒号为逗号（提升TTS流畅度）
                dialogue = dialogue.replace('：', '，').replace(':', '，')

                if dialogue:
                    dialogues.append({
                        'role': role,
                        'text': dialogue
                    })

        return dialogues

    def optimize_dialogues(self, dialogues):
        """优化对话文本"""
        optimized = []

        for d in dialogues:
            # 去除多余空格
            text = ' '.join(d['text'].split())

            optimized.append({
                'role': d['role'],
                'text': text
            })

        return optimized

    def save_dialogues(self, dialogues, output_file):
        """保存对话到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for d in dialogues:
                f.write(f"【{d['role']}】{d['text']}\n")

    def get_stats(self, dialogues):
        """获取对话统计信息"""
        roles = set(d['role'] for d in dialogues)

        stats = {
            'total': len(dialogues),
            'roles': len(roles),
            'role_names': list(roles)
        }

        return stats

def main():
    parser = argparse.ArgumentParser(
        description='通用对话提取工具 - 支持多种广播剧脚本格式'
    )
    parser.add_argument('input', help='输入的脚本文件')
    parser.add_argument('-o', '--output', default='广播剧_对话.txt',
                       help='输出的对话文件（默认：广播剧_对话.txt）')
    parser.add_argument('--keep-role-list', action='store_true',
                       help='保留角色列表部分（不跳过）')
    parser.add_argument('--min-length', type=int, default=80,
                       help='判断为对话的最小长度（默认：80字）')
    parser.add_argument('--no-replace-colons', action='store_true',
                       help='不替换冒号为逗号')

    args = parser.parse_args()

    print(f"[INFO] 读取脚本: {args.input}")
    print(f"[INFO] 最小对话长度: {args.min_length}字")
    print(f"[INFO] 跳过角色列表: {not args.keep_role_list}")

    # 创建提取器
    extractor = DialogueExtractor(
        skip_role_list=not args.keep_role_list,
        min_dialogue_len=args.min_length
    )

    # 提取对话
    dialogues = extractor.extract_dialogues(args.input)

    # 如果不替换冒号
    if args.no_replace_colons:
        for d in dialogues:
            # 恢复冒号
            d['text'] = d['text'].replace('，', '：')

    # 优化对话
    dialogues = extractor.optimize_dialogues(dialogues)

    # 保存对话
    extractor.save_dialogues(dialogues, args.output)
    print(f"[OK] 对话已保存: {args.output}")

    # 统计信息
    stats = extractor.get_stats(dialogues)
    print(f"\n[统计]")
    print(f"  总对话数: {stats['total']}")
    print(f"  角色数: {stats['roles']}")
    print(f"  角色列表: {', '.join(stats['role_names'])}")

    # 预览前5条
    print(f"\n[预览] 前5条对话:")
    for i, d in enumerate(dialogues[:5], 1):
        preview = d['text'][:60] + '...' if len(d['text']) > 60 else d['text']
        print(f"  {i}. 【{d['role']}】{preview}")

    print(f"\n[提示] 下一步，使用以下命令生成音频:")
    print(f"  python drama_to_audio.py {args.output} 输出音频.mp3")

if __name__ == '__main__':
    main()
