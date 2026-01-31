# 格式互换技能 - 快速入门

## 30 秒上手

### 在 Claude Code 中使用（最简单）

直接说：
```
把 "文件.md" 转成 PDF
```

就这么简单！

---

## 支持的格式转换

```
.md   →  .docx   ✅
.md   →  .pdf    ✅
.docx →  .md     ✅
.docx →  .pdf    ✅
.pdf  →  .md     ✅
.pdf  →  .docx   ✅
.txt  →  .md     ✅
.txt  →  .docx   ✅
```

---

## 常见使用场景

### 1. 写小说
```
Markdown (写作) → Word (编辑) → PDF (发布)
```

### 2. 处理 PDF
```
PDF (提取) → Markdown (编辑) → Word/PDF (输出)
```

### 3. 文档分享
```
Word (编辑) → PDF (发送)
```

---

## 命令行使用

```bash
# 基本用法
python convert.py input.md output.docx

# 指定格式
python convert.py input.md --to pdf
```

---

## 安装依赖

### Windows
双击运行：`install.bat`

### Mac/Linux
运行：`bash install.sh`

### 手动安装
```bash
pip install python-docx pdfplumber pdf2docx pypandoc
```

---

## 需要帮助？

- 完整文档：`README.md`
- 技能说明：`SKILL.md`
- 示例文件：`example.md`

---

**就这么简单！开始转换吧！** 🚀
