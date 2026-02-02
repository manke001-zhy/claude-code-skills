# 🤖 Claude Code 技能库

> 为 Claude Code CLI 打造的强大技能集合，提升 AI 编程助手的生产力

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude-Code-purple.svg)](https://claude.com/claude-code)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black.svg)](https://github.com/manke001-zhy/claude-code-skills)

---

## 📚 目录

- [✨ 特性](#-特性)
- [🎯 技能列表](#-技能列表)
- [🚀 快速开始](#-快速开始)
- [📦 安装](#-安装)
- [⚙️ 配置](#️-配置)
- [📖 使用指南](#-使用指南)
- [🤝 贡献](#-贡献)
- [📄 许可证](#-许可证)

---

## ✨ 特性

- **🔌 即插即用**：所有技能都是独立的模块，可直接在 Claude Code 中使用
- **📝 详细文档**：每个技能都包含完整的 SKILL.md 文档
- **🛠️ 实用工具**：涵盖文档处理、视频音频、格式转换、通信等场景
- **🔒 安全设计**：敏感信息采用 `.local.json` 配置，不上传到 Git
- **🎨 可扩展**：使用 `skill-creator` 轻松创建自定义技能

---

## 🎯 技能列表

### 📄 文档处理

| 技能 | 说明 | 用途 |
|------|------|------|
| **[format-converter](./format-converter/)** | 格式转换工具 | Markdown ↔ PDF ↔ Word 互相转换 |
| **[docx](./docx/)** | Word 文档处理 | 创建、编辑、分析 .docx 文件 |
| **[pdf](./pdf/)** | PDF 处理工具 | 合并、拆分、提取 PDF 内容 |
| **[pptx](./pptx/)** | PowerPoint 处理 | 创建、编辑演示文稿 |
| **[xlsx](./xlsx/)** | Excel 处理 | 电子表格创建、编辑、数据分析 |

### 🎬 视频音频

| 技能 | 说明 | 用途 |
|------|------|------|
| **[bilibili-subtitle-extractor](./bilibili-subtitle-extractor/)** | B站字幕提取 | 下载 B站视频并提取字幕转 Markdown |
| **[ffmpeg](./ffmpeg/)** | 视频音频处理 | 格式转换、压缩、音频提取 |
| **[tts-converter](./tts-converter/)** | 语音合成 | 使用 Edge TTS 将文字转换为音频 |
| **[video-text-overlay](./video-text-overlay/)** | 视频文字叠加 | 为视频添加字幕、标题、水印 |

### 🌐 网络通信

| 技能 | 说明 | 用途 |
|------|------|------|
| **[telegram-control](./telegram-control/)** | Telegram 双向控制 | 通过 Telegram Bot 与 Claude Code 交互 |
| **[file-share](./file-share/)** | 文件邮件分享 | 通过邮箱快速分享文件到手机 |

### 🛠️ 开发工具

| 技能 | 说明 | 用途 |
|------|------|------|
| **[dev-browser](./dev-browser/)** | 浏览器自动化 | 使用 Playwright 进行浏览器操作、网页测试、自动发帖 |
| **[mcp-builder](./mcp-builder/)** | MCP 服务器构建 | 创建模型上下文协议服务器 |
| **[web-artifacts-builder](./web-artifacts-builder/)** | Web 组件构建 | 使用 React + Tailwind 构建 Web 工具 |
| **[webapp-testing](./webapp-testing/)** | Web 应用测试 | 使用 Playwright 进行浏览器测试 |

### 🤖 AI 辅助

| 技能 | 说明 | 用途 |
|------|------|------|
| **[Humanizer-zh](./Humanizer-zh/)** | AI 写作去痕 | 消除 AI 生成文本的痕迹，更自然 |
| **[self-update-ai](./self-update-ai/)** | 偏好管理 | 让 AI 记住并应用你的个人偏好 |
| **[skill-creator](./skill-creator/)** | 技能创建器 | 快速创建新技能的工具 |

### 🎨 其他

| 技能 | 说明 | 用途 |
|------|------|------|
| **[remotion](./remotion/)** | React 视频制作 | 使用 React 创建程序化视频 |

---

## 🚀 快速开始

### 前置要求

- ✅ 已安装 [Claude Code CLI](https://claude.com/claude-code)
- ✅ Python 3.8+ （部分技能需要）
- ✅ Git （用于版本管理）

### 克隆仓库

```bash
# 克隆到 Claude Code 技能目录
cd ~/.claude/skills
git clone https://github.com/manke001-zhy/claude-code-skills.git temp
mv temp/* temp/.git* .
rmdir temp
```

### 目录结构

```
~/.claude/skills/
├── README.md                    # 本文件
├── CONFIG_SETUP.md              # 详细配置说明
├── .gitignore                   # Git 忽略规则
├── format-converter/            # 格式转换技能
├── telegram-control/            # Telegram 控制技能
├── bilibili-subtitle-extractor/ # B站字幕提取
└── ...                          # 其他技能
```

---

## 📦 安装

### 方法1：手动安装（推荐）

1. **进入技能目录**
   ```bash
   cd ~/.claude/skills
   ```

2. **克隆本仓库**
   ```bash
   git clone https://github.com/manke001-zhy/claude-code-skills.git .
   ```

3. **验证安装**
   ```bash
   ls -la
   # 应该能看到所有技能文件夹
   ```

### 方法2：使用符号链接（开发模式）

如果你想在其他地方维护代码：

```bash
# 克隆到任意位置
git clone https://github.com/manke001-zhy/claude-code-skills.git ~/my-skills

# 创建符号链接
cd ~/.claude/skills
ln -s ~/my-skills/* .
```

---

## ⚙️ 配置

部分技能需要配置 API 密钥或授权码。详细的配置步骤请参考 **[CONFIG_SETUP.md](./CONFIG_SETUP.md)**

### 需要配置的技能

| 技能 | 配置内容 | 说明 |
|------|----------|------|
| **file-share** | 邮箱 SMTP 授权码 | 用于文件邮件发送 |
| **telegram-control** | Bot Token + Chat ID | Telegram Bot 令牌 |
| **telegram-control** | OpenAI API Key | LLM 调用（可选） |

### 配置示例

```bash
# 1. 复制配置模板
cp file-share/email_config.json file-share/email_config.local.json

# 2. 编辑配置文件
vim file-share/email_config.local.json

# 3. 填入真实信息（注意不要提交到 Git）
```

> ⚠️ **安全提示**：所有 `.local.json` 文件已被 `.gitignore` 排除，不会上传到 Git

---

## 📖 使用指南

### 在 Claude Code 中使用技能

Claude Code 会自动识别 `~/.claude/skills/` 目录下的所有技能。

**示例对话：**

```
你：把 test.md 转成 PDF
Claude：调用 /format-converter 技能...
```

```
你：从 B站下载视频并提取字幕
Claude：调用 /bilibili-subtitle-extractor 技能...
```

```
你：把这个文件发到我手机
Claude：调用 /file-share 技能...
```

### 查看技能文档

每个技能都有独立的 `SKILL.md` 文档：

```bash
# 查看某个技能的文档
cat format-converter/SKILL.md
cat telegram-control/SKILL.md
```

### 创建自定义技能

使用 `skill-creator` 快速创建新技能：

```bash
cd ~/.claude/skills/skill-creator/scripts
python init_skill.py --name "my-skill" --description "我的自定义技能"
```

---

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. **Fork 本仓库**
2. **创建特性分支**
   ```bash
   git checkout -b feature/my-skill
   ```
3. **提交更改**
   ```bash
   git commit -m "添加: 新技能 XXX"
   ```
4. **推送到分支**
   ```bash
   git push origin feature/my-skill
   ```
5. **创建 Pull Request**

### 贡献指南

- 遵循现有技能的目录结构
- 每个技能必须包含 `SKILL.md` 文档
- 使用 `.local.json` 处理敏感配置
- 添加必要的注释和使用示例

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🔗 相关资源

- [Claude Code 官方文档](https://claude.com/claude-code)
- [技能配置指南](./CONFIG_SETUP.md)
- [问题反馈](https://github.com/manke001-zhy/claude-code-skills/issues)

---

## 💡 技能亮点

### 📊 数据统计

- ✨ **17+** 个实用技能
- 📝 **100%** 文档覆盖率
- 🔒 **安全** 配置管理
- 🎯 **即插即用** 设计

### 🌟 特色技能

- **[telegram-control](./telegram-control/)** ⭐ 最受欢迎
  - 通过 Telegram 远程控制 Claude Code
  - 支持文件传输、命令执行、AI 对话

- **[format-converter](./format-converter/)** ⭐ 使用最多
  - 一键转换文档格式
  - 支持 Markdown、PDF、Word 互转

- **[bilibili-subtitle-extractor](./bilibili-subtitle-extractor/)** ⭐ 创意奖
  - 自动提取 B站视频字幕
  - 转换为 Markdown 方便阅读

---

## 📞 联系方式

- **作者**: zhy
- **GitHub**: [manke001-zhy](https://github.com/manke001-zhy)
- **问题反馈**: [Issues](https://github.com/manke001-zhy/claude-code-skills/issues)

---

<div align="center">

**如果觉得有用，请给一个 ⭐️ Star！**

Made with ❤️ by zhy

</div>
