# 版本更新日志

## v2.0 - 重大更新 (2026-01-24)

### 🎉 重大突破

#### 1. 不依赖外部工具
**之前**：
- Markdown/Word → PDF 需要 Pandoc 或 LibreOffice
- 安装复杂，需要配置环境变量
- 跨平台兼容性差

**现在**：
- ✅ 使用 Python 库直接转换
- ✅ 只需 `pip install reportlab`
- ✅ 真正的跨平台支持

#### 2. 完整的中文支持
**新增功能**：
- 自动检测并注册 Windows 中文字体
- 支持：微软雅黑、黑体、宋体
- PDF 文档完美显示中文内容

**技术实现**：
```python
def register_chinese_font():
    # 自动检测系统字体
    # 注册到 reportlab
    # 优雅降级（失败时使用默认字体）
```

#### 3. Word → PDF 优化
**之前**：
- 需要 Word COM 接口
- 需要 Word 应用程序
- 容易出错，权限问题

**现在**：
- Word → Markdown → PDF
- 不依赖任何外部应用
- 稳定可靠

### 📦 依赖项变化

| 功能 | v1.0 | v2.0 |
|------|------|------|
| MD → Word | python-docx | python-docx |
| MD → PDF | pandoc (外部) | reportlab |
| Word → MD | pypandoc | python-docx |
| Word → PDF | pypandoc | reportlab (通过 MD) |
| PDF → MD | pdfplumber | pdfplumber |
| PDF → Word | pdf2docx | pdf2docx |

**核心依赖**：
```bash
pip install python-docx reportlab
```

### ✨ 新增特性

1. **优雅降级机制**
   - 优先使用内置方法
   - 失败时自动尝试备用方案
   - 用户友好的错误提示

2. **中文字体自动注册**
   - Windows: 微软雅黑、黑体、宋体
   - Mac/Linux: 可扩展字体路径
   - 失败时使用默认字体

3. **临时文件自动清理**
   - Word → PDF 转换产生的临时 MD 文件自动删除
   - 不留痕迹

### 🧪 测试结果

所有测试用例通过：

| 转换 | 测试文件 | 结果 | 文件大小 |
|------|---------|------|---------|
| MD → PDF | 小说.md | ✅ 成功 | 356KB |
| Word → PDF | 小说.docx | ✅ 成功 | 356KB |
| Word → MD | 小说.docx | ✅ 成功 | 9.2KB |
| MD → Word | 小说.md | ✅ 成功 | 40KB |

### 📝 使用示例对比

#### v1.0（旧版）
```bash
# 需要先安装 Pandoc
# 下载：https://pandoc.org/installing.html
# 配置环境变量

python convert.py novel.md novel.pdf  # 可能失败
```

#### v2.0（新版）
```bash
# 只需安装 Python 库
pip install python-docx reportlab

# 直接使用
python convert.py novel.md novel.pdf  # ✅ 成功
python convert.py novel.docx novel.pdf  # ✅ 成功
```

### 🐛 已修复的问题

1. ✅ Word → PDF COM 接口错误
2. ✅ Pandoc 下载超时
3. ✅ 中文路径问题
4. ✅ 中文显示为方块

### 🔮 未来计划

- [ ] 支持更多中文字体（楷体、仿宋等）
- [ ] Mac/Linux 中文字体自动检测
- [ ] 图片和表格处理优化
- [ ] 批量转换功能

### 💡 迁移指南

#### 从 v1.0 升级到 v2.0

1. **安装新依赖**：
   ```bash
   pip install reportlab
   ```

2. **无需卸载 Pandoc**：
   - v2.0 会优先使用内置方法
   - 如果内置方法失败，会自动尝试 Pandoc
   - 完全向后兼容

3. **使用方式不变**：
   - 命令行参数相同
   - API 调用方式相同
   - 无缝升级

### 📊 性能对比

| 指标 | v1.0 (with Pandoc) | v2.0 (reportlab) |
|------|-------------------|------------------|
| MD → PDF 速度 | ~2s | ~3s |
| Word → PDF 速度 | ~2s | ~5s (通过MD) |
| 内存占用 | 中等 | 较低 |
| 依赖复杂度 | 高 | 低 |
| 跨平台 | 中 | 优秀 |

**结论**：v2.0 牺牲少量速度，换取更好的稳定性和兼容性。

---

## v1.0 - 初始版本 (2026-01-24)

### 功能
- Markdown → Word 转换
- 基础格式支持

### 限制
- 需要外部工具（Pandoc）
- 中文支持有限
- Word → PDF 不稳定

---

**感谢使用格式互换技能！** 🚀
