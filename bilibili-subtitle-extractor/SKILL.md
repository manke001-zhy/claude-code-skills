---
name: bilibili-subtitle-extractor - B站字幕提取
description: 从 Bilibili 下载视频并提取字幕，转换为 Markdown 格式。用于需要下载 Bilibili 视频、提取字幕并将字幕转换为可读 Markdown 文档的场景。
---

# Bilibili 字幕提取技能

本技能提供从 Bilibili 下载视频、提取字幕并转换为 Markdown 格式的完整工作流。

## 快速开始

### 1. 下载视频和字幕

```bash
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt \
    --quality best
```

### 2. 转换字幕为 Markdown

```bash
python scripts/convert_srt_to_md.py \
    -i "*.srt" \
    -t "视频标题" \
    --id "BV1qwrHBdE15"
```

## 详细指南

对于完整的工作流、参数详解和故障排除，请参考：[完整工作流指南](references/workflow-guide.md)

对于常用命令速查，请参考：[快速参考](references/quick-reference.md)

## 前置要求

### 必需工具

1. **yt-dlp**: 视频下载工具
   ```bash
   pip install yt-dlp
   ```

2. **ffmpeg**: 视频处理工具
   - Windows: 下载并添加到 PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

3. **cookies 文件**: Bilibili 登录凭证
   - 从浏览器导出 cookies (www.bilibili.com)
   - 保存为 `bilibili_cookies.txt`

### 验证安装

```bash
yt-dlp --version
ffmpeg -version
```

## 使用脚本

### 脚本 1: download_bilibili_video.py

下载 Bilibili 视频和字幕。

**基本用法**:
```bash
python scripts/download_bilibili_video.py VIDEO_URL --cookies COOKIES_FILE
```

**完整示例**:
```bash
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt \
    --output ~/Videos \
    --quality 1080p \
    --sub-langs ai-zh,ai-en
```

**参数说明**:
- `VIDEO_URL`: Bilibili 视频 URL (必需)
- `-c, --cookies`: cookies.txt 文件路径 (必需)
- `-o, --output`: 输出目录 (默认: H:\我的云端硬盘\bilibili-downloads)
- `-q, --quality`: 视频质量 (best/1080p/720p, 默认: best)
- `--no-sub`: 不下载字幕
- `--sub-langs`: 字幕语言 (默认: ai-zh)
- `--list-formats`: 查看可用格式后退出

### 脚本 2: convert_srt_to_speech.py (推荐)

将 SRT 字幕文件转换为**完整的口播稿**（智能合并短句、移除口头禅、优化段落结构）。

**基本用法**:
```bash
python scripts/convert_srt_to_speech.py -i INPUT.srt
```

**完整示例**:
```bash
python scripts/convert_srt_to_speech.py \
    -i "2025年终总结 [BV1qwrHBdE15].ai-zh.srt" \
    -o "2025年终总结_口播稿.md" \
    -t "2025年终总结！同居7年，我们之间最大的分歧和变化..." \
    --id "BV1qwrHBdE15" \
    --url "https://www.bilibili.com/video/BV1qwrHBdE15/"
```

**功能特点**:
- 自动合并短句子，形成连贯段落
- 移除口头禅和填充词（"这个那个"、"就是说"、"嗯啊哦"等）
- 按主题自动分段
- 优化标点符号和语句流畅度
- 保留核心内容，移除重复表达

**参数说明**:
- `-i, --input`: 输入 SRT 文件路径 (必需)
- `-o, --output`: 输出 Markdown 文件路径 (自动命名如果未提供，默认为 `_口播稿.md`)
- `-t, --title`: 视频标题 (用于 Markdown 头部)
- `--id`: 视频 ID
- `--url`: 视频完整 URL

### 脚本 3: convert_srt_to_md.py

将 SRT 字幕文件转换为**带时间戳的字幕文档**（保留原始时间戳，适合需要精确时间参考的场景）。

**基本用法**:
```bash
python scripts/convert_srt_to_md.py -i INPUT.srt
```

**完整示例**:
```bash
python scripts/convert_srt_to_md.py \
    -i "2025年终总结 [BV1qwrHBdE15].ai-zh.srt" \
    -o "2025年终总结_字幕版.md" \
    -t "2025年终总结！同居7年，我们之间最大的分歧和变化..." \
    --id "BV1qwrHBdE15" \
    --url "https://www.bilibili.com/video/BV1qwrHBdE15/"
```

**参数说明**:
- `-i, --input`: 输入 SRT 文件路径 (必需)
- `-o, --output`: 输出 Markdown 文件路径 (自动命名如果未提供)
- `-t, --title`: 视频标题 (用于 Markdown 头部)
- `--id`: 视频 ID
- `--url`: 视频完整 URL

**输出示例**:
```markdown
### 00:00:00,000 --> 00:00:01,360

哈喽大家

---

### 00:00:01,360 --> 00:00:05,160

今天是2025的年度总结

---
```

**转换结果示例**:
```markdown
# 字幕：视频标题

**视频ID**: BV1qwrHBdE15
**视频链接**: https://www.bilibili.com/video/BV1qwrHBdE15/
**字幕类型**: AI生成

---

### 00:00:00,000 --> 00:00:01,360

哈喽大家

---

### 00:00:01,360 --> 00:00:05,160

今天是2025的年度总结

---
```

## 完整工作流

### 步骤 1: 准备

确保已安装 yt-dlp 和 ffmpeg，并准备好 cookies 文件。

### 步骤 2: 下载

使用 download_bilibili_video.py 下载视频和字幕：

```bash
python scripts/download_bilibili_video.py \
    "BILIBILI_VIDEO_URL" \
    --cookies ~/Downloads/bilibili_cookies.txt \
    --quality best
```

此步骤会生成：
- `.mp4` 视频文件
- `.srt` 字幕文件（如果有）

### 步骤 3: 转换

使用 convert_srt_to_md.py 将字幕转换为 Markdown：

```bash
python scripts/convert_srt_to_md.py \
    -i "DOWNLOADED.srt" \
    -o "OUTPUT.md" \
    -t "视频标题"
```

### 步骤 4: 验证

检查生成的 Markdown 文件内容和格式是否正确。

## 常见问题

### 403 Forbidden 错误

**问题**: 即使使用 cookies 也返回 403 错误

**解决方案**:
1. 清除 yt-dlp 缓存：
   ```bash
   yt-dlp --rm-cache-dir
   ```

2. 重新导出新鲜 cookies：
   - 清除浏览器 cookies
   - 重新登录 Bilibili
   - 使用浏览器扩展导出 cookies

3. 确认视频在浏览器中可播放

参考: [workflow-guide.md - 问题 1](references/workflow-guide.md#问题-1-下载失败)

### 字幕下载失败

**问题**: 无法下载字幕或字幕为空

**解决方案**:
1. 检查可用字幕：
   ```bash
   python scripts/download_bilibili_video.py "URL" --cookies cookies.txt --list-formats
   ```

2. 尝试下载不同语言：
   ```bash
   --sub-langs danmaku,ai-zh
   ```

3. 确认视频是否有字幕：某些视频可能没有 AI 字幕

参考: [workflow-guide.md - 问题 3](references/workflow-guide.md#问题-3弹幕无法下载)

### 编码错误

**问题**: 中文字幕显示乱码

**解决方案**:
convert_srt_to_md.py 会自动检测 UTF-8 和 GBK 编码。如果仍然失败：

1. 检查文件编码：
   ```bash
   file -i subtitle.srt
   ```

2. 手动转换编码：
   ```bash
   iconv -f GBK -t UTF-8 subtitle.srt > subtitle_utf8.srt
   ```

参考: [workflow-guide.md - 编码错误](references/workflow-guide.md#问题-3编码错误)

## 高级用法

### 批量下载

创建视频 URL 列表文件：

```bash
cat > videos.txt <<EOF
https://www.bilibili.com/video/BV1xxx
https://www.bilibili.com/video/BV1yyy
https://www.bilibili.com/video/BV1zzz
EOF
```

使用 yt-dlp 批量下载：

```bash
yt-dlp --cookies ~/Downloads/bilibili_cookies.txt \
       -f "bestvideo+bestaudio" \
       -a videos.txt
```

### 批量转换字幕

假设已下载多个 .srt 文件：

```bash
for srt_file in *.srt; do
    python scripts/convert_srt_to_md.py -i "$srt_file"
done
```

### 查看可用格式

在下载前查看可用的视频格式和字幕：

```bash
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies cookies.txt \
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
```

### 仅下载字幕

如果只需要字幕，不下载视频：

```bash
python scripts/download_bilibili_video.py \
    "URL" \
    --cookies cookies.txt \
    --no-sub

# 或直接使用 yt-dlp
yt-dlp --cookies cookies.txt \
       --write-subs \
       --sub-langs ai-zh \
       --skip-download \
       "URL"
```

## 输出说明

### 文件命名

**视频文件**：
- 格式：`视频标题_视频ID_分辨率.mp4`
- 示例：`2025年终总结！..._BV1qwrHBdE15_1080p.mp4`

**字幕文件**：
- 格式：`视频标题 [视频ID].语言代码.srt`
- 示例：`2025年终总结！... [BV1qwrHBdE15].ai-zh.srt`

**Markdown 文件**：
- 格式：`视频标题.md` (或指定的输出名)
- 示例：`2025年终总结.md`

### 目录结构

默认输出目录：
```
H:\我的云端硬盘\bilibili-downloads\
├── video1_BVxxx_1080p.mp4
├── video1 [BVxxx].ai-zh.srt
├── video1_口播稿.md
├── video2_BVyyy_720p.mp4
├── video2 [BVyyy].ai-zh.srt
└── video2_口播稿.md
```

## 注意事项

### 版权和合规

- 仅下载自己有权限访问的视频
- 尊重视频创作者的版权
- 下载的内容仅供个人学习和研究使用
- 遵守 Bilibili 的服务条款

### 技术要求

- 需要有效的 Bilibili 账号
- 某些高清格式可能需要大会员才能访问
- 字幕功能取决于视频是否支持
- AI 字幕是自动生成的，可能存在错误

### 最佳实践

1. **定期更新 cookies**：cookies 会过期，建议每月更新一次
2. **检查可用格式**：在下载前使用 `--list-formats` 查看选项
3. **自动命名**：尽量使用自动生成的文件名，避免手动重命名
4. **备份 cookies**：妥善保管 cookies 文件，不要分享给他人

## 故障排除指南

如需详细的故障排除步骤，参考：[workflow-guide.md - 故障排除](references/workflow-guide.md#🔧-故障排除)

## 相关资源

- [yt-dlp 文档](https://github.com/yt-dlp/yt-dlp)
- [完整工作流指南](references/workflow-guide.md)
- [快速参考](references/quick-reference.md)

## 示例

### 示例 1: 下载单个视频并提取字幕

```bash
# 下载
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt

# 转换
python scripts/convert_srt_to_md.py \
    -i "2025年终总结！... [BV1qwrHBdE15].ai-zh.srt" \
    -o "2025年终总结.md" \
    -t "2025年终总结！同居7年，我们之间最大的分歧和变化..."
```

### 示例 2: 仅下载字幕

```bash
python scripts/download_bilibili_video.py \
    "https://www.bilibili.com/video/BV1qwrHBdE15/" \
    --cookies ~/Downloads/bilibili_cookies.txt \
    --no-sub

python scripts/convert_srt_to_md.py -i "*.srt"
```

### 示例 3: 批量处理播放列表

```bash
# 下载播放列表
yt-dlp --cookies ~/Downloads/bilibili_cookies.txt \
       -f "bestvideo+bestaudio" \
       --yes-playlist \
       "PLAYLIST_URL"

# 批量转换
for srt in *.srt; do
    python scripts/convert_srt_to_md.py -i "$srt"
done
```
