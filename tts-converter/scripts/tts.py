#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字转语音（TTS）转换工具
使用微软 Edge 浏览器的语音合成技术
"""

import edge_tts
import asyncio
import argparse
import sys
from pathlib import Path


# 默认中文女声
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"


async def text_to_speech(text, output_file, voice=DEFAULT_VOICE, rate=None, pitch=None, volume=None):
    """
    将文字转换为语音

    参数:
        text: 要转换的文本
        output_file: 输出文件路径
        voice: 语音名称
        rate: 语速调整（例如 '+0%', '+20%', '-10%'）
        pitch: 音调调整（例如 '+0Hz', '+10Hz', '-10Hz'）
        volume: 音量调整（例如 '+0%', '+10%', '-50%'）
    """
    try:
        # 构建参数
        params = {'text': text, 'voice': voice}

        # 只添加非默认值的参数
        if rate and rate != '+0%':
            params['rate'] = rate
        if pitch and pitch != '+0%':
            params['pitch'] = pitch
        if volume and volume != '+0%':
            params['volume'] = volume

        # 创建语音对象
        communicate = edge_tts.Communicate(**params)

        # 保存音频
        await communicate.save(output_file)

        print(f"[SUCCESS] 已生成: {output_file}")
        print(f"[INFO] 使用声音: {voice}")
        return True

    except Exception as e:
        print(f"[ERROR] 转换失败: {e}", file=sys.stderr)
        return False


def read_text_file(file_path):
    """读取文本文件"""
    try:
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'utf-16', 'latin-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        raise Exception("无法解码文件，请确保文件是 UTF-8 或 GBK 编码")

    except Exception as e:
        print(f"[ERROR] 读取文件失败: {e}", file=sys.stderr)
        return None


async def list_volumes(language_filter=None):
    """列出所有可用的语音"""
    try:
        voices = await edge_tts.list_voices()

        if language_filter:
            voices = [v for v in voices if v['Locale'].startswith(language_filter)]

        print(f"\n可用语音列表 (共 {len(voices)} 个):\n")

        # 按语言分组
        by_locale = {}
        for voice in voices:
            locale = voice['Locale']
            if locale not in by_locale:
                by_locale[locale] = []
            by_locale[locale].append(voice)

        # 显示语音
        for locale, locale_voices in sorted(by_locale.items()):
            print(f"\n{locale}:")

            for voice in locale_voices:
                name = voice['Name']
                gender = voice['Gender']
                description = voice.get('Description', '')

                # 标记推荐语音
                flag = " [推荐]" if "Neural" in name and locale.startswith("zh") else ""

                print(f"  - {name} ({gender}){flag}")
                if description:
                    print(f"    {description}")

        print("\n")

    except Exception as e:
        print(f"[ERROR] 获取语音列表失败: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description='文字转语音工具 - 使用微软 Edge 语音合成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s input.txt output.mp3
  %(prog)s input.txt output.mp3 --voice zh-CN-XiaoyiNeural
  %(prog)s input.txt output.mp3 --rate +20%
  %(prog)s --list-voices zh
  %(prog)s "你好世界" output.mp3
        '''
    )

    parser.add_argument('input', nargs='?', help='输入文件路径或文本内容')
    parser.add_argument('output', nargs='?', help='输出音频文件路径（支持 mp3/wav/ogg）')
    parser.add_argument('--voice', default=DEFAULT_VOICE,
                        help=f'语音名称（默认: {DEFAULT_VOICE}）')
    parser.add_argument('--rate', default=None,
                        help='语速调整（例如: +20%%, -10%%）')
    parser.add_argument('--pitch', default=None,
                        help='音调调整（例如: +10Hz, -10Hz）')
    parser.add_argument('--volume', default=None,
                        help='音量调整（例如: +10%%, -50%%）')
    parser.add_argument('--list-voices', metavar='LANG',
                        help='列出可用语音（可选语言过滤器，如: zh, en, all）')

    args = parser.parse_args()

    # 列出语音
    if args.list_voices is not None:
        language_filter = None if args.list_voices == 'all' else args.list_voices
        asyncio.run(list_volumes(language_filter))
        return 0

    # 检查必需参数
    if not args.input or not args.output:
        parser.print_help()
        return 1

    # 获取文本内容
    input_path = Path(args.input)

    if input_path.exists():
        # 从文件读取
        text = read_text_file(args.input)
        if text is None:
            return 1
    else:
        # 直接使用输入的文本
        text = args.input

    if not text.strip():
        print("[ERROR] 文本内容为空", file=sys.stderr)
        return 1

    # 执行转换
    print(f"[INFO] 正在转换文字为语音...")
    print(f"[INFO] 输入文本长度: {len(text)} 字符")

    success = asyncio.run(text_to_speech(
        text,
        args.output,
        args.voice,
        args.rate,
        args.pitch,
        args.volume
    ))

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
