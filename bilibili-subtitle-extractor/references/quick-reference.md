# Bilibili 字幕提取 - 快速参考

## 核心工具安装

```bash
pip install yt-dlp
```

验证安装：
```bash
yt-dlp --version
ffmpeg -version
```

## 快速开始

### 1. 下载视频 + 字幕

```bash
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt
```

### 2. 转换字幕到 Markdown

```bash
python scripts/convert_srt_to_md.py \
    -i "*.srt" \
    -t "视频标题"
```

## 常用命令速查

### 📺 下载视频

| 场景 | 命令 |
|------|------|
| **最佳质量** | `-q best` |
| **1080P** | `-q 1080p` |
| **720P** | `-q 720p` |
| **自定义目录** | `-o ./videos` |
| **仅视频** | `--no-sub` |

示例：
```bash
python scripts/download_bilibili_video.py "URL" -c cookies.txt -q 1080p -o ./my-videos
```

### 📝 字幕选项

| 参数 | 说明 |
|------|------|
| `--sub-langs ai-zh` | AI 中文字幕 (默认) |
| `--sub-langs danmaku` | 弹幕 |
| `--sub-langs ai-en` | AI 英文字幕 |
| `--sub-langs ai-zh,ai-en` | 多语言字幕 |

示例：
```bash
python scripts/download_bilibili_video.py "URL" -c cookies.txt --sub-langs danmaku,ai-zh
```

### 🔍 查看可用格式

```bash
python scripts/download_bilibili_video.py "URL" -c cookies.txt --list-formats
```

### 🔄 批量处理

批量转换所有字幕：
```bash
for f in *.srt; do python scripts/convert_srt_to_md.py -i "$f"; done
```

## 输出文件

| 文件类型 | 命名方式 | 示例 |
|---------|---------|------|
| 📹 视频 | 标题_视频ID_分辨率.mp4 | 年终总结_BV1qwr_1080p.mp4 |
| 📝 字幕 | 标题 [视频ID].语言.srt | 年终总结 [BV1qwr].ai-zh.srt |
| 📄 Markdown | 标题.md | 年终总结.md |

## 故障排除

### ❌ 403 Forbidden
```bash
# 清除缓存
yt-dlp --rm-cache-dir

# 重新导出 cookies (必须)
# 然后重新运行
python scripts/download_bilibili_video.py "URL" -c new_cookies.txt
```

### ❌ 字幕缺失
```bash
# 检查可用字幕
python scripts/download_bilibili_video.py "URL" -c cookies.txt --list-formats

# 如果没有字幕，视频可能不支持或需要大会员
```

### ❌ 编码错误
转换字幕时如有乱码：
```bash
python scripts/convert_srt_to_md.py -i subtitle.srt -o output.md
```

脚本会自动检测 UTF-8 和 GBK 编码。

## 完整工作流示例

### 工作流 1: 下载 + 转换

```bash
# 步骤 1: 下载
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt

# 步骤 2: 转换
python scripts/convert_srt_to_md.py \
    -i "*.srt" \
    -t "2025年终总结" \
    --id "BV1qwrHBdE15"
```

### 工作流 2: 仅字幕

```bash
# 下载字幕 (不下载视频)
yt-dlp --cookies cookies.txt \
       --write-subs --sub-langs ai-zh \
       --skip-download "URL"

# 转换
python scripts/convert_srt_to_md.py -i video.ai-zh.srt
```

### 工作流 3: 批量处理

```bash
# 创建视频列表
cat > videos.txt <<EOF
https://www.bilibili.com/video/BV1xxx
https://www.bilibili.com/video/BV1yyy
EOF

# 批量下载
yt-dlp --cookies cookies.txt -a videos.txt

# 批量转换
for srt in *.srt; do
    python scripts/convert_srt_to_md.py -i "$srt"
done
```

## 参数速查表

### download_bilibili_video.py

```
必需参数:
  video_url              视频URL
  -c, --cookies FILE     cookies文件

可选参数:
  -o, --output DIR       输出目录 (默认: ~/Downloads/bilibili-downloads)
  -q, --quality STR      质量: best/1080p/720p (默认: best)
  --no-sub              不下载字幕
  --sub-langs STR       字幕语言 (默认: ai-zh)
  --list-formats        列出格式后退出
```

### convert_srt_to_md.py

```
必需参数:
  -i, --input FILE       输入SRT文件

可选参数:
  -o, --output FILE      输出Markdown文件
  -t, --title STR        视频标题
  --id STR              视频ID
  --url STR             视频URL
```

## 典型场景

### 场景 1: 快速下载视频
```bash
python scripts/download_bilibili_video.py "URL" -c cookies.txt
```

### 场景 2: 仅下载字幕
```bash
python scripts/download_bilibili_video.py "URL" -c cookies.txt --no-sub
```

### 场景 3: 获取特定质量
```bash
python scripts/download_bilibili_video.py "URL" -c cookies.txt -q 1080p
```

### 场景 4: 多语言字幕
```bash
python scripts/download_bilibili_video.py "URL" -c cookies.txt --sub-langs ai-zh,ai-en
```

### 场景 5: 转换已有字幕
```bash
python scripts/convert_srt_to_md.py -i subtitle.srt -t "我的视频"
```
