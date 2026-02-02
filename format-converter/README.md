# 格式互换技能 - 通用文档格式转换工具 v2.0

> 支持 Markdown、Word、PDF 等多种格式的互相转换

**✨ v2.0 新特性**：
- ✅ **不依赖外部工具**：PDF 转换不需要 Pandoc/LibreOffice
- ✅ **中文支持**：自动使用 Windows 中文字体
- ✅ **优雅降级**：优先内置方法，失败时尝试备用方案

## 快速开始

### 在 Claude Code 中使用（推荐）

直接告诉 Claude：
```
把 [文件] 转成 [目标格式]
```

**示例**：
```
把 "小说.md" 转成 PDF
把 "文档.docx" 转成 Markdown
把 "报告.pdf" 转成 Word
```

### 命令行使用

```bash
# 基本用法
python convert.py input.md output.docx    # Markdown -> Word
python convert.py input.docx output.pdf   # Word -> PDF
python convert.py input.pdf output.md     # PDF -> Markdown

# 指定输出格式
python convert.py input.md --to pdf
```

## 支持的转换

| 输入格式 | 输出格式 | 状态 |
|---------|---------|------|
| .md | .docx | ✅ 完整支持 |
| .md | .pdf | ✅ 完整支持 |
| .docx | .md | ✅ 完整支持 |
| .docx | .pdf | ✅ 完整支持 |
| .pdf | .md | ✅ 完整支持 |
| .pdf | .docx | ✅ 完整支持 |
| .txt | .md | ✅ 完整支持 |
| .txt | .docx | ✅ 完整支持 |

## 功能特点

### Markdown → Word
- ✅ 标题自动转换（# ## ### → 标题样式）
- ✅ 主标题居中显示
- ✅ 粗体保留（**文本**）
- ✅ 列表支持（- 和 1.）
- ✅ 分隔线处理（---）
- ✅ 段落间距优化

### Markdown → PDF
- ✅ 保留 Markdown 格式
- ✅ 生成可打印 PDF
- ✅ 适合分享和发布

### Word → Markdown
- ✅ 保留标题结构
- ✅ 转换为标准 Markdown
- ✅ 保留文本内容

### PDF → Markdown/Word
- ✅ 提取文本内容
- ✅ 保留基本结构
- ✅ 支持中文

### Word → PDF
- ✅ 保留 Word 格式
- ✅ 生成标准 PDF
- ✅ 适合正式文档

## 安装依赖

### 基础依赖（必需）

```bash
pip install python-docx
```

### 完整依赖（推荐）

```bash
# 基础功能
pip install python-docx

# PDF 生成（Markdown/Word → PDF）
pip install reportlab

# PDF 处理（PDF → Markdown/Word）
pip install pdfplumber pdf2docx
```

### 一键安装（推荐）

**Windows**：
```bash
# 双击运行
install.bat
```

**Mac/Linux**：
```bash
bash install.sh
```

**手动安装**：
```bash
pip install python-docx reportlab pdfplumber pdf2docx
```

**重要**：v2.0 版本**不需要**安装 Pandoc 或 LibreOffice！

## 使用示例

### 示例 1：小说发布

将 Markdown 小说转换为多种格式：

```bash
# 转为 Word（可编辑）
python convert.py novel.md novel.docx

# 转为 PDF（可分享）
python convert.py novel.md novel.pdf
```

### 示例 2：PDF 编辑

从 PDF 提取内容，修改后再转换回 PDF：

```bash
# PDF -> Markdown
python convert.py report.pdf report.md

# 编辑 report.md...

# Markdown -> PDF
python convert.py report.md report_updated.pdf
```

### 示例 3：Word 文档分享

将 Word 文档转为 PDF 以便分享：

```bash
python convert.py resume.docx resume.pdf
```

## 命令行参数

```
usage: convert.py [-h] [--to OUTPUT_FORMAT] input [output]

positional arguments:
  input                 输入文件路径
  output                输出文件路径（可选）

optional arguments:
  -h, --help            显示帮助信息
  --to OUTPUT_FORMAT    输出格式 (md, docx, pdf, txt)
```

## 最佳实践

### 1. 小说创作流程

```
Markdown (写作) → Word (编辑) → PDF (发布)
```

### 2. PDF 文档处理

```
PDF (提取) → Markdown (编辑) → PDF/Word (输出)
```

### 3. 格式选择

- **写作/编辑**：Markdown 或 Word
- **分享/打印**：PDF
- **版本控制**：Markdown
- **正式文档**：Word 或 PDF

## 故障排除

### 问题：ModuleNotFoundError

**错误信息**：
```
ModuleNotFoundError: No module named 'docx'
```

**解决方法**：
```bash
pip install python-docx pdfplumber pdf2docx pypandoc
```

### 问题：pandoc not found

**错误信息**：
```
Pandoc not found. Installing pandoc...
```

**解决方法**：
1. 下载 Pandoc：https://pandoc.org/installing.html
2. 安装后重新运行转换

### 问题：中文乱码

**解决方法**：
- 确保源文件是 UTF-8 编码
- 在文本编辑器中另存为 UTF-8 格式

### 问题：PDF 转换质量差

**原因**：PDF 提取可能丢失格式

**解决方法**：
- 对于复杂文档，使用专业 PDF 工具
- 或先转为 Markdown 再手动调整格式

## 技术实现

**核心库**：
- `python-docx` - Word 文档处理
- `pypandoc` - 通用文档转换
- `pdfplumber` - PDF 文本提取
- `pdf2docx` - PDF 转 Word

**语言**：Python 3.7+

**编码**：UTF-8

## 更新日志

### v2.0 (2026-01-24) - 重大更新 ✨

**核心改进**：
- ✨ **不依赖外部工具**：Markdown/Word → PDF 不再需要 Pandoc
- ✨ **中文支持**：自动注册 Windows 中文字体（微软雅黑）
- ✨ **优雅降级**：优先使用内置方法，失败时尝试备用方案
- ✨ **Word → PDF 优化**：通过 Markdown 中转，无需 COM 接口

**新增功能**：
- ✅ Markdown → PDF（使用 reportlab）
- ✅ Word → PDF（自动通过 Markdown 中转）
- ✅ Word → Markdown（支持中文标题样式）

**技术升级**：
- 📦 核心依赖：`python-docx` + `reportlab`
- 🔧 备用方案：支持 `pypandoc`（如果已安装）
- 🌍 跨平台支持：Windows/Mac/Linux

**文档优化**：
- 📝 完善故障排除指南
- 🎯 添加详细的使用示例
- 💡 优化最佳实践说明

### v1.0 (2026-01-24)
- 🎉 首次发布
- ✅ 支持 Markdown → Word

## 贡献

欢迎提交问题和改进建议！

## 许可

MIT License
