#!/usr/bin/env python3
"""
PDF文本提取工具
从PDF文件中提取文本内容
"""

import sys
import argparse

def extract_text(pdf_path, output_file=None):
    """从PDF提取文本"""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("错误: 需要安装 pypdf 库")
        print("请运行: pip install pypdf")
        sys.exit(1)

    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    print(f"正在处理: {pdf_path}")
    print(f"总页数: {total_pages}\n")

    text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += f"--- 第{i+1}页 ---\n"
            text += page_text + "\n\n"

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"文本已保存到: {output_file}")
    else:
        print(text)

    return text

def main():
    parser = argparse.ArgumentParser(description='从PDF文件提取文本')
    parser.add_argument('pdf_file', help='PDF文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选，不指定则打印到控制台）')

    args = parser.parse_args()

    extract_text(args.pdf_file, args.output)

if __name__ == '__main__':
    main()
