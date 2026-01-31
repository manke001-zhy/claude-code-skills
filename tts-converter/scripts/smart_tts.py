#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能多角色文字转语音工具
自动识别角色、判断性别、分配声音、合成音频
"""

import re
import json
import edge_tts
import asyncio
import argparse
import sys
from pathlib import Path
from collections import defaultdict


# 性别对应的声音
VOICE_MAP = {
    '男': {
        '年轻': 'zh-CN-YunxiNeural',  # 云希
        '成熟': 'zh-CN-YunjianNeural',  # 云建
        '中年': 'zh-CN-YunyangNeural',  # 云扬
    },
    '女': {
        '温柔': 'zh-CN-XiaoxiaoNeural',  # 晓晓（默认）
        '活泼': 'zh-CN-XiaomengNeural',  # 晓梦
        '成熟': 'zh-CN-XiaoyiNeural',  # 晓伊
    },
    '旁白': 'zh-CN-XiaoxiaoNeural',  # 晓晓（默认旁白）
    '主角': 'zh-CN-YunxiNeural',  # 云希（默认主角男声）
}


class Character:
    """角色信息"""

    def __init__(self, name, gender='未知', age='年轻', voice=None):
        self.name = name
        self.gender = gender  # 男/女/未知
        self.age = age  # 年轻/成熟/中年
        self.voice = voice

    def get_voice(self):
        """获取分配的声音"""
        if self.voice:
            return self.voice

        if self.gender == '男':
            return VOICE_MAP['男'].get(self.age, VOICE_MAP['男']['年轻'])
        elif self.gender == '女':
            return VOICE_MAP['女'].get(self.age, VOICE_MAP['女']['温柔'])
        else:
            return VOICE_MAP['旁白']

    def to_dict(self):
        return {
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'voice': self.get_voice()
        }


def analyze_characters(text):
    """
    分析文本中的角色

    返回: (角色字典, 对话片段列表)
    """
    characters = {}
    dialogue_segments = []

    # 提取对话（「」或『』）
    dialogue_pattern = r'[「『]([^「」『』]+)[」』]'

    # 统计对话前的说话人
    context_lines = text.split('\n')
    for i, line in enumerate(context_lines):
        # 查找对话
        dialogues = re.findall(dialogue_pattern, line)
        if not dialogues:
            continue

        # 查找对话前的说话人（如："艾米说"）
        speaker_pattern = r'(\w{2,4})(说|道|问|喊|笑道|摊摊手|平静地|回答|解释|补充|嘟囔)'
        speaker_match = re.search(speaker_pattern, line)

        if speaker_match:
            speaker = speaker_match.group(1)
            # 过滤掉非角色词汇
            if speaker not in ['这个', '那个', '什么', '怎么', '因为', '所以', '但是', '不过', '而且', '然后', '接着', '最后']:
                for dialogue in dialogues:
                    dialogue_segments.append({
                        'speaker': speaker,
                        'text': dialogue,
                        'line_number': i + 1
                    })
        else:
            # 没有明确的说话人，尝试从上下文推断
            # 查看前几行
            prev_lines = context_lines[max(0, i-3):i]
            for prev_line in reversed(prev_lines):
                speaker_match = re.search(speaker_pattern, prev_line)
                if speaker_match:
                    speaker = speaker_match.group(1)
                    if speaker not in ['这个', '那个', '什么', '怎么', '因为', '所以', '但是', '不过', '而且', '然后', '接着', '最后']:
                        for dialogue in dialogues:
                            dialogue_segments.append({
                                'speaker': speaker,
                                'text': dialogue,
                                'line_number': i + 1
                            })
                        break
            else:
                # 无法判断说话人，标记为"未知"
                for dialogue in dialogues:
                    dialogue_segments.append({
                        'speaker': '未知',
                        'text': dialogue,
                        'line_number': i + 1
                    })

    # 统计每个角色的对话次数
    character_counts = defaultdict(int)
    for seg in dialogue_segments:
        character_counts[seg['speaker']] += 1

    # 只保留对话次数>=2的角色，避免误识别
    for name, count in sorted(character_counts.items(), key=lambda x: x[1], reverse=True):
        if count >= 2 and name != '我' and name != '未知':
            character = Character(name)
            characters[name] = character

    return characters, dialogue_segments


def guess_gender_from_text(text, character_name):
    """
    从文本中推断角色性别

    返回: (性别, 年龄)
    """
    # 常见的女性特征词
    female_keywords = ['她', '姐姐', '妹妹', '少女', '女', '小姐', '妈', '娘', '女孩', '女王']
    # 常见的男性特征词
    male_keywords = ['他', '哥哥', '弟弟', '少年', '男', '先生', '爸', '爹', '男孩', '国王', '学长']

    # 统计特征词出现次数
    female_count = 0
    male_count = 0

    for keyword in female_keywords:
        female_count += text.count(keyword)

    for keyword in male_keywords:
        male_count += text.count(keyword)

    # 判断性别
    if female_count > male_count:
        return '女', '年轻'
    elif male_count > female_count:
        return '男', '年轻'
    else:
        return '未知', '年轻'


def analyze_and_assign_voices(text):
    """
    分析文本并自动分配声音

    返回: (角色字典, 旁白声音, 对话片段列表)
    """
    print("[INFO] 正在分析文本...\n")

    # 分析角色
    characters, dialogue_segments = analyze_characters(text)

    # 判断主角性别
    protagonist_gender = '男'
    protagonist_age = '年轻'

    # 检查"我"的性别
    if '我' in text:
        # 统计"我"后面的代词
        pattern = r'我(?:.{0,20})([他她])'
        matches = re.findall(pattern, text)
        if matches:
            female = matches.count('她')
            male = matches.count('他')
            if female > male:
                protagonist_gender = '女'

    # 添加主角
    protagonist = Character('我（旁白）', protagonist_gender, protagonist_age)
    protagonist.voice = VOICE_MAP['主角'] if protagonist_gender == '男' else VOICE_MAP['女']['温柔']
    characters['我（旁白）'] = protagonist

    # 为每个角色推断性别
    for name, char in characters.items():
        if name == '我（旁白）':
            continue

        gender, age = guess_gender_from_text(text, name)
        char.gender = gender
        char.age = age

    return characters, dialogue_segments


def display_character_analysis(characters):
    """显示角色分析结果"""
    print("=" * 60)
    print("角色分析结果")
    print("=" * 60)

    for name, char in characters.items():
        print(f"\n角色: {name}")
        print(f"  性别: {char.gender}")
        print(f"  年龄: {char.age}")
        print(f"  声音: {char.get_voice()}")

    print("\n" + "=" * 60)


def save_character_config(characters, output_file):
    """保存角色配置到文件"""
    config = {
        'characters': {name: char.to_dict() for name, char in characters.items()}
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\n[INFO] 角色配置已保存到: {output_file}")


def load_character_config(config_file):
    """从文件加载角色配置"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    characters = {}
    for name, data in config['characters'].items():
        char = Character(name, data['gender'], data['age'], data['voice'])
        characters[name] = char

    return characters


def split_text_by_speaker(text, characters):
    """
    根据说话人分割文本

    返回: [(说话人, 文本片段), ...]
    """
    segments = []

    lines = text.split('\n')
    current_speaker = '我（旁白）'
    current_text = []

    for line in lines:
        # 检查是否是对话
        dialogue_pattern = r'[「『]([^「」『』]+)[」』]'
        dialogues = re.findall(dialogue_pattern, line)

        if dialogues:
            # 保存之前的旁白
            if current_text:
                text = '\n'.join(current_text).strip()
                if text:
                    segments.append((current_speaker, text))
                current_text = []

            # 查找说话人
            speaker_pattern = r'(\w+)(说|道|问|喊|笑道|摊摊手|平静地|回答)'
            speaker_match = re.search(speaker_pattern, line)

            if speaker_match:
                speaker = speaker_match.group(1)
                # 如果是"我"，使用旁白
                if speaker == '我':
                    current_speaker = '我（旁白）'
                else:
                    # 查找对应的角色
                    found = False
                    for char_name in characters.keys():
                        if char_name in speaker or speaker in char_name:
                            current_speaker = char_name
                            found = True
                            break

                    if not found:
                        # 使用原说话人
                        current_speaker = speaker
            else:
                # 没有明确的说话人，保持当前说话人
                pass

            # 添加对话
            for dialogue in dialogues:
                segments.append((current_speaker, dialogue))

            # 添加对话后的描述
            remaining = re.sub(dialogue_pattern, '', line).strip()
            if remaining:
                current_text.append(remaining)
                current_speaker = '我（旁白）'
        else:
            # 不是对话，作为旁白
            current_text.append(line)
            current_speaker = '我（旁白）'

    # 保存剩余文本
    if current_text:
        text = '\n'.join(current_text).strip()
        if text:
            segments.append(('我（旁白）', text))

    return segments


async def text_to_speech(text, output_file, voice):
    """将文字转换为语音"""
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return True
    except Exception as e:
        print(f"[ERROR] 转换失败: {e}", file=sys.stderr)
        return False


async def merge_audio_files(audio_files, output_file):
    """
    合并多个音频文件

    注意：这里使用简单的方式，实际应该用 pydub 或其他库
    """
    try:
        from pydub import AudioSegment

        combined = AudioSegment.empty()

        for audio_file in audio_files:
            audio = AudioSegment.from_mp3(audio_file)
            combined += audio

        combined.export(output_file, format='mp3')
        return True

    except ImportError:
        print("[WARN] 未安装 pydub，无法自动合并音频文件")
        print("[INFO] 请手动合并以下文件：")
        for i, f in enumerate(audio_files, 1):
            print(f"  {i}. {f}")

        # 创建一个合并列表文件
        list_file = output_file.replace('.mp3', '_file_list.txt')
        with open(list_file, 'w', encoding='utf-8') as f:
            for audio_file in audio_files:
                f.write(f"file '{Path(audio_file).absolute()}'\n")

        print(f"\n[INFO] 可以使用 ffmpeg 合并：")
        print(f"ffmpeg -f concat -safe 0 -i {list_file} -c copy {output_file}")
        return False

    except Exception as e:
        print(f"[ERROR] 合并失败: {e}", file=sys.stderr)
        return False


async def generate_multi_voice_audio(text, output_file, characters):
    """生成多角色音频"""
    print(f"\n[INFO] 开始生成多角色音频...")

    # 分割文本
    segments = split_text_by_speaker(text, characters)

    print(f"[INFO] 共分割成 {len(segments)} 个片段")

    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp()

    # 生成每个片段的音频
    audio_files = []
    for i, (speaker, text) in enumerate(segments):
        if not text.strip():
            continue

        # 获取声音
        voice = characters.get(speaker)
        if not voice:
            voice = characters['我（旁白）']

        # 生成临时文件
        temp_file = Path(temp_dir) / f"segment_{i:04d}.mp3"

        print(f"[{i+1}/{len(segments)}] {speaker}: {text[:30]}...")

        success = await text_to_speech(text, str(temp_file), voice.get_voice())

        if success:
            audio_files.append(str(temp_file))

    print(f"\n[INFO] 成功生成 {len(audio_files)} 个音频片段")

    # 合并音频
    print(f"[INFO] 正在合并音频...")
    success = await merge_audio_files(audio_files, output_file)

    if success:
        print(f"[SUCCESS] 已生成: {output_file}")
    else:
        print(f"[INFO] 音频片段保存在: {temp_dir}")

    return success


async def main():
    parser = argparse.ArgumentParser(
        description='智能多角色文字转语音工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('input', help='输入文件路径')
    parser.add_argument('output', help='输出音频文件路径')
    parser.add_argument('--config', help='角色配置文件（JSON）')
    parser.add_argument('--auto-merge', action='store_true',
                        help='自动合并音频片段（需要安装 pydub）')

    args = parser.parse_args()

    # 读取文本
    print(f"[INFO] 读取文件: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"[INFO] 文本长度: {len(text)} 字符\n")

    # 加载或分析角色
    if args.config and Path(args.config).exists():
        print(f"[INFO] 加载角色配置: {args.config}")
        characters = load_character_config(args.config)
    else:
        # 自动分析
        characters, _ = analyze_and_assign_voices(text)

        # 显示分析结果
        display_character_analysis(characters)

        # 保存配置
        config_file = Path(args.input).stem + '_角色配置.json'
        save_character_config(characters, config_file)

        print("\n" + "=" * 60)
        print("请检查并修改角色配置文件后重新运行")
        print(f"配置文件: {config_file}")
        print("\n修改后使用: python smart_tts.py {input} {output} --config {config}")
        print("=" * 60)

        if not args.config:
            # 第一次运行，只生成配置
            return 0

    # 生成音频
    if args.auto_merge:
        try:
            import pydub
            success = await generate_multi_voice_audio(text, args.output, characters)
        except ImportError:
            print("[ERROR] 需要安装 pydub: pip install pydub")
            return 1
    else:
        # 不自动合并，只生成片段
        success = await generate_multi_voice_audio(text, args.output, characters)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
