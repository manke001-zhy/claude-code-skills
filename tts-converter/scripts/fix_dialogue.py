#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话角色修正工具
显示每段对话及其识别的说话人，允许手动修正
"""

import re
import json
from pathlib import Path
import sys


def extract_dialogues_with_speakers(text):
    """
    提取所有对话及其识别的说话人
    """
    lines = text.split('\n')
    dialogues = []

    # 当前说话人（默认是主角/旁白）
    current_speaker = '我（旁白）'

    for i, line in enumerate(lines, 1):
        # 查找对话
        pattern = r'[「『]([^「」『』]+)[」』]'
        matches = re.finditer(pattern, line)

        for match in matches:
            dialogue_text = match.group(1)
            full_line = line

            # 尝试识别说话人
            speaker = None

            # 策略1: 同一行中的"XX说"
            before = full_line[:full_line.find(dialogue_text)]
            after = full_line[full_line.find(dialogue_text) + len(dialogue_text):]

            # 检查对话前
            speaker_match_before = re.search(r'(\w{2,4})(说|道|问|喊|笑道|解释|回答|嘟囔|摊摊手|平静地)', before)
            if speaker_match_before:
                speaker = speaker_match_before.group(1)

            # 检查对话后
            if not speaker:
                speaker_match_after = re.search(r'(\w{2,4})(说|道|问|喊|笑道|解释|回答)', after)
                if speaker_match_after:
                    speaker = speaker_match_after.group(1)

            # 策略2: 如果没找到，查看前几行
            if not speaker:
                for j in range(max(0, i-3), i):
                    context_line = lines[j]
                    speaker_match = re.search(r'(\w{2,4})(说|道|问|喊|笑道|解释|回答)', context_line)
                    if speaker_match:
                        speaker = speaker_match.group(1)
                        break

            # 如果还是没找到，使用当前说话人
            if not speaker:
                speaker = current_speaker

            # 特殊处理：如果是"我"，标记为旁白
            if speaker == '我':
                speaker = '我（旁白）'

            dialogues.append({
                'line_number': i,
                'speaker': speaker,
                'dialogue': dialogue_text,
                'full_line': full_line.strip()
            })

            # 如果有明确的说话人，更新当前说话人
            if speaker and speaker != '我（旁白）':
                current_speaker = speaker

    return dialogues


def load_character_config(config_file):
    """加载角色配置"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    characters = {}
    for name, data in config['characters'].items():
        characters[name] = data

    return characters


def main():
    if len(sys.argv) < 3:
        print("用法: python fix_dialogue.py <小说文件> <配置文件>")
        sys.exit(1)

    input_file = sys.argv[1]
    config_file = sys.argv[2]

    print(f"[INFO] 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"[INFO] 加载配置: {config_file}")
    characters = load_character_config(config_file)

    # 提取对话
    dialogues = extract_dialogues_with_speakers(text)

    print(f"\n[INFO] 共找到 {len(dialogues)} 段对话\n")

    # 显示对话和识别的说话人
    print("=" * 80)
    print("对话识别结果（前30段）")
    print("=" * 80)

    for i, dlg in enumerate(dialogues[:30], 1):
        print(f"\n[{i}] 第{dlg['line_number']}行")
        print(f"    识别为: {dlg['speaker']}")
        print(f"    对话: {dlg['dialogue']}")
        print(f"    原文: {dlg['full_line'][:80]}...")

    print("\n" + "=" * 80)

    # 统计每个角色的对话数量
    speaker_counts = {}
    for dlg in dialogues:
        speaker = dlg['speaker']
        speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1

    print("\n角色对话统计：")
    for speaker, count in sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {speaker}: {count}次")

    # 生成修正建议
    print("\n" + "=" * 80)
    print("修正建议")
    print("=" * 80)

    suggestions = []

    # 检查常见的误识别
    for dlg in dialogues:
        # 如果识别为"和也"但对话内容明显像艾米说的
        if dlg['speaker'] in ['和也', '佐藤和也', '我（旁白）']:
            # 检查对话内容中是否包含艾米特有的词汇
            ami_keywords = ['根据', '数据显示', '大数据', '算法', '检测', '建议', '分析']
            if any(kw in dlg['dialogue'] for kw in ami_keywords):
                suggestions.append({
                    'line': dlg['line_number'],
                    'current': dlg['speaker'],
                    'suggested': '艾米',
                    'dialogue': dlg['dialogue']
                })

    if suggestions:
        print(f"\n发现 {len(suggestions)} 处可能的误识别：\n")
        for i, sug in enumerate(suggestions[:10], 1):
            print(f"{i}. 第{sug['line']}行")
            print(f"   当前: {sug['current']}")
            print(f"   建议: {sug['suggested']}")
            print(f"   对话: {sug['dialogue']}")
            print()

    # 生成修正后的配置
    print("=" * 80)
    print("[OK] 分析完成！")
    print("=" * 80)

    print("\n下一步：")
    print("1. 查看上面的识别结果")
    print("2. 如果需要修正，我可以为你创建一个交互式修正工具")
    print("3. 或者告诉我具体的修正规则，我会改进算法")


if __name__ == '__main__':
    main()
