#!/usr/bin/env python3
"""
convert_srt_to_speech.py
将字幕转换为口播稿，基于字幕块合并策略
"""

import re
import sys
import os
import argparse

# 需要移除的填充词和语气词
filler_words = [
    '这个那个',
    '那个',
    '这个',
    '就是说',
    '嗯',
    '嗯嗯',
    '嗯啊',
    '啊',
    '啊啊',
    '哦',
    '哦哦',
    '哎呀',
    '哎',
    '哇',
    '哇哦',
    '好吧',
    '对吧',
    '是吧',
    '行吧',
    '好吗',
    '好吗',
    '这个嘛',
    '那个嘛',
    '这个啊',
    '那个啊',
    '那个的话',
    '这个的话',
    '你懂的',
    '你懂的',
]

# 句首需要移除的词
sentence_prefixes = [
    '所以',
    '然后',
    '接着',
    '那么',
    '可是',
    '但是',
    '不过',
    '于是',
    "然后呢",
    "后来呢",
]

# 常见的转录修正
transcription_fixes = {
    '是滴': '是的',
    '事滴': '是的',
    '系滴': '是的',
    '对滴': '对的',
    '九种胳膊': '九种方法',
    'A股份': 'A股',
    'A上市公司': 'A股上市公司',
    'h股': 'H股',
    'H股': 'H股',
    'IPO受理': 'IPO受理',
    'BP': 'BP',
    'BM': 'BM',
    'HBM4 e': 'HBM4E',
    'drum n m': 'DRAM/NAND',
    'drum和m': 'DRAM和NAND',
    'Drum和m': 'DRAM和NAND',
    'Drum n m': 'DRAM/NAND',
    'OPTIMUS3': 'Optimus 3',
    'etf': 'ETF',
    'Etf': 'ETF',
    'ETF脱': 'ETF托',
    '投机倒把': '投机',
}

def clean_single_subtitle(text):
    """
    清理单个字幕文本
    字幕文本可能包含多个词，移除填充词和语气词
    """
    # 去掉首尾空格
    text = text.strip()

    # 移除填充词
    for filler in filler_words:
        pattern = r'\b' + re.escape(filler) + r'\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # 转录修正
    for wrong, correct in transcription_fixes.items():
        text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text, flags=re.IGNORECASE)

    # 修复多个空格
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def add_punctuation(text):
    """
    智能添加标点符号

    规则：
    - 如果文本很短（<10个字符），通常没有标点
    - 如果文本较长 (>30个字符)，一般以句号结束
    - 如果文本是疑问或感叹，保留相应标点
    """
    if not text:
        return text

    text = text.strip()

    # 如果已经有标点，直接返回
    if re.match(r'.*[。！？;；.!?]$', text):
        return text

    # 根据文本长度和内容决定标点
    if len(text) < 10:
        # 简短文本，通常是强调或口语，用逗号
        if '吗' in text or '呢' in text or '啊' in text:
            return text + '。'
        return text

    if len(text) > 30:
        # 长文本，通常是完整句子，用句号
        if text.endswith('吗'):
            return text + '？'
        elif text.endswith('重要'):
            return text + '。'
        elif text.startswith('如果') or text.startswith('假如'):
            return text + '，'
        else:
            return text + '。'

    # 中等长度，根据疑问词判断
    if text.endswith('吗') or text.endswith('呢') or text.endswith('什么'):
        return text + '？'
    elif text.endswith('啊') or text.endswith('呀') or text.endswith('哦'):
        return text + '。'

    # 默认情况
    return text + '。'

def merge_subtitles_into_sentences(subtitles):
    """
    将字幕块合并成较长的句子

    策略：
    - 设置目标：每个合并后的句子 15-50字
    - 将多个短字幕合并成一个较长的句子
    """
    merged = []
    current_sentence = ""
    current_length = 0

    for subtitle_text in subtitles:
        # 清理字幕文本
        cleaned = clean_single_subtitle(subtitle_text)
        if not cleaned:
            continue

        cleaned_len = len(cleaned)

        # 决定是否需要合并
        if current_length == 0:
            # 开始新句子
            current_sentence = cleaned
            current_length = cleaned_len
        elif current_length + cleaned_len < 50:
            # 继续合并（用空格连接）
            current_sentence += ' ' + cleaned
            current_length += cleaned_len
        else:
            # 句子已经够长，保存并重新开始
            merged.append(current_sentence)
            current_sentence = cleaned
            current_length = cleaned_len

    # 添加最后一个句子
    if current_sentence:
        merged.append(current_sentence)

    # 为每个合并后的句子添加标点
    return [add_punctuation(sent) for sent in merged]

def organize_into_paragraphs(sentences, max_sentences_per_para=5):
    """
    将句子组织成段落，每段最多5句
    """
    paragraphs = []
    current_para = []

    for sentence in sentences:
        current_para.append(sentence)

        # 如果达到5句，开始新段落
        if len(current_para) >= max_sentences_per_para:
            paragraphs.append(' '.join(current_para))
            current_para = []

    # 添加剩余的句子
    if current_para:
        paragraphs.append(' '.join(current_para))

    return paragraphs

def structure_into_sections(paragraphs):
    """
    将段落组织成章节
    """
    sections = []
    current_section = []

    # 主题分割关键词
    keywords = ['首先', '其次', '第二', '另外', '还有', '最后', '总结', '总之', '也就是说']

    for i, paragraph in enumerate(paragraphs):
        current_section.append(paragraph)

        # 检查是否需要开始新章节
        if i < len(paragraphs) - 1:
            next_para = paragraphs[i + 1]

            # 如果下一段包含关键词，开始新章节
            has_keyword = any(keyword in next_para for keyword in keywords)

            if has_keyword and current_section:
                sections.append('\n\n'.join(current_section))
                current_section = []

    # 添加剩余段落
    if current_section:
        sections.append('\n\n'.join(current_section))

    return sections

def srt_to_speech_script(srt_file, output_file=None, video_title=None, video_id=None, video_url=None):
    """
    转换SRT字幕为口播稿

    处理流程：
    1. 读取并解析SRT文件
    2. 合并字幕块到句子
    3. 组织成段落（每段5句）
    4. 结构化章节
    5. 生成Markdown
    """
    if output_file is None:
        base = os.path.splitext(os.path.basename(srt_file))[0]
        base = re.sub(r'\.[a-z]{2}-[a-z]{2}$', '', base)
        output_file = f"{base}_口播稿.md"

    # 读取SRT文件
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(srt_file, 'r', encoding='gbk') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(srt_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()

    # 解析字幕块
    blocks = re.split(r'\n\s*\n', content.strip())

    # 提取字幕文本
    subtitle_texts = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # 提取字幕文本（跳过序号和时间戳）
            text = ' '.join(lines[2:])
            if text.strip():
                subtitle_texts.append(text.strip())

    # 合并字幕为句子
    sentences = merge_subtitles_into_sentences(subtitle_texts)

    # 组织段落（每段5句）
    paragraphs = organize_into_paragraphs(sentences)

    # 结构化章节
    sections = structure_into_sections(paragraphs)

    # 写入Markdown文件
    with open(output_file, 'w', encoding='utf-8') as f:
        # 标题
        if video_title:
            f.write(f'# 口播稿：{video_title}\n\n')
        else:
            f.write('# 视频口播稿\n\n')

        # 元数据
        if video_id:
            f.write(f'**视频ID**：{video_id}\n\n')
        if video_url:
            f.write(f'**视频链接**：{video_url}\n\n')

        subtitle_type = "AI生成" if "ai-" in srt_file else "字幕"
        f.write(f'**字幕类型**：{subtitle_type}\n\n')
        f.write('---\n\n')

        # 内容
        for i, section in enumerate(sections):
            if len(sections) > 1:
                f.write(f'## 第{i+1}部分\n\n')
            f.write(section)
            f.write('\n\n')

        # 页脚
        f.write('---\n\n')
        f.write('*以上内容由AI字幕自动生成并整理成口播稿，可能存在少量误差*\n')

    stats = {
        'subtitle_blocks': len(blocks),
        'merged_sentences': len(sentences),
        'paragraphs': len(paragraphs),
        'sections': len(sections)
    }

    return output_file, stats

def main():
    parser = argparse.ArgumentParser(
        description='Convert SRT subtitle to speech script (口播稿)'
    )

    parser.add_argument('-i', '--input', required=True, help='Input SRT file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-t', '--title', help='Video title')
    parser.add_argument('--id', help='Video ID')
    parser.add_argument('--url', help='Video URL')

    args = parser.parse_args()

    try:
        output_file, stats = srt_to_speech_script(
            srt_file=args.input,
            output_file=args.output,
            video_title=args.title,
            video_id=args.id,
            video_url=args.url
        )

        print(f'\n字幕已转换为口播稿：{output_file}')
        print(f'\n统计信息：')
        print(f'  · 原始字幕块数：{stats["subtitle_blocks"]}')
        print(f'  · 合并后句子数：{stats["merged_sentences"]}')
        print(f'  · 段落数：{stats["paragraphs"]}')
        print(f'  · 章节数：{stats["sections"]}')

    except Exception as e:
        print(f'错误：{e}', file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
