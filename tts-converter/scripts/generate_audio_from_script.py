#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据广播剧文稿生成音频
第二步：读取修正后的文稿，生成多角色音频
"""

import re
import json
import edge_tts
import asyncio
from pathlib import Path
import sys


# 角色声音配置
CHARACTER_VOICES = {
    '艾米': 'zh-CN-XiaoxiaoNeural',
    '和也': 'zh-CN-YunxiNeural',
    '星月星空': 'zh-CN-XiaoyiNeural',
    '旁白': 'zh-CN-YunxiNeural',
    '我（旁白）': 'zh-CN-YunxiNeural',
    '星空': 'zh-CN-XiaoyiNeural',
}


def parse_markdown_script(script_file):
    """
    解析Markdown格式的广播剧文稿
    """
    with open(script_file, 'r', encoding='utf-8') as f:
        content = f.read()

    segments = []

    # 提取对话片段
    # 格式：### [序号] 第XX行 - **角色名**
    pattern = r'###\s*\[(\d+)\].*?\*\*(.+?)\*\*\s*\n\s*\*\*对话\*\*：([^\n]+)'

    matches = re.findall(pattern, content)

    for match in matches:
        index = int(match[0])
        speaker = match[1].strip()
        dialogue = match[2].strip()

        segments.append({
            'index': index,
            'speaker': speaker,
            'dialogue': dialogue
        })

    return segments


def parse_json_script(script_file):
    """
    解析JSON格式的广播剧文稿
    """
    with open(script_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    segments = []

    for i, seg in enumerate(data['segments'], 1):
        segments.append({
            'index': i,
            'speaker': seg['speaker'],
            'dialogue': seg['dialogue']
        })

    return segments


def get_voice_for_speaker(speaker):
    """获取角色的声音"""
    # 直接匹配
    if speaker in CHARACTER_VOICES:
        return CHARACTER_VOICES[speaker]

    # 模糊匹配
    for char_name, voice in CHARACTER_VOICES.items():
        if char_name in speaker or speaker in char_name:
            return voice

    # 默认：男主角声音
    return CHARACTER_VOICES['和也']


async def generate_audio_segments(segments, temp_dir):
    """
    生成所有音频片段
    """
    audio_files = []

    for i, seg in enumerate(segments):
        speaker = seg['speaker']
        dialogue = seg['dialogue']

        # 获取声音
        voice = get_voice_for_speaker(speaker)

        print(f"[{i+1}/{len(segments)}] {speaker}: {dialogue[:40]}...")

        # 生成音频
        temp_file = Path(temp_dir) / f"segment_{i:04d}.mp3"

        try:
            communicate = edge_tts.Communicate(dialogue, voice)
            await communicate.save(str(temp_file))
            audio_files.append(str(temp_file))
        except Exception as e:
            print(f"[ERROR] 片段 {i+1} 生成失败: {e}")

    return audio_files


def generate_ffmpeg_list(audio_files, list_file):
    """生成ffmpeg合并列表"""
    with open(list_file, 'w', encoding='utf-8') as f:
        for audio_file in audio_files:
            f.write(f"file '{Path(audio_file).absolute()}'\n")


async def main():
    if len(sys.argv) < 2:
        print("用法: python generate_audio_from_script.py <文稿文件>")
        print("\n支持的格式：")
        print("  - Markdown文稿 (*.md)")
        print("  - JSON文稿 (*.json)")
        print("\n示例：")
        print("  python generate_audio_from_script.py 科幻小说_广播剧文稿.md")
        print("  python generate_audio_from_script.py 科幻小说_广播剧文稿.json")
        sys.exit(1)

    script_file = sys.argv[1]
    script_path = Path(script_file)

    print(f"[INFO] 读取文稿: {script_file}")

    # 解析文稿
    if script_path.suffix == '.json':
        segments = parse_json_script(script_file)
    else:
        segments = parse_markdown_script(script_file)

    print(f"[INFO] 共 {len(segments)} 个对话片段")

    if not segments:
        print("[ERROR] 文稿中没有找到对话片段")
        sys.exit(1)

    # 显示统计信息
    speaker_counts = {}
    for seg in segments:
        speaker = seg['speaker']
        speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1

    print(f"\n[INFO] 角色统计：")
    for speaker, count in sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True):
        voice = get_voice_for_speaker(speaker)
        print(f"  {speaker}: {count}次 ({voice})")

    # 生成音频
    print(f"\n[INFO] 开始生成音频...")

    import tempfile
    temp_dir = tempfile.mkdtemp()

    audio_files = await generate_audio_segments(segments, temp_dir)

    print(f"\n[INFO] 成功生成 {len(audio_files)} 个音频片段")

    # 生成输出文件
    output_file = script_path.parent / (script_path.stem.replace('_广播剧文稿', '') + '_最终版.mp3')

    # 生成ffmpeg列表
    list_file = script_path.parent / (output_file.stem + '_file_list.txt')
    generate_ffmpeg_list(audio_files, list_file)

    print(f"\n[INFO] 音频片段列表: {list_file}")

    # 使用ffmpeg合并
    print(f"\n[INFO] 正在合并音频...")
    import subprocess

    try:
        result = subprocess.run([
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file),
            '-c', 'copy',
            str(output_file)
        ], capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print(f"[OK] 音频已生成: {output_file}")

            # 获取文件大小
            file_size = output_file.stat().st_size / (1024 * 1024)
            print(f"[INFO] 文件大小: {file_size:.1f} MB")
        else:
            print(f"[ERROR] 合并失败")
            print(result.stderr)

    except Exception as e:
        print(f"[ERROR] 合并失败: {e}")
        print(f"\n[INFO] 请手动合并：")
        print(f"ffmpeg -f concat -safe 0 -i {list_file} -c copy {output_file}")


if __name__ == '__main__':
    asyncio.run(main())
