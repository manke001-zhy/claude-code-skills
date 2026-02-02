# 文字转语音（TTS）工具

> 使用微软 Edge 浏览器的语音合成技术，将文字转换为高质量的音频文件

## 快速开始

## 快速开始

### 1. 安装依赖

```bash
pip install edge-tts
```

### 2. 基本使用

```bash
# 将文本文件转换为音频
python scripts/tts.py input.txt output.mp3

# 直接转换文本
python scripts/tts.py "你好世界" output.mp3

# 使用指定的声音
python scripts/tts.py input.txt output.mp3 --voice zh-CN-XiaoyiNeural

# 调整语速
python scripts/tts.py input.txt output.mp3 --rate +20%

# 查看所有可用的中文语音
python scripts/tts.py --list-voices zh
```

## 使用 Claude 调用

更简单的方式是直接告诉 Claude：

```
把 "口播稿.txt" 转成音频
用晓晓的声音把 "文章.md" 转成 mp3
把桌面的 "稿子.txt" 转成音频，语速调快一点
```

## 常用声音

### 女声
- `zh-CN-XiaoxiaoNeural` - 晓晓（温柔，默认）
- `zh-CN-XiaoyiNeural` - 晓伊（温柔）
- `zh-CN-XiaomengNeural` - 晓梦（活泼）

### 男声
- `zh-CN-YunxiNeural` - 云希（年轻）
- `zh-CN-YunyangNeural` - 云扬（成熟）
- `zh-CN-YunjianNeural` - 云建（成熟）

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| --voice | 语音名称 | `--voice zh-CN-XiaoxiaoNeural` |
| --rate | 语速 | `--rate +20%` (加快), `--rate -10%` (减慢) |
| --pitch | 音调 | `--pitch +10Hz` (升高), `--pitch -10Hz` (降低) |
| --volume | 音量 | `--volume +10%` (增大), `--volume -50%` (减小) |

## 支持的格式

- MP3（推荐）
- WAV
- OGG

## 注意事项

1. 首次使用需要联网
2. 支持的文本格式：`.txt`, `.md`, `.rst` 等
3. 建议使用 UTF-8 编码
4. 长文本可能需要较长的转换时间

## 示例

### 将口播稿转换为音频

```bash
python scripts/tts.py "演讲稿.txt" "演讲稿.mp3"
```

### 使用男声并加快语速

```bash
python scripts/tts.py "文章.txt" "文章.mp3" \
  --voice zh-CN-YunxiNeural \
  --rate +20%
```

### 批量转换多个文件

```bash
for file in *.txt; do
  python scripts/tts.py "$file" "${file%.txt}.mp3"
done
```

## 故障排除

### 问题：转换失败

**解决方法**：
- 检查网络连接
- 确认文本文件编码为 UTF-8
- 更新 edge-tts：`pip install --upgrade edge-tts`

### 问题：音质不佳

**解决方法**：
- 尝试不同的声音（Neural 结尾的音质更好）
- 调整语速和音调参数
- 在文本中添加适当的标点符号

## 更多信息

查看 [SKILL.md](SKILL.md) 了解更多详细说明。
