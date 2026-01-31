#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能角色识别工具 v2
使用上下文分析和规则匹配
"""

import re
import json
from collections import defaultdict
from pathlib import Path


def extract_names_and_dialogues(text):
    """
    提取角色名和对话

    策略：
    1. 提取所有对话（「」）
    2. 查找对话前后的角色名
    3. 使用上下文推断说话人
    """
    lines = text.split('\n')

    # 对话列表：{(对话内容, 行号): [可能的说话人]}
    dialogues = defaultdict(list)

    # 常见的非角色名
    exclude_words = {
        '这个', '那个', '什么', '怎么', '因为', '所以', '但是', '不过',
        '而且', '然后', '接着', '最后', '另外', '此外', '感觉', '觉得',
        '发现', '看到', '听到', '知道', '明白', '理解', '开始', '结束',
        '继续', '停止', '时候', '地方', '东西', '事情', '问题', '办法',
    }

    # 第一步：提取所有对话
    for i, line in enumerate(lines):
        pattern = r'[「『]([^「」『』]+)[」』]'
        matches = re.finditer(pattern, line)

        for match in matches:
            dialogue_text = match.group(1)
            dialogues[(dialogue_text, i + 1)] = []

    # 第二步：为每个对话查找可能的说话人
    for (dialogue_text, line_num), speakers in dialogues.items():
        line_idx = line_num - 1
        line = lines[line_idx]

        # 策略1: 同一行中的"名字+动词"模式（在对话前）
        # 例如："艾米说：「...」"
        before_dialogue = line[:line.find(dialogue_text)]
        speaker_pattern = r'(\w{2,4})(说|道|问|喊|笑道|解释|补充|回答|嘟囔|摊摊手|平静地)'
        matches = re.findall(speaker_pattern, before_dialogue)
        for match in matches:
            name = match[0]
            if name not in exclude_words:
                speakers.append((name, '同前'))

        # 策略2: 同一行中的"名字+动词"模式（在对话后）
        # 例如：「...」艾米说
        after_dialogue = line[line.find(dialogue_text) + len(dialogue_text):]
        matches = re.findall(speaker_pattern, after_dialogue)
        for match in matches:
            name = match[0]
            if name not in exclude_words:
                speakers.append((name, '同后'))

        # 策略3: 查找下一行或前后几行中的名字
        # 查找范围：前后3行
        start_idx = max(0, line_idx - 2)
        end_idx = min(len(lines), line_idx + 4)

        for idx in range(start_idx, end_idx):
            if idx == line_idx:
                continue

            context_line = lines[idx]

            # 查找这一行中的名字
            # 2-4个字符的中文名
            name_pattern = r'([艾米星空和也佐藤星月]{2,4})'
            matches = re.findall(name_pattern, context_line)

            for name in matches:
                if name not in exclude_words and len(name) >= 2:
                    # 根据位置判断权重
                    if idx < line_idx:
                        speakers.append((name, '前行'))
                    elif idx == line_idx + 1:
                        speakers.append((name, '后行'))
                    else:
                        speakers.append((name, '后行'))

        # 策略4: 查找代词和名字的组合
        # 前后几行中查找"她说"、"艾米说"等
        for idx in range(start_idx, end_idx):
            if idx == line_idx:
                continue

            context_line = lines[idx]

            # "代词/名字 + 说/道/问"
            speaker_pattern = r'([他她它]\w{0,2}|艾米|星空|和也|佐藤|星月)(说|道|问|喊|笑道|解释|回答)'
            matches = re.findall(speaker_pattern, context_line)

            for match in matches:
                name = match[0]
                if name in ['他', '她']:
                    # 代词，暂时跳过
                    continue
                if name not in exclude_words:
                    speakers.append((name, '上下文'))

    # 第三步：统计每个名字的出现次数和权重
    name_stats = defaultdict(lambda: {'count': 0, 'sources': set()})

    for (dialogue_text, line_num), speakers in dialogues.items():
        for name, source in speakers:
            name_stats[name]['count'] += 1
            name_stats[name]['sources'].add(source)

    # 第四步：过滤出真正的角色（出现次数>=2且来自不同来源）
    characters = {}

    for name, stats in sorted(name_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        if stats['count'] >= 2 and len(stats['sources']) >= 1:
            if len(name) >= 2:  # 名字至少2个字
                characters[name] = stats

    return characters, dialogues


def infer_gender(text, character_name):
    """推断角色性别"""
    # 查找名字周围的代词
    patterns = [
        rf'{character_name}{{0,50}}([他她])',
        rf'([他她]){{0,50}}{character_name}',
    ]

    female = 0
    male = 0

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            if '她' in m:
                female += 1
            elif '他' in m:
                male += 1

    if female > male:
        return '女'
    elif male > female:
        return '男'
    else:
        return '未知'


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python analyze_smart.py <小说文件路径>")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"[INFO] 读取文件: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"[INFO] 文本长度: {len(text)} 字符\n")

    # 提取角色
    characters, dialogues = extract_names_and_dialogues(text)

    print("=" * 60)
    print("角色识别结果")
    print("=" * 60)

    # 创建角色配置
    char_configs = {}

    for name, stats in sorted(characters.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
        gender = infer_gender(text, name)

        char_configs[name] = {
            'name': name,
            'dialogue_count': stats['count'],
            'sources': list(stats['sources']),
            'gender': gender
        }

        print(f"\n角色: {name}")
        print(f"  对话次数: {stats['count']}")
        print(f"  推断性别: {gender}")
        print(f"  来源: {', '.join(stats['sources'])}")

    # 添加主角（我）
    protagonist_gender = '男'
    if text.count('她') > text.count('他'):
        protagonist_gender = '女'

    char_configs['我（旁白）'] = {
        'name': '我（旁白）',
        'dialogue_count': 0,
        'sources': ['主角'],
        'gender': protagonist_gender
    }

    print(f"\n角色: 我（旁白）[主角]")
    print(f"  性别: {protagonist_gender}")

    # 保存配置
    input_path = Path(input_file)
    output_file = str(input_path.parent / (input_path.stem + '_角色配置_智能版.json'))

    # 转换为TTS格式
    tts_config = {
        'characters': {}
    }

    voice_map = {
        '男': 'zh-CN-YunxiNeural',  # 云希
        '女': 'zh-CN-XiaoxiaoNeural',  # 晓晓
        '未知': 'zh-CN-XiaoxiaoNeural'
    }

    for name, char in char_configs.items():
        tts_config['characters'][name] = {
            'name': name,
            'gender': char['gender'],
            'age': '年轻',
            'voice': voice_map.get(char['gender'], 'zh-CN-XiaoxiaoNeural')
        }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tts_config, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"[OK] 配置已保存: {output_file}")
    print("=" * 60)

    print("\n[INFO] 下一步：")
    print("1. 检查并修改配置文件")
    print("2. 运行多角色TTS转换")


if __name__ == '__main__':
    main()
