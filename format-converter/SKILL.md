---
name: format-converter - 格式转换
description: 支持多种文档格式之间的相互转换，包括 Markdown (.md)、Word (.docx)、PDF (.pdf) 等格式的互相转换。用于将小说从 Markdown 转为 Word 或 PDF、将 PDF 文档转为可编辑的 Markdown、将 Word 文档转为 PDF、在不同格式之间转换文档、生成可分享或打印的文档版本
---

# 格式互换技能

## 功能说明

支持多种文档格式之间的相互转换，包括 Markdown (.md)、Word (.docx)、PDF (.pdf) 等格式的互相转换。

## 支持的格式转换

### 输入格式 → 输出格式

| 输入 | 输出 | 说明 |
|------|------|------|
| .md | .docx | Markdown 转 Word |
| .md | .pdf | Markdown 转 PDF |
| .docx | .md | Word 转 Markdown |
| .docx | .pdf | Word 转 PDF |
| .pdf | .md | PDF 转 Markdown |
| .pdf | .docx | PDF 转 Word |
| .txt | .md | 纯文本 转 Markdown |
| .txt | .docx | 纯文本 转 Word |

## 适用场景

当你需要：
- 将小说从 Markdown 转为 Word 或 PDF
- 将 PDF 文档转为可编辑的 Markdown
- 将 Word 文档转为 PDF
- 在不同格式之间转换文档
- 生成可分享或打印的文档版本

## 使用方法

### 方式1：简单命令（推荐）

直接告诉Claude：
```
把 [文件] 转成 [目标格式]
```

**示例**：
```
把 "小说.md" 转成 PDF
把 "文档.docx" 转成 Markdown
把 "报告.pdf" 转成 Word
把桌面的 "故事.md" 转成 Word 文档
```

### 方式2：指定路径

```
转换 [输入文件] 为 [输出文件]
```

**示例**：
```
转换 "C:\Users\file.md" 为 "C:\Users\output.docx"
```

### 方式3：命令行使用

```bash
# 基本用法（自动检测格式并转换）
python convert.py input.md output.docx
python convert.py input.docx output.pdf
python convert.py input.pdf output.md

# 指定输入输出格式
python convert.py --from md --to pdf input.md
```

## 转换特点

### Markdown → Word
- ✅ 标题自动转换（# ## ### → 标题样式）
- ✅ 粗体保留（**文本**）
- ✅ 列表保留（- 和 1.）
- ✅ 标题居中显示
- ✅ 段落间距优化
- ✅ 不依赖外部工具

### Markdown → PDF ✨ NEW
- ✅ 不依赖外部工具（Pandoc）
- ✅ 自动使用 Windows 中文字体（微软雅黑）
- ✅ 保留 Markdown 格式
- ✅ 生成可打印的 PDF
- ✅ 适合分享和发布
- 📦 需要：`pip install reportlab`

### Word → Markdown
- ✅ 保留标题结构
- ✅ 支持中文标题样式
- ✅ 转换为标准 Markdown 语法
- ✅ 保留文本格式
- ✅ 不依赖外部工具

### Word → PDF ✨ OPTIMIZED
- ✅ 不依赖外部工具（通过 Markdown 中转）
- ✅ 支持中文文档
- ✅ 保留基本格式
- ✅ 适合正式文档
- 📦 需要：`pip install reportlab`

### PDF → Markdown/Word
- ✅ 提取文本内容
- ✅ 保留基本结构
- ✅ 支持中文内容
- 📦 需要：`pip install pdfplumber pdf2docx`

## 技术实现

**使用工具**：
- Python 3
- python-docx（Word 文档处理）
- reportlab（PDF 生成，支持中文）
- pdfplumber（PDF 文本提取）
- pdf2docx（PDF 转 Word）
- pypandoc（可选，备用方案）

**核心优势**：
- ✅ **不依赖外部工具**：PDF 转换不需要 Pandoc 或 LibreOffice
- ✅ **中文支持**：自动注册 Windows 中文字体
- ✅ **优雅降级**：优先使用内置方法，失败时尝试备用方案
- ✅ **跨平台**：支持 Windows、Mac、Linux

## 依赖项

### 最小依赖（基础功能）
```bash
pip install python-docx
```

### 推荐依赖（完整功能）
```bash
# 基础文档处理
pip install python-docx

# PDF 生成（Markdown/Word → PDF）
pip install reportlab

# PDF 处理（PDF → Markdown/Word）
pip install pdfplumber pdf2docx
```

### 可选依赖（备用方案）
```bash
# 如果你已经有 Pandoc，可以安装 pypandoc
pip install pypandoc
```

**注意**：v2.0 版本**不需要**安装 Pandoc 或 LibreOffice，所有核心转换都可以用 Python 库完成！

## 示例

### 示例1：小说转换

**输入**：
```
把 "我的小说.md" 转成 Word 和 PDF
```

**输出**：
- `我的小说.docx`
- `我的小说.pdf`

### 示例2：PDF 提取

**输入**：
```
把 "研究报告.pdf" 转成 Markdown
```

**输出**：
- `研究报告.md`（可编辑的文本）

### 示例3：Word 分享

**输入**：
```
把 "简历.docx" 转成 PDF
```

**输出**：
- `简历.pdf`（适合邮件发送）

## 最佳实践

1. **复杂格式**：Word → PDF 使用 LibreOffice 效果最好
2. **简单快速**：使用 pypandoc 可以快速转换
3. **PDF 编辑**：PDF → Markdown → 修改 → → PDF
4. **小说创作**：Markdown 写作 → Word/PDF 发布

## 注意事项

- 确保已安装必要的依赖库
- PDF 转换可能丢失部分格式
- 复杂表格和图片需要手动调整
- 中文内容建议使用 UTF-8 编码
- 某些转换需要安装外部工具（Pandoc/LibreOffice）

## 故障排除

### 问题：ModuleNotFoundError

**错误信息**：
```
ModuleNotFoundError: No module named 'docx'
```

**解决方法**：
```bash
pip install python-docx reportlab pdfplumber pdf2docx
```

### 问题：PDF 中文显示为方块或乱码

**原因**：系统缺少中文字体

**解决方法**：
- Windows：确保安装了微软雅黑字体（通常默认有）
- Mac/Linux：需要手动指定中文字体路径

**临时方案**：转换为 Word 而不是 PDF

### 问题：Word → PDF 转换失败

**错误信息**：
```
Word to PDF failed: ...
```

**解决方法**：
1. 确保安装了 reportlab：
   ```bash
   pip install reportlab
   ```

2. 如果还是失败，分两步转换：
   ```bash
   # 先转 Markdown
   python convert.py input.docx output.md
   # 再转 PDF
   python convert.py output.md final.pdf
   ```

### 问题：PDF → Word 转换质量差

**原因**：PDF 提取可能丢失复杂格式

**解决方法**：
- 对于简单 PDF：直接转换即可
- 对于复杂 PDF（有表格、图片）：建议使用专业工具如 Adobe Acrobat
- 或者先转为 Markdown，手动调整后再转 Word

### 问题：转换速度慢

**原因**：大文件或复杂的 PDF

**解决方法**：
- 耐心等待，转换速度取决于文件大小
- Word → PDF 通过 Markdown 中转，会有额外开销
- 可以尝试使用 Pandoc（如果已安装）来提升速度
