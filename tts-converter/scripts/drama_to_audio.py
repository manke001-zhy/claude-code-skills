#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广播剧稿子转音频工具
简单直接：把稿子变成MP3
"""

import re
import edge_tts
import asyncio
import subprocess
from pathlib import Path
import sys
import tempfile


# 角色声音映射
VOICE_MAP = {
    # 男声
    '男主角': 'zh-CN-YunxiNeural',      # 云希 - 年轻男声
    '男1': 'zh-CN-YunxiNeural',          # 云希 - 年轻男声
    '男2': 'zh-CN-YunxiNeural',          # 云希 - 年轻男声
    '旁白': 'zh-CN-YunjianNeural',       # 云建 - 成熟男声（更有磁性）
    '我': 'zh-CN-YunxiNeural',           # 云希 - 年轻男声
    '和也': 'zh-CN-YunxiNeural',         # 云希 - 年轻男声（少年音）
    '阿基': 'zh-CN-YunzeNeural',         # 云泽 - 机器人男声

    # 女声
    '女主角': 'zh-CN-XiaoxiaoNeural',    # 晓晓 - 温柔女声
    '女1': 'zh-CN-XiaoxiaoNeural',        # 晓晓 - 温柔女声
    '女2': 'zh-CN-XiaoyiNeural',          # 晓伊 - 成熟女声
    '少女': 'zh-CN-XiaoxiaoNeural',       # 晓晓 - 少女音
    'AI': 'zh-CN-XiaoxiaoNeural',         # 晓晓 - AI女声
    '艾米': 'zh-CN-XiaoxiaoNeural',       # 晓晓 - 少女音（活泼AI）
    '星空': 'zh-CN-XiaoyiNeural',         # 晓伊 - 少女音（温柔）

    # 异世界骑士广播剧角色
    '莱昂': 'zh-CN-YunxiNeural',         # 云希 - 22岁骑士，年轻男声
    '汤姆': 'zh-CN-YunxiNeural',         # 云希 - 热血少年，年轻男声
    '艾莉丝': 'zh-CN-XiaoxiaoNeural',     # 晓晓 - 公主，温柔女声
    '魔王': 'zh-CN-YunjianNeural',       # 云建 - 魔王，成熟男声（疲惫）
    '国王': 'zh-CN-YunjianNeural',        # 云建 - 国王，成熟男声（女儿奴）
}


def clean_dialogue_text(text):
    """
    清理对话文本，去除引导词

    去除：我说、他想、她说、他说、他道等
    """
    # 去除开头的引导词（支持多种变体）
    text = re.sub(r'^(我说|他想|她说|他说|他道|她道|他问|她问|她喊|他喊|问道|问道：|答道：)\s*[,，]?\s*', '', text)
    return text


def parse_script(text):
    """
    解析广播剧稿子

    支持的格式：
    1. 角色名：对话内容
    2. 【角色名】对话内容
    3. 【角色名】\n对话内容（角色名和对话分行）
    4. ## 角色名（Markdown格式）
    """
    segments = []

    lines = text.strip().split('\n')

    current_speaker = None
    current_dialogue = []
    expect_dialogue = False  # 标记是否期待对话内容

    for line in lines:
        line = line.strip()

        if not line:
            # 空行，保存当前对话
            if current_speaker and current_dialogue:
                dialogue_text = ' '.join(current_dialogue).strip()
                if dialogue_text:
                    dialogue_text = clean_dialogue_text(dialogue_text)
                    segments.append({
                        'speaker': current_speaker,
                        'text': dialogue_text
                    })
                current_dialogue = []
                expect_dialogue = False
            continue

        # 格式1：角色名：对话内容
        match = re.match(r'^([^：:]+)[：:](.+)$', line)
        if match:
            # 保存之前的对话
            if current_speaker and current_dialogue:
                dialogue_text = ' '.join(current_dialogue).strip()
                if dialogue_text:
                    dialogue_text = clean_dialogue_text(dialogue_text)
                    segments.append({
                        'speaker': current_speaker,
                        'text': dialogue_text
                    })
                current_dialogue = []

            current_speaker = match.group(1).strip()
            current_dialogue.append(match.group(2).strip())
            expect_dialogue = False
            continue

        # 格式2：【角色名】对话内容（同行）
        match = re.match(r'^【(.+?)】(.+)$', line)
        if match:
            # 保存之前的对话
            if current_speaker and current_dialogue:
                dialogue_text = ' '.join(current_dialogue).strip()
                if dialogue_text:
                    dialogue_text = clean_dialogue_text(dialogue_text)
                    segments.append({
                        'speaker': current_speaker,
                        'text': dialogue_text
                    })
                current_dialogue = []

            current_speaker = match.group(1).strip()
            current_dialogue.append(match.group(2).strip())
            expect_dialogue = False
            continue

        # 格式3：【角色名】单独一行（期待对话）
        match = re.match(r'^【(.+?)】$', line)
        if match:
            # 保存之前的对话
            if current_speaker and current_dialogue:
                dialogue_text = ' '.join(current_dialogue).strip()
                if dialogue_text:
                    dialogue_text = clean_dialogue_text(dialogue_text)
                    segments.append({
                        'speaker': current_speaker,
                        'text': dialogue_text
                    })
                current_dialogue = []

            current_speaker = match.group(1).strip()
            expect_dialogue = True
            continue

        # 格式3：## 角色名（Markdown标题）
        match = re.match(r'^#+\s*(.+)$', line)
        if match:
            # 保存之前的对话
            if current_speaker and current_dialogue:
                dialogue_text = ' '.join(current_dialogue).strip()
                if dialogue_text:
                    dialogue_text = clean_dialogue_text(dialogue_text)
                    segments.append({
                        'speaker': current_speaker,
                        'text': dialogue_text
                    })
                current_dialogue = []

            current_speaker = match.group(1).strip()
            continue

        # 普通文本，作为对话内容
        if current_speaker:
            current_dialogue.append(line)

    # 保存最后的对话
    if current_speaker and current_dialogue:
        dialogue_text = ' '.join(current_dialogue).strip()
        if dialogue_text:
            dialogue_text = clean_dialogue_text(dialogue_text)
            segments.append({
                'speaker': current_speaker,
                'text': dialogue_text
            })

    return segments


def get_voice(speaker):
    """获取角色的声音"""
    # 直接匹配
    if speaker in VOICE_MAP:
        return VOICE_MAP[speaker]

    # 模糊匹配
    for key, voice in VOICE_MAP.items():
        if key in speaker or speaker in key:
            return voice

    # 默认：男主角声音
    return VOICE_MAP['男主角']


async def generate_audio(segments, output_file):
    """生成音频"""
    temp_dir = tempfile.mkdtemp()
    audio_files = []

    print(f"\n[INFO] 共 {len(segments)} 个片段\n")

    for i, seg in enumerate(segments, 1):
        speaker = seg['speaker']
        text = seg['text']
        voice = get_voice(speaker)

        print(f"[{i}/{len(segments)}] {speaker}: {text[:30]}...")

        # 生成音频
        temp_file = Path(temp_dir) / f"segment_{i:04d}.mp3"

        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(temp_file))
            audio_files.append(str(temp_file))
        except Exception as e:
            print(f"  [ERROR] 生成失败: {e}")

    # 合并音频
    if audio_files:
        print(f"\n[INFO] 成功生成 {len(audio_files)} 个片段")
        print(f"[INFO] 正在合并音频...")

        list_file = Path(temp_dir) / "file_list.txt"
        with open(list_file, 'w', encoding='utf-8') as f:
            for audio_file in audio_files:
                f.write(f"file '{audio_file}'\n")

        # 使用ffmpeg合并
        try:
            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(list_file),
                '-c', 'copy',
                str(output_file)
            ], check=True, capture_output=True)

            print(f"[OK] 音频已生成: {output_file}")

            # 显示文件大小
            size_mb = Path(output_file).stat().st_size / (1024 * 1024)
            print(f"[INFO] 文件大小: {size_mb:.1f} MB")

            return True

        except Exception as e:
            print(f"[ERROR] 合并失败: {e}")
            print(f"[INFO] 音频片段保存在: {temp_dir}")
            return False
    else:
        print("[ERROR] 没有成功生成任何音频片段")
        return False


def main():
    if len(sys.argv) < 3:
        print("用法: python drama_to_audio.py <稿子文件> <输出MP3>")
        print("\n稿子格式示例：")
        print("""
男主角：你好，世界。
女主角：你好！
旁白：他们相遇了。
        """)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"[INFO] 读取稿子: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # 解析稿子
    segments = parse_script(text)

    if not segments:
        print("[ERROR] 稿子中没有识别到对话内容")
        print("[INFO] 请检查稿子格式是否正确")
        sys.exit(1)

    print(f"[INFO] 识别到 {len(segments)} 个对话片段")

    # 显示前几个片段
    print("\n[预览] 前3个片段：")
    for seg in segments[:3]:
        voice = get_voice(seg['speaker'])
        print(f"  {seg['speaker']} ({voice}): {seg['text'][:40]}...")

    # 生成音频
    asyncio.run(generate_audio(segments, output_file))


if __name__ == '__main__':
    main()
