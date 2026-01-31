# Bilibili 字幕提取工作流指南

## 完整工作流

### 步骤 1: 准备环境

1. **安装必要工具**:
   ```bash
   pip install yt-dlp
   ```

2. **准备 cookies 文件**:
   - 登录 Bilibili 账号
   - 使用浏览器导出 cookies (获取 bilibili_cookies.txt)
   - 保存到安全位置 (如: ~/Downloads/bilibili_cookies.txt)

### 步骤 2: 查看可用格式

在下载前检查可用的视频格式和字幕：

```bash
python scripts/download_bilibili_video.py "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt \
    --list-formats
```

输出示例：
```
可用的字幕：
Language Formats
danmaku  xml
ai-zh    srt
ai-en    srt
ai-ja    srt
ai-es    srt
ai-ar    srt
ai-pt    srt
```

### 步骤 3: 下载视频和字幕

#### 方案 A: 下载视频和字幕

```bash
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt \
    --quality best
```

此命令会:
- 下载最佳质量的视频
- 下载所有可用的字幕 (默认: ai-zh 中文字幕)
- 输出格式: MP4
- 保存到: ~/Downloads/bilibili-downloads/

#### 方案 B: 仅下载字幕

```bash
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt \
    --no-sub
```

#### 方案 C: 自定义输出和格式

```bash
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt \
    --output ./my-videos \
    --quality 1080p \
    --sub-langs ai-zh,ai-en
```

### 步骤 4: 转换字幕为 Markdown

下载完成后，转换 SRT 字幕文件为 Markdown 格式：

```bash
python scripts/convert_srt_to_md.py \
    -i "2025年终总结！... [BV1qwrHBdE15].ai-zh.srt" \
    -o "2025年终总结.md" \
    -t "2025年终总结！同居7年，我们之间最大的分歧和变化..." \
    --id "BV1qwrHBdE15" \
    --url "https://www.bilibili.com/video/BV1qwrHBdE15/"
```

如果只转换基本字幕：

```bash
python scripts/convert_srt_to_md.py -i video.srt -o video.md
```

## 批量处理工作流

### 批量下载多个视频

1. 创建视频链接列表文件:

```bash
cat > videos.txt <<EOF
https://www.bilibili.com/video/BV1xxx
https://www.bilibili.com/video/BV1yyy
https://www.bilibili.com/video/BV1zzz
EOF
```

2. 使用 yt-dlp 批量下载:

```bash
yt-dlp --cookies ~/Downloads/bilibili_cookies.txt \
       -f "bestvideo+bestaudio" \
       -a videos.txt
```

### 批量转换字幕

假设已下载多个 .srt 文件:

```bash
for srt_file in *.srt; do
    python scripts/convert_srt_to_md.py -i "$srt_file"
done
```

## 常见问题

### 问题 1: 403 Forbidden 错误

**症状**: `HTTP Error 403: Forbidden`

**解决方案**:
1. 确认 cookies 文件是最新的
2. 重新登录 Bilibili 并导出新鲜 cookies
3. 确认视频在浏览器中可访问
4. 检查账号是否被封禁或有下载限制

```bash
# 重新下载前清除 yt-dlp 缓存
yt-dlp --rm-cache-dir
```

### 问题 2: 字幕下载失败

**症状**: `Unable to extract subtitle info`

**解决方案**:
1. 确认视频是否有字幕:
   ```bash
   python scripts/download_bilibili_video.py "URL" --cookies cookies.txt --list-formats
   ```

2. 尝试下载不同语言的字幕:
   ```bash
   --sub-langs danmaku,ai-zh
   ```

3. 确认视频是否需要大会员才能访问字幕

### 问题 3: 编码错误

**症状**: `UnicodeDecodeError` 或中文字符显示异常

**解决方案**:
转换脚本会自动尝试 UTF-8 和 GBK 编码。如果仍然失败:

1. 检查原始字幕文件编码:
   ```bash
   file -i subtitle.srt
   ```

2. 手动转换编码:
   ```bash
   iconv -f GBK -t UTF-8 subtitle.srt > subtitle_utf8.srt
   ```

### 问题 4: 视频格式不支持

**症状**: `Requested format is not available` 或 `Unable to download video`

**解决方案**:
1. 列出可用格式并选择合适的:
   ```bash
   python scripts/download_bilibili_video.py "URL" --cookies cookies.txt --list-formats
   ```

2. 使用自动选择最佳可用格式:
   ```bash
   -f "bv*+ba/b"
   ```

3. 对于多P视频，下载所有分P:
   ```bash
   --yes-playlist
   ```

### 问题 5: 速度慢或连接超时

**解决方案**:
1. 使用并发下载:
   ```bash
   -N 4  # 4 个连接
   ```

2. 使用代理 (如果需要):
   ```bash
   --proxy http://127.0.0.1:1080
   ```

3. 设置超时时间:
   ```bash
   --socket-timeout 60
   ```

## 参数详解

### download_bilibili_video.py

- `-c, --cookies`: cookies.txt 文件路径 (必需)
- `-o, --output`: 输出目录 (默认: ~/Downloads/bilibili-downloads)
- `-q, --quality`: 视频质量
  - `best`: 最佳质量 (默认)
  - `1080p`: 1080P 或更低
  - `720p`: 720P 或更低
  - 或指定格式代码 (如: 100026+30280)
- `--no-sub`: 不下载字幕
- `--sub-langs`: 字幕语言 (逗号分隔, 默认: ai-zh)
  - `ai-zh`: AI 中文
  - `ai-en`: AI 英文
  - `danmaku`: 弹幕
- `--list-formats`: 仅列出可用格式并退出

### convert_srt_to_md.py

- `-i, --input`: 输入 SRT 文件 (必需)
- `-o, --output`: 输出 Markdown 文件 (自动命名如果未提供)
- `-t, --title`: 视频标题 (用于 Markdown 头部)
- `--id`: 视频 ID (如: BV1qwrHBdE15)
- `--url`: 视频完整 URL

## 输出文件说明

### 视频文件
- 格式: MP4
- 命名: `视频标题_视频ID_分辨率.mp4`
- 示例: `2025年终总结！..._BV1qwrHBdE15_1080p.mp4`

### 字幕文件
- 格式: SRT (转换为可读的文本格式)
- 命名: `视频标题 [视频ID].语言代码.srt`
- 示例: `2025年终总结！... [BV1qwrHBdE15].ai-zh.srt`

### Markdown 文件
- 格式: Markdown
- 命名: `视频标题.md` 或根据输出参数
- 内容: 时间戳 + 字幕文本
- 示例: `2025年终总结.md`

## 进阶用法

### 使用配置文件

创建配置文件 `config.yaml`:

```yaml
cookies: ~/Downloads/bilibili_cookies.txt
output_dir: ~/Downloads/bilibili-downloads
quality: best
subtitles: true
sub_langs: [ai-zh, ai-en]
```

然后引用:

```bash
python scripts/download_bilibili_video.py "$VIDEO_URL" \
    --cookies "$(grep cookies config.yaml | cut -d': ' -f2)"
```

### 集成到自动化脚本

在 shell 脚本或 Python 脚本中使用:

```python
import subprocess

def download_and_convert(video_url, cookies_file):
    # 下载
    subprocess.run([
        'python', 'scripts/download_bilibili_video.py',
        video_url, '--cookies', cookies_file
    ], check=True)

    # 转换字幕
    srt_files = [f for f in os.listdir('.') if f.endswith('.srt')]
    for srt_file in srt_files:
        subprocess.run([
            'python', 'scripts/convert_srt_to_md.py',
            '-i', srt_file
        ], check=True)
```
