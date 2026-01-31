#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广播剧文稿生成工具
第一步：生成可编辑的文稿，标注每段对话的说话人
"""

import re
import json
from pathlib import Path
import sys


# 角色特征词汇
CHARACTER_KEYWORDS = {
    '艾米': {
        'keywords': ['根据', '数据显示', '大数据', '算法', '分析', '检测', '建议', '统计', '概率', '幸福指数', '智商', '数据库'],
        'name_variations': ['艾米', 'AI管家'],
        'voice': 'zh-CN-XiaoxiaoNeural',
        'description': 'AI管家，女性声音，技术性强'
    },
    '和也': {
        'keywords': ['完蛋', '什么鬼', '闭嘴', '能不能', '为什么', '帮忙', '论文', '起床'],
        'name_variations': ['和也', '佐藤和也'],
        'voice': 'zh-CN-YunxiNeural',
        'description': '男主角，年轻男声'
    },
    '星月星空': {
        'keywords': ['意识上传', '永生', '物理学', '转校生', '天体物理学家'],
        'name_variations': ['星空', '星月星空'],
        'voice': 'zh-CN-XiaoyiNeural',
        'description': '转校生，银发少女，成熟女声'
    },
    '旁白': {
        'keywords': [],
        'name_variations': ['我', '旁白'],
        'voice': 'zh-CN-YunxiNeural',
        'description': '第一人称旁白，使用男主角声音'
    }
}


def extract_dialogues_with_speakers(text):
    """
    提取对话并识别说话人
    """
    lines = text.split('\n')
    script_segments = []

    for i, line in enumerate(lines, 1):
        # 查找对话
        pattern = r'[「『]([^「」『』]+)[」』]'
        matches = re.finditer(pattern, line)

        for match in matches:
            dialogue_text = match.group(1)

            # 识别说话人
            speaker = identify_speaker(text, i, dialogue_text, lines)

            script_segments.append({
                'line_number': i,
                'speaker': speaker,
                'dialogue': dialogue_text,
                'context': line.strip()
            })

    return script_segments


def identify_speaker(text, line_num, dialogue_text, lines):
    """
    多策略识别说话人
    """

    # 策略1: 内容特征分析（优先级最高）
    content_result = identify_by_content(dialogue_text)
    if content_result:
        return content_result

    # 策略2: 同一行的说话人标识
    same_line_result = identify_by_same_line(lines[line_num - 1], dialogue_text)
    if same_line_result:
        return same_line_result

    # 策略3: 上下文分析（前后5行）
    context_result = identify_by_context(lines, line_num)
    if context_result:
        return context_result

    # 默认：旁白
    return '旁白'


def identify_by_content(dialogue_text):
    """根据对话内容特征识别说话人"""
    scores = {}

    for char_name, char_info in CHARACTER_KEYWORDS.items():
        score = 0
        for keyword in char_info['keywords']:
            if keyword in dialogue_text:
                score += 1
        scores[char_name] = score

    # 需要至少2个特征词才确定
    max_score = max(scores.values())
    if max_score >= 2:
        return max(scores, key=scores.get)

    return None


def identify_by_same_line(line, dialogue_text):
    """检查同一行的说话人标识"""
    before = line[:line.find(dialogue_text)]

    # 对话前的"XX说"
    speaker_match = re.search(r'(\w{2,4})(说|道|问|喊|笑道|解释|回答)', before)
    if speaker_match:
        name = speaker_match.group(1)
        return normalize_character_name(name)

    return None


def identify_by_context(lines, line_num):
    """检查上下文"""
    start = max(0, line_num - 6)
    end = min(len(lines), line_num + 5)

    mentions = {}

    for i in range(start, end):
        if i == line_num - 1:
            continue

        line = lines[i]

        for char_name, char_info in CHARACTER_KEYWORDS.items():
            for variation in char_info['name_variations']:
                if variation in line:
                    weight = 3 if i >= line_num - 2 else 1
                    mentions[char_name] = mentions.get(char_name, 0) + weight

    if mentions:
        max_char = max(mentions, key=mentions.get)
        if mentions[max_char] >= 3:
            return max_char

    return None


def normalize_character_name(name):
    """标准化角色名"""
    if '和也' in name:
        return '和也'
    elif '星空' in name:
        return '星月星空'
    elif name == '艾米':
        return '艾米'
    else:
        return '旁白'


def generate_markdown_script(script_segments, output_file):
    """生成Markdown格式的广播剧文稿"""

    md_content = """# 广播剧文稿

**说明**：这是自动识别的广播剧文稿，请检查每段对话的说话人是否正确。
- 如有错误，请修改说话人名称
- 修改完成后保存文件
- 然后运行音频生成命令

---

## 角色列表

| 角色 | 声音 | 说明 |
|------|------|------|
"""

    for char_name, char_info in CHARACTER_KEYWORDS.items():
        md_content += f"| {char_name} | {char_info['voice']} | {char_info['description']} |\n"

    md_content += "\n---\n\n## 对话文稿\n\n"

    # 生成对话列表
    current_speaker = None

    for i, seg in enumerate(script_segments, 1):
        speaker = seg['speaker']
        dialogue = seg['dialogue']
        line_num = seg['line_number']

        # 添加分隔符
        if speaker != current_speaker:
            md_content += "\n"

        md_content += f"### [{i}] 第{line_num}行 - **{speaker}**\n\n"
        md_content += f"**对话**：{dialogue}\n\n"
        md_content += f"**原文**：{seg['context'][:100]}...\n\n"

        # 添加标注提示
        if speaker in ['艾米', '和也', '星月星空']:
            md_content += f"✓ 已识别\n\n"
        else:
            md_content += f"⚠️ 需要确认\n\n"

        md_content += "---\n\n"

        current_speaker = speaker

    # 添加统计信息
    speaker_counts = {}
    for seg in script_segments:
        speaker = seg['speaker']
        speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1

    md_content += "\n## 统计信息\n\n"
    md_content += "| 角色 | 对话数量 |\n"
    md_content += "|------|---------|\n"

    for speaker, count in sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True):
        md_content += f"| {speaker} | {count} |\n"

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"[OK] 文稿已生成: {output_file}")
    print(f"[INFO] 共 {len(script_segments)} 段对话")


def generate_json_script(script_segments, output_file):
    """生成JSON格式的文稿（方便程序处理）"""

    script_data = {
        'metadata': {
            'total_segments': len(script_segments),
            'characters': list(CHARACTER_KEYWORDS.keys())
        },
        'segments': script_segments
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)

    print(f"[OK] JSON文稿已生成: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("用法: python generate_script.py <小说文件路径>")
        print("\n示例:")
        print("  python generate_script.py 科幻小说.md")
        sys.exit(1)

    input_file = sys.argv[1]
    input_path = Path(input_file)

    print(f"[INFO] 读取文件: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"[INFO] 文本长度: {len(text)} 字符")

    # 提取对话
    print(f"[INFO] 正在分析对话...")
    script_segments = extract_dialogues_with_speakers(text)

    print(f"[INFO] 共识别 {len(script_segments)} 段对话")

    # 生成文稿
    md_output = input_path.parent / (input_path.stem + '_广播剧文稿.md')
    json_output = input_path.parent / (input_path.stem + '_广播剧文稿.json')

    print(f"\n[INFO] 生成广播剧文稿...")

    generate_markdown_script(script_segments, str(md_output))
    generate_json_script(script_segments, str(json_output))

    print("\n" + "=" * 60)
    print("✅ 文稿生成完成！")
    print("=" * 60)
    print(f"\n📄 Markdown文稿: {md_output}")
    print(f"📊 JSON文稿: {json_output}")
    print("\n下一步：")
    print("1. 打开并查看文稿（推荐使用Markdown版本）")
    print("2. 检查每段对话的说话人是否正确")
    print("3. 修正错误后保存")
    print("4. 运行命令生成音频：")
    print(f"   python generate_audio_from_script.py {md_output.name}")
    print("=" * 60)


if __name__ == '__main__':
    main()
