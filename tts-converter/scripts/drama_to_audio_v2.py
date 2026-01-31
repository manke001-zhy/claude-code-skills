#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能广播剧音频生成工具 v2.0
自动识别角色、智能声音匹配、性格语速调整
"""

import re
import edge_tts
import asyncio
import subprocess
from pathlib import Path
import sys
import argparse
from character_parser import CharacterParser
from voice_matcher import VoiceMatcher


class SmartDramaToAudio:
    """智能广播剧音频生成器"""

    def __init__(self, add_name_prompt=True, use_speed_adjustment=True):
        """
        初始化生成器

        Args:
            add_name_prompt: 是否在对话前添加角色名提示
            use_speed_adjustment: 是否使用语速调整
        """
        self.add_name_prompt = add_name_prompt
        self.use_speed_adjustment = use_speed_adjustment

        # 兼容旧版VOICE_MAP（用于没有角色列表的情况）
        self.voice_map = {
            '男主角': 'zh-CN-YunxiNeural',
            '男1': 'zh-CN-YunxiNeural',
            '女1': 'zh-CN-XiaoxiaoNeural',
            '女2': 'zh-CN-XiaoyiNeural',
            '旁白': 'zh-CN-YunjianNeural',
            '我': 'zh-CN-YunxiNeural',
            '阿基': 'zh-CN-YunzeNeural',  # 机器人
            '少女': 'zh-CN-XiaoxiaoNeural',  # 外星少女
            '莱昂': 'zh-CN-YunxiNeural',
            '汤姆': 'zh-CN-YunxiNeural',
            '艾莉丝': 'zh-CN-XiaoxiaoNeural',
            '魔王': 'zh-CN-YunjianNeural',
            '国王': 'zh-CN-YunjianNeural',
        }

    def parse_script(self, text: str, voice_assignments: dict = None):
        """
        解析广播剧脚本

        Args:
            text: 脚本文本
            voice_assignments: 声音分配字典（如果有角色列表）

        Returns:
            对话片段列表
        """
        segments = []
        lines = text.strip().split('\n')

        current_speaker = None
        current_dialogue = []
        in_role_list = False  # 是否在角色列表区域
        found_role_list_title = False  # 是否找到角色列表标题

        for line in lines:
            line_stripped = line.strip()

            # 检测角色列表标题
            if re.match(r'^#+\s*\*{0,2}\s*角色列表\s*\*{0,2}', line_stripped, re.IGNORECASE):
                found_role_list_title = True
                in_role_list = True
                current_speaker = None
                current_dialogue = []
                continue

            if not line_stripped:
                # 空行
                if found_role_list_title and in_role_list:
                    # 角色列表中的空行，继续跳过
                    continue
                else:
                    # 正文中的空行，保存当前对话
                    if current_speaker and current_dialogue:
                        dialogue_text = ' '.join(current_dialogue).strip()
                        if dialogue_text:
                            segments.append(self._create_segment(current_speaker, dialogue_text, voice_assignments))
                        current_dialogue = []
                continue

            # 检查是否是对话行
            match = re.match(r'^【(.+?)】(.*)$', line_stripped)
            if match:
                # 如果还在角色列表区域，检查是否是角色描述
                if in_role_list:
                    # 检查是否是短描述（< 80字符）
                    if len(line_stripped) < 80:
                        # 这是角色描述，继续跳过
                        continue
                    else:
                        # 遇到长对话，说明角色列表结束
                        in_role_list = False
                        found_role_list_title = False
                        # 清空之前可能收集的内容
                        current_speaker = None
                        current_dialogue = []

                # 保存之前的对话
                if current_speaker and current_dialogue:
                    dialogue_text = ' '.join(current_dialogue).strip()
                    if dialogue_text:
                        segments.append(self._create_segment(current_speaker, dialogue_text, voice_assignments))
                    current_dialogue = []

                current_speaker = match.group(1).strip()
                dialogue_text = match.group(2).strip()

                if dialogue_text:
                    # 【角色名】后面有对话内容（同行）
                    current_dialogue.append(dialogue_text)
                # 否则期待下一行的对话内容

                continue

            # 普通文本
            if not in_role_list and current_speaker:
                current_dialogue.append(line_stripped)

        # 保存最后的对话
        if current_speaker and current_dialogue:
            dialogue_text = ' '.join(current_dialogue).strip()
            if dialogue_text:
                segments.append(self._create_segment(current_speaker, dialogue_text, voice_assignments))

        return segments

    def _create_segment(self, speaker: str, text: str, voice_assignments: dict = None) -> dict:
        """
        创建对话片段

        Args:
            speaker: 说话者
            text: 对话内容
            voice_assignments: 声音分配字典

        Returns:
            片段字典
        """
        segment = {
            'speaker': speaker,
            'original_text': text
        }

        # 旁白:直接读内容,不添加前缀
        if speaker == '旁白':
            segment['text'] = text
            segment['need_intro'] = False  # 不需要角色介绍
            # 使用默认旁白声音或声音分配中的旁白声音
            if voice_assignments and '旁白' in voice_assignments:
                segment['voice'] = voice_assignments['旁白']['voice']
                segment['rate'] = voice_assignments['旁白']['rate'] if self.use_speed_adjustment else '+0%'
            else:
                segment['voice'] = self.voice_map.get('旁白', 'zh-CN-YunjianNeural')
                segment['rate'] = '+0%'
        else:
            # 其他角色:添加"角色说"前缀信息
            if voice_assignments and speaker in voice_assignments:
                assignment = voice_assignments[speaker]
                segment['voice'] = assignment['voice']
                segment['rate'] = assignment['rate'] if self.use_speed_adjustment else '+0%'
            else:
                # 使用默认声音映射
                segment['voice'] = self.voice_map.get(speaker, self.voice_map['男主角'])
                segment['rate'] = '+0%'

            segment['text'] = text
            # 如果需要角色名提示,设置need_intro标志
            if self.add_name_prompt:
                segment['need_intro'] = True  # 需要旁白读"角色说"
                segment['intro_text'] = f"{speaker}说"
            else:
                segment['need_intro'] = False

        return segment

    def _get_narrator_voice(self, voice_assignments: dict = None) -> str:
        """
        获取旁白声音

        Args:
            voice_assignments: 声音分配字典

        Returns:
            旁白声音ID
        """
        if voice_assignments and '旁白' in voice_assignments:
            return voice_assignments['旁白']['voice']
        return 'zh-CN-YunjianNeural'  # 默认旁白声音

    async def generate_audio(self, segments: list, output_file: str, voice_assignments: dict = None):
        """
        生成音频

        Args:
            segments: 对话片段列表
            output_file: 输出文件路径
            voice_assignments: 声音分配字典(用于获取旁白声音)
        """
        import tempfile

        temp_dir = tempfile.mkdtemp()
        audio_files = []

        print(f"\n[INFO] 共 {len(segments)} 个片段\n")

        for i, seg in enumerate(segments, 1):
            speaker = seg['speaker']
            text = seg['text']
            voice = seg['voice']
            rate = seg['rate']
            need_intro = seg.get('need_intro', False)

            # 预览文本
            preview = text[:40] + "..." if len(text) > 40 else text
            rate_str = f" [语速{rate}]" if rate != '+0%' else ""

            # 如果需要角色介绍,显示特殊标记
            if need_intro:
                print(f"[{i}/{len(segments)}] {speaker}说: {preview}{rate_str}")
            else:
                print(f"[{i}/{len(segments)}] {speaker}: {preview}{rate_str}")

            # 收集当前片段的所有音频文件(可能包含角色介绍)
            segment_audio_parts = []

            # 如果需要角色介绍(非旁白且有add_name_prompt)
            if need_intro:
                intro_text = seg['intro_text']
                narrator_voice = self._get_narrator_voice(voice_assignments)

                # 生成"角色说"(用旁白声音)
                intro_file = Path(temp_dir) / f"segment_{i:04d}_intro.mp3"
                try:
                    intro_communicate = edge_tts.Communicate(intro_text, narrator_voice)
                    await intro_communicate.save(str(intro_file))
                    segment_audio_parts.append(str(intro_file))
                except Exception as e:
                    print(f"  [ERROR] 生成角色介绍失败: {e}")

            # 生成对话内容
            dialogue_file = Path(temp_dir) / f"segment_{i:04d}_dialogue.mp3"
            try:
                # 创建communicate对象
                communicate = edge_tts.Communicate(text, voice)

                # 设置语速
                if rate != '+0%':
                    communicate = edge_tts.Communicate(text, voice, rate=rate)

                await communicate.save(str(dialogue_file))
                segment_audio_parts.append(str(dialogue_file))
            except Exception as e:
                print(f"  [ERROR] 生成对话失败: {e}")

            # 如果有角色介绍和对话内容,需要合并
            if len(segment_audio_parts) > 1:
                # 合并角色介绍和对话内容
                merged_file = Path(temp_dir) / f"segment_{i:04d}.mp3"
                await self._merge_segment_parts(segment_audio_parts, str(merged_file), temp_dir)
                audio_files.append(str(merged_file))
            elif len(segment_audio_parts) == 1:
                # 只有一个音频文件,直接使用
                audio_files.append(segment_audio_parts[0])

        # 合并音频
        return await self._merge_audio(audio_files, output_file, temp_dir)

    async def _merge_segment_parts(self, audio_parts: list, output_file: str, temp_dir: str):
        """
        合并单个片段的多个音频部分(如角色介绍+对话内容)

        Args:
            audio_parts: 音频部分文件列表
            output_file: 输出文件路径
            temp_dir: 临时目录

        Returns:
            是否成功
        """
        if not audio_parts:
            return False

        # 如果只有一个文件,直接复制
        if len(audio_parts) == 1:
            import shutil
            shutil.copy(audio_parts[0], output_file)
            return True

        # 多个文件,使用ffmpeg合并
        list_file = Path(temp_dir) / f"temp_{Path(output_file).stem}_list.txt"
        with open(list_file, 'w', encoding='utf-8') as f:
            for audio_part in audio_parts:
                f.write(f"file '{audio_part}'\n")

        try:
            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(list_file),
                '-c', 'copy',
                str(output_file)
            ], check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"  [ERROR] 合并片段部分失败: {e}")
            return False

    async def _merge_audio(self, audio_files: list, output_file: str, temp_dir: str):
        """
        合并音频文件

        Args:
            audio_files: 音频文件列表
            output_file: 输出文件路径
            temp_dir: 临时目录

        Returns:
            是否成功
        """
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

    async def generate(self, input_file: str, output_file: str):
        """
        从脚本文件生成音频

        Args:
            input_file: 输入脚本文件
            output_file: 输出音频文件
        """
        print(f"[INFO] 读取脚本: {input_file}")

        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()

        # 尝试解析角色信息
        parser = CharacterParser()
        parse_result = parser.parse_script(text)

        voice_assignments = None

        if parse_result['characters']:
            # 有角色列表，使用智能声音匹配
            characters = parse_result['characters']
            matcher = VoiceMatcher()
            voice_assignments = matcher.assign_voices(characters)

            print(f"\n[INFO] 识别到 {len(characters)} 个角色")
            for name, info in characters.items():
                print(f"  - {name}: {info['gender']}, {info['age']}, {info['personality']}")

            print(f"\n[INFO] 声音分配结果:")
            for name, assignment in voice_assignments.items():
                rate_str = f" 语速{assignment['rate']}" if assignment['rate'] != '+0%' else ""
                print(f"  {name}: {assignment['voice_description']}{rate_str}")

            # 过滤掉角色列表部分
            if parse_result['role_list_end'] != -1:
                lines = text.split('\n')
                text = '\n'.join(lines[parse_result['role_list_end'] + 1:])
        else:
            print("\n[WARN] 未识别到角色列表，使用默认声音映射")
            print(f"[INFO] 对话前{'会' if self.add_name_prompt else '不会'}添加角色名")

        # 解析脚本
        segments = self.parse_script(text, voice_assignments)

        if not segments:
            print("[ERROR] 脚本中没有识别到对话内容")
            print("[INFO] 请检查脚本格式是否正确")
            return False

        print(f"\n[INFO] 识别到 {len(segments)} 个对话片段")

        # 生成音频
        return await self.generate_audio(segments, output_file, voice_assignments)


def main():
    parser = argparse.ArgumentParser(
        description='智能广播剧音频生成工具 v2.0 - 自动识别角色、智能声音匹配',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础使用（推荐）
  python drama_to_audio_v2.py 脚本.md 广播剧.mp3

  # 不添加角色名提示
  python drama_to_audio_v2.py 脚本.md 广播剧.mp3 --no-name-prompt

  # 不使用语速调整
  python drama_to_audio_v2.py 脚本.md 广播剧.mp3 --no-speed-adjustment
        """
    )

    parser.add_argument('input', help='输入的脚本文件')
    parser.add_argument('output', help='输出的MP3文件')
    parser.add_argument('--no-name-prompt', action='store_true',
                       help='不在对话前添加角色名提示')
    parser.add_argument('--no-speed-adjustment', action='store_true',
                       help='不使用性格语速调整')

    args = parser.parse_args()

    # 创建生成器
    generator = SmartDramaToAudio(
        add_name_prompt=not args.no_name_prompt,
        use_speed_adjustment=not args.no_speed_adjustment
    )

    # 生成音频
    asyncio.run(generator.generate(args.input, args.output))


if __name__ == '__main__':
    main()
