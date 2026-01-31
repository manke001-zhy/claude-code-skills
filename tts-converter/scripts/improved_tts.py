#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进版多角色TTS工具
使用更智能的上下文分析
"""

import re
import json
import edge_tts
import asyncio
from pathlib import Path
from collections import defaultdict


# 角色特征词汇
CHARACTER_KEYWORDS = {
    '艾米': {
        'keywords': ['根据', '数据显示', '大数据', '算法', '分析', '检测', '建议', '统计', '概率', '幸福指数', '智商'],
        'name_variations': ['艾米', 'AI管家', '她'],
    },
    '和也': {
        'keywords': ['完蛋', '什么鬼', '闭嘴', '能不能', '为什么', '帮忙', '论文'],
        'name_variations': ['和也', '佐藤和也', '我'],
    },
    '星月星空': {
        'keywords': ['意识上传', '永生', '物理学', '转校生'],
        'name_variations': ['星空', '星月星空', '她'],
    }
}


def extract_dialogues_with_context(text):
    """
    提取对话，使用改进的上下文分析
    """
    lines = text.split('\n')
    dialogues = []

    for i, line in enumerate(lines, 1):
        # 查找对话
        pattern = r'[「『]([^「」『』]+)[」』]'
        matches = re.finditer(pattern, line)

        for match in matches:
            dialogue_text = match.group(1)

            # 多策略识别说话人
            speaker = identify_speaker(text, i, dialogue_text, lines)

            dialogues.append({
                'line_number': i,
                'speaker': speaker,
                'dialogue': dialogue_text,
                'full_line': line.strip()
            })

    return dialogues


def identify_speaker(text, line_num, dialogue_text, lines):
    """
    使用多策略识别说话人
    """

    # 策略1: 检查对话内容特征
    content_based_speaker = identify_by_content(dialogue_text)
    if content_based_speaker:
        return content_based_speaker

    # 策略2: 检查同一行的说话人标识
    speaker = identify_by_same_line(lines[line_num - 1], dialogue_text)
    if speaker:
        return speaker

    # 策略3: 检查前后5行的上下文
    speaker = identify_by_context(lines, line_num)
    if speaker:
        return speaker

    # 默认：旁白
    return '我（旁白）'


def identify_by_content(dialogue_text):
    """
    根据对话内容识别说话人
    """
    scores = {}

    for char_name, char_info in CHARACTER_KEYWORDS.items():
        score = 0
        for keyword in char_info['keywords']:
            if keyword in dialogue_text:
                score += 1
        scores[char_name] = score

    # 如果有明显的匹配（score >= 2）
    max_score = max(scores.values())
    if max_score >= 2:
        return max(scores, key=scores.get)

    return None


def identify_by_same_line(line, dialogue_text):
    """
    检查同一行的说话人标识
    """
    # 对话前
    before = line[:line.find(dialogue_text)]
    speaker_match_before = re.search(r'(\w{2,4})(说|道|问|喊|笑道|解释|回答|嘟囔|摊摊手|平静地)', before)
    if speaker_match_before:
        name = speaker_match_before.group(1)
        if name == '我':
            return '我（旁白）'
        return normalize_character_name(name)

    # 对话后
    after = line[line.find(dialogue_text) + len(dialogue_text):]
    speaker_match_after = re.search(r'(\w{2,4})(说|道|问|喊|笑道|解释|回答)', after)
    if speaker_match_after:
        name = speaker_match_after.group(1)
        if name == '我':
            return '我（旁白）'
        return normalize_character_name(name)

    return None


def identify_by_context(lines, line_num):
    """
    检查前后几行的上下文
    """
    # 查看前后5行
    start = max(0, line_num - 6)
    end = min(len(lines), line_num + 5)

    character_mentions = defaultdict(int)

    for i in range(start, end):
        if i == line_num - 1:  # 跳过对话所在行
            continue

        line = lines[i]

        # 查找角色名提及
        for char_name, char_info in CHARACTER_KEYWORDS.items():
            for variation in char_info['name_variations']:
                if variation in line:
                    # 如果在同一句或前一句，权重更高
                    weight = 3 if i >= line_num - 2 else 1
                    character_mentions[char_name] += weight

    # 返回提及最多的角色
    if character_mentions:
        max_char = max(character_mentions, key=character_mentions.get)
        if character_mentions[max_char] >= 2:
            return max_char

    return None


def normalize_character_name(name):
    """
    标准化角色名
    """
    # 如果是名字的变体，统一为标准名
    if '和也' in name:
        return '和也'
    elif '星空' in name:
        return '星月星空'
    elif name == '艾米':
        return '艾米'
    elif name == '我':
        return '我（旁白）'
    else:
        return name


def split_text_segments(text, dialogues):
    """
    分割文本为音频片段
    """
    segments = []

    # 简单实现：每段对话作为一个片段
    for dlg in dialogues:
        segments.append({
            'speaker': dlg['speaker'],
            'text': dlg['dialogue']
        })

    return segments


async def generate_audio(text, output_file, characters):
    """生成音频"""
    dialogues = extract_dialogues_with_context(text)
    segments = split_text_segments(text, dialogues)

    print(f"[INFO] 识别到 {len(segments)} 个音频片段")

    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp()

    audio_files = []

    for i, seg in enumerate(segments):
        speaker = seg['speaker']
        text = seg['text']

        # 获取声音
        voice_data = characters.get(speaker)
        if not voice_data:
            # 尝试查找匹配的角色
            for char_name, char_data in characters.items():
                if speaker in char_name or char_name in speaker:
                    voice_data = char_data
                    break

        if not voice_data:
            voice_data = characters['我（旁白）']

        voice = voice_data['voice']

        print(f"[{i+1}/{len(segments)}] {speaker}: {text[:30]}...")

        # 生成音频
        temp_file = Path(temp_dir) / f"segment_{i:04d}.mp3"

        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(temp_file))
            audio_files.append(str(temp_file))
        except Exception as e:
            print(f"[ERROR] 片段 {i+1} 生成失败: {e}")

    print(f"\n[INFO] 成功生成 {len(audio_files)} 个片段")

    # 生成合并列表文件
    list_file = Path(output_file).parent / (Path(output_file).stem + '_file_list.txt')
    with open(list_file, 'w', encoding='utf-8') as f:
        for audio_file in audio_files:
            f.write(f"file '{Path(audio_file).absolute()}'\n")

    print(f"[INFO] 音频片段列表: {list_file}")
    print(f"[INFO] 使用 ffmpeg 合并：")
    print(f"ffmpeg -f concat -safe 0 -i {list_file} -c copy {output_file}")

    return True


def main():
    import sys

    if len(sys.argv) < 4:
        print("用法: python improved_tts.py <小说文件> <输出文件> <配置文件>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    config_file = sys.argv[3]

    print(f"[INFO] 读取文件: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"[INFO] 加载配置: {config_file}")
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    characters = config['characters']

    # 生成音频
    asyncio.run(generate_audio(text, output_file, characters))


if __name__ == '__main__':
    main()
