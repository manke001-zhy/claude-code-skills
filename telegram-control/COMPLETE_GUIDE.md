# 🚀 完整启动指南

## ✅ 最简单的方式（推荐）

**双击运行**：
```
C:\Users\manke\.claude\skills\telegram-control\start_all.bat
```

这会启动：
1. AI监听器（使用GPT-4o理解）
2. Telegram Bot（接收和转发）

两个窗口会在后台运行。

## 🎯 现在支持的所有格式

### 🎬 视频格式
```
mp4, avi, mkv, mov, wmv, flv, webm
最大100MB
```

### 🎵 音频格式
```
mp3, wav, flac, aac, ogg, m4a
最大100MB
```

### 🖼️ 图片格式
```
jpg, png, gif, bmp, webp, svg
最大100MB
```

### 📄 文档格式
```
pdf, doc, docx, xls, xlsx, ppt, pptx
txt, md, csv
最大100MB
```

### 📦 其他格式
```
zip, rar, 7z, exe, 所有其他格式
最大100MB
```

## 💡 使用示例

### 发送视频
```
📎 → 选择 video.mp4 → 发送
Bot: [接收视频] 正在保存: video.mp4 (15.3MB)...
```

### 发送音乐
```
📎 → 选择 song.mp3 → 发送
Bot: [接收音频] 正在保存: song.mp3 (4.2MB)...
```

### 发送图片
```
📎 → 选择 photo.jpg → 发送
Bot: [接收图片] 正在保存: photo.jpg (1.2MB)...
```

### 文本操作
```
test.txt写入hello
读取test.txt
桌面有什么
```

## ⚡ 开机自启（可选）

### 设置开机自启
双击运行：
```
C:\Users\manke\.claude\skills\telegram-control\enable_autostart.bat
```

设置后，每次开机都会自动启动Bot系统。

**性能影响**：
- 内存占用：50-100MB
- 开机延迟：+3-5秒
- CPU占用：0%（闲置时）

### 取消开机自启
双击运行：
```
C:\Users\manke\.claude\skills\telegram-control\disable_autostart.bat
```

## 🛑 如何停止

双击运行：
```
C:\Users\manke\.claude\skills\telegram-control\stop_all.bat
```

## 🔧 如果启动失败

1. 确保安装了依赖：
```bash
pip install python-telegram-bot openai watchdog
```

2. 检查配置文件：
   - `config.json` (Telegram配置)
   - `llm_config.json` (OpenAI配置)

3. 查看日志：
   - `bot_forward.log`
   - 检查是否有错误信息

## 📊 系统架构

```
Telegram → Bot转发 → 文件请求 → AI监听器 → GPT-接收文件 → GPT-4o理解 → 执行 → 返回结果
```

## 🎉 总结

现在支持：
- ✅ 所有视频格式 (🎬)
- ✅ 所有音频格式 (🎵)
- ✅ 所有图片格式 (🖼️)
- ✅ 所有文档格式 (📄)
- ✅ 压缩包、程序等 (📦)

**最大文件大小：100MB**

**现在可以发送任何文件了！** 🚀
