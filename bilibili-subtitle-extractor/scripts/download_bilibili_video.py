#!/usr/bin/env python3
"""
Download Bilibili video and subtitles using yt-dlp
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_ffmpeg_and_ytdlp():
    """Check if ffmpeg and yt-dlp are available"""
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        print("[OK] yt-dlp 已安装")
    except:
        print("[ERROR] yt-dlp 未安装，请先安装: pip install yt-dlp")
        return False

    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("[OK] ffmpeg 已安装")
    except:
        print("[ERROR] ffmpeg 未安装，请先安装 ffmpeg")
        return False

    return True

def download_bilibili_video(video_url, cookies_file, output_dir=None, quality='best', download_subtitles=True, subtitle_langs='ai-zh'):
    """Download Bilibili video and optional subtitles

    Args:
        video_url: Bilibili video URL (e.g., https://www.bilibili.com/video/BV1qwrHBdE15/)
        cookies_file: Path to cookies.txt file for authentication
        output_dir: Output directory (default: ~/Downloads/bilibili-downloads)
        quality: Video quality - 'best', '1080p', '720p', or specific format code
        download_subtitles: Whether to download subtitles (default: True)
        subtitle_langs: Comma-separated subtitle languages (default: 'ai-zh')

    Returns:
        dict: Paths to downloaded files
    """
    # Set default output directory
    if output_dir is None:
        output_dir = Path('H:') / '我的云端硬盘' / 'bilibili-downloads'
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"下载目录：{output_dir}")

    # Build yt-dlp command
    cmd = [
        'yt-dlp',
        '--cookies', str(cookies_file),
    ]

    # Set output template
    if download_subtitles:
        cmd.extend([
            '-o', str(output_dir / '%(title)s_%(id)s.%(ext)s')
        ])
    else:
        cmd.extend([
            '-o', str(output_dir / '%(title)s_%(id)s_%(resolution)s.%(ext)s')
        ])

    # Set quality
    if quality == 'best':
        cmd.extend(['-f', 'bestvideo+bestaudio/best'])
    elif quality == '1080p':
        cmd.extend(['-f', 'bv*[height<=1080]+ba/b[height<=1080]'])
    elif quality == '720p':
        cmd.extend(['-f', 'bv*[height<=720]+ba/b[height<=720]'])
    else:
        cmd.extend(['-f', quality])

    # Set merge output format
    cmd.extend(['--merge-output-format', 'mp4'])

    # Add subtitle options
    if download_subtitles:
        cmd.extend([
            '--write-subs',
            '--sub-langs', subtitle_langs,
            '--convert-subs', 'srt'
        ])

    # Add video URL
    cmd.append(video_url)

    print(f"\n执行命令：{' '.join(cmd)}")
    print("-" * 60)

    # Execute command
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print("\n[SUCCESS] 下载成功！")
        return True
    else:
        print(f"\n[ERROR] 下载失败！返回码：{result.returncode}")
        return False

def list_available_formats(video_url, cookies_file):
    """List available video formats and subtitles"""
    cmd = [
        'yt-dlp',
        '--cookies', str(cookies_file),
        '--list-formats',
        video_url
    ]

    print(f"{'='*60}")
    print("可用的视频格式：")
    print(f"{'='*60}")
    subprocess.run(cmd)

    print("\n")

    cmd = [
        'yt-dlp',
        '--cookies', str(cookies_file),
        '--list-subs',
        video_url
    ]

    print(f"{'='*60}")
    print("可用的字幕：")
    print(f"{'='*60}")
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description='Download Bilibili video and subtitles')
    parser.add_argument('video_url', help='Bilibili video URL')
    parser.add_argument('-c', '--cookies', required=True, help='Path to cookies.txt file')
    parser.add_argument('-o', '--output', help='Output directory (default: ~/Downloads/bilibili-downloads)')
    parser.add_argument('-q', '--quality', default='best',
                       help='Video quality: best, 1080p, 720p, or format code')
    parser.add_argument('--no-sub', action='store_true', help='Do not download subtitles')
    parser.add_argument('--sub-langs', default='ai-zh', help='Subtitle languages (comma-separated)')
    parser.add_argument('--list-formats', action='store_true', help='List available formats and exit')

    args = parser.parse_args()

    # Check dependencies
    if not check_ffmpeg_and_ytdlp():
        return 1

    if args.list_formats:
        list_available_formats(args.video_url, args.cookies)
        return 0

    # Download video
    success = download_bilibili_video(
        video_url=args.video_url,
        cookies_file=args.cookies,
        output_dir=args.output,
        quality=args.quality,
        download_subtitles=not args.no_sub,
        subtitle_langs=args.sub_langs
    )

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
