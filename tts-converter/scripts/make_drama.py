#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广播剧制作工具
一键式从Markdown脚本到MP3音频
"""

import re
import sys
import argparse

def extract_dialogues(input_file):
    """从Markdown脚本中提取纯对话"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    dialogues = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 匹配角色标记: **\[角色\]**：
        if '**\\[' in line and ']**' in line and ('：' in line or ':' in line):
            # 提取角色名
            start = line.find('[') + 1
            end = line.rfind(']')

            if start > 0 and end > start:
                role_full = line[start:end]

                # 获取纯角色名
                if '：' in role_full:
                    role = role_full.split('：')[0].strip()
                else:
                    role = role_full.strip()

                # 查找对话内容
                i += 1
                dialogue_found = False

                # 跳过空行
                while i < len(lines) and not lines[i].strip():
                    i += 1

                # 获取对话
                if i < len(lines):
                    dialogue_line = lines[i].rstrip()

                    # 去除动作描述
                    clean_dialogue = dialogue_line
                    while '\\[' in clean_dialogue:
                        start_bracket = clean_dialogue.find('\\[')
                        end_bracket = clean_dialogue.find('\\]', start_bracket)
                        if end_bracket > start_bracket:
                            clean_dialogue = clean_dialogue[:start_bracket] + clean_dialogue[end_bracket+2:]
                        else:
                            break

                    # 去除普通括号中的动作
                    while '[' in clean_dialogue:
                        start_bracket = clean_dialogue.find('[')
                        end_bracket = clean_dialogue.find(']', start_bracket)
                        if end_bracket > start_bracket:
                            clean_dialogue = clean_dialogue[:start_bracket] + clean_dialogue[end_bracket+1:]
                        else:
                            break

                    clean_dialogue = ' '.join(clean_dialogue.split())

                    if clean_dialogue:
                        dialogues.append({
                            'role': role,
                            'text': clean_dialogue
                        })
                        dialogue_found = True

        i += 1

    return dialogues

def optimize_dialogues(dialogues, replace_colons=True):
    """优化对话文本"""
    optimized = []

    for d in dialogues:
        text = d['text']

        # 替换冒号为逗号（提升TTS流畅度）
        if replace_colons:
            text = text.replace('：', '，').replace(':', '，')

        optimized.append({
            'role': d['role'],
            'text': text
        })

    return optimized

def save_dialogues(dialogues, output_file):
    """保存对话到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for d in dialogues:
            f.write(f"【{d['role']}】{d['text']}\n")

def main():
    parser = argparse.ArgumentParser(description='广播剧制作工具')
    parser.add_argument('input', help='输入的Markdown脚本文件')
    parser.add_argument('-o', '--output', default='广播剧_对话.txt', help='输出的对话文件')
    parser.add_argument('--keep-colons', action='store_true', help='保留冒号（不替换为逗号）')

    args = parser.parse_args()

    print(f"[INFO] 读取脚本: {args.input}")

    # 提取对话
    dialogues = extract_dialogues(args.input)
    print(f"[INFO] 提取到 {len(dialogues)} 个对话片段")

    # 优化对话
    dialogues = optimize_dialogues(dialogues, replace_colons=not args.keep_colons)

    # 保存对话
    save_dialogues(dialogues, args.output)
    print(f"[OK] 对话已保存: {args.output}")

    # 预览前5条
    print("\n[预览] 前5条对话:")
    for i, d in enumerate(dialogues[:5], 1):
        print(f"  {i}. 【{d['role']}】{d['text'][:50]}...")

    print(f"\n[提示] 下一步，使用以下命令生成音频:")
    print(f"  python drama_to_audio.py {args.output} 输出音频.mp3")

if __name__ == '__main__':
    main()
