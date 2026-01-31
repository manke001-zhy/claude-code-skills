#!/usr/bin/env python3
import re
import sys
import os
import argparse

def srt_to_markdown(srt_file, output_file=None, video_title=None, video_id=None, video_url=None):
    """Convert SRT subtitle file to Markdown format

    Args:
        srt_file: Path to the SRT subtitle file
        output_file: Path to the output Markdown file (auto-generated if None)
        video_title: Video title for the header
        video_id: Video ID (e.g., BV1qwrHBdE15 for Bilibili)
        video_url: Full video URL
    """
    # Auto-generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(srt_file))[0]
        # Remove language code if present (e.g., .ai-zh.srt -> remove .ai-zh)
        base_name = re.sub(r'\.[a-z]{2}-[a-z]{2}$', '', base_name)
        output_file = f"{base_name}.md"

    # Read SRT file with encoding detection
    try:
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with gbk encoding (common for Chinese)
        try:
            with open(srt_file, 'r', encoding='gbk') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback to system default
            with open(srt_file, 'r', encoding='utf-8-sig', errors='ignore') as f:
                content = f.read()

    # Split by subtitle blocks (blank lines)
    blocks = re.split(r'\n\s*\n', content.strip())

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        if video_title:
            f.write(f'# 字幕：{video_title}\n\n')
        else:
            f.write('# 视频字幕\n\n')

        if video_id:
            f.write(f'**视频ID**：{video_id}\n\n')
        if video_url:
            f.write(f'**视频链接**：{video_url}\n\n')

        subtitle_type = "AI生成" if "ai-" in srt_file else "字幕"
        f.write(f'**字幕类型**：{subtitle_type}\n\n')
        f.write('---\n\n')

        # Process each subtitle block
        valid_blocks = 0
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Extract subtitle number, timestamp and text
                subtitle_id = lines[0]
                timestamp = lines[1]
                text = ' '.join(lines[2:])

                # Clean up the text (remove leading/trailing spaces)
                text = text.strip()

                if text:  # Only write if there's actual text
                    # Write to markdown
                    f.write(f'### {timestamp}\n\n')
                    f.write(f'{text}\n\n')
                    f.write('---\n\n')
                    valid_blocks += 1

        # Write footer
        f.write('---\n\n')
        f.write('*本字幕由AI自动生成，可能存在少量错误*\n')

    print(f'字幕已转换为 Markdown：{output_file}')
    print(f'共处理 {valid_blocks} 个字幕块')
    return output_file, valid_blocks


def main():
    parser = argparse.ArgumentParser(description='Convert SRT subtitle file to Markdown format')
    parser.add_argument('-i', '--input', required=True, help='Input SRT file path')
    parser.add_argument('-o', '--output', help='Output Markdown file path (auto-generated if not provided)')
    parser.add_argument('-t', '--title', help='Video title')
    parser.add_argument('--id', help='Video ID')
    parser.add_argument('--url', help='Video URL')

    args = parser.parse_args()

    try:
        output_file, count = srt_to_markdown(
            srt_file=args.input,
            output_file=args.output,
            video_title=args.title,
            video_id=args.id,
            video_url=args.url
        )
        print(f"\n转换完成！输出文件：{output_file}")
        return 0
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
