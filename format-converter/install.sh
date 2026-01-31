#!/bin/bash
# 格式互换技能 - 依赖安装脚本

echo "==================================="
echo "格式互换技能 - 安装依赖"
echo "==================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 未安装"
    echo "请先安装 Python 3.7 或更高版本"
    exit 1
fi

echo "[OK] Python 已安装: $(python3 --version)"
echo ""

# 安装基础依赖
echo "安装基础依赖 (python-docx)..."
pip install python-docx

echo ""
echo "安装可选依赖..."
echo "这些依赖提供更多转换功能"
echo ""

# PDF 相关
echo "安装 PDF 处理库 (pdfplumber, pdf2docx)..."
pip install pdfplumber pdf2docx

# 通用转换
echo "安装通用转换工具 (pypandoc)..."
pip install pypandoc

echo ""
echo "==================================="
echo "安装完成！"
echo "==================================="
echo ""
echo "提示："
echo "1. 为了获得最佳转换质量，建议安装 Pandoc"
echo "   下载地址: https://pandoc.org/installing.html"
echo ""
echo "2. 使用方法："
echo "   在 Claude Code 中说: 把 [文件] 转成 [格式]"
echo "   命令行: python convert.py input.md output.docx"
echo ""
echo "3. 查看完整文档: README.md"
echo ""
