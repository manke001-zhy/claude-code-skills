#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将Markdown文件转换为PDF
"""

import markdown
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

def register_fonts():
    """注册中文字体"""
    # 尝试注册常见的中文字体
    font_paths = [
        'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',  # 黑体
        'C:/Windows/Fonts/simsun.ttc',  # 宋体
        'C:/Windows/Fonts/STXIHEI.TTF',  # 华文细黑
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                if font_path.endswith('.ttc'):
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                print(f'成功加载字体: {font_path}')
                return True
            except Exception as e:
                print(f'加载字体失败 {font_path}: {e}')
                continue

    print('警告: 无法加载中文字体，将使用默认字体')
    return False

def md_to_pdf(md_file, pdf_file):
    """将Markdown文件转换为PDF"""

    # 注册中文字体
    font_registered = register_fonts()

    # 读取Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 转换Markdown到HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
    )

    # 创建PDF文档
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    # 创建样式
    styles = getSampleStyleSheet()

    if font_registered:
        # 自定义样式（使用中文字体）
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontName='ChineseFont',
            fontSize=24,
            textColor='#2C3E50',
            spaceAfter=20,
            leading=32
        ))

        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontName='ChineseFont',
            fontSize=18,
            textColor='#34495E',
            spaceAfter=12,
            spaceBefore=20,
            leading=24
        ))

        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontName='ChineseFont',
            fontSize=14,
            textColor='#7F8C8D',
            spaceAfter=10,
            spaceBefore=15,
            leading=20
        ))

        styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontName='ChineseFont',
            fontSize=10,
            leading=16,
            alignment=TA_LEFT,
            spaceAfter=8
        ))

        title_style = styles['CustomTitle']
        h1_style = styles['CustomHeading1']
        h2_style = styles['CustomHeading2']
        normal_style = styles['CustomNormal']
    else:
        # 使用默认样式
        title_style = styles['Title']
        h1_style = styles['Heading1']
        h2_style = styles['Heading2']
        normal_style = styles['Normal']

    # 解析HTML并构建PDF内容
    story = []

    # 简单的HTML解析
    lines = html_content.split('\n')
    in_list = False
    list_items = []

    for line in lines:
        line = line.strip()

        if not line:
            if in_list:
                # 列表结束
                for item in list_items:
                    story.append(Paragraph(f'• {item}', normal_style))
                list_items = []
                in_list = False
            story.append(Spacer(1, 0.3*cm))
            continue

        # 处理标题
        if line.startswith('<h1>'):
            text = line.replace('<h1>', '').replace('</h1>', '')
            if story:  # 不是第一页标题
                story.append(PageBreak())
            story.append(Paragraph(text, title_style))
            story.append(Spacer(1, 0.5*cm))
            continue

        if line.startswith('<h2>'):
            text = line.replace('<h2>', '').replace('</h2>', '')
            story.append(Paragraph(text, h1_style))
            story.append(Spacer(1, 0.3*cm))
            continue

        if line.startswith('<h3>'):
            text = line.replace('<h3>', '').replace('</h3>', '')
            story.append(Paragraph(text, h2_style))
            story.append(Spacer(1, 0.2*cm))
            continue

        # 处理段落
        if line.startswith('<p>') and line.endswith('</p>'):
            text = line.replace('<p>', '').replace('</p>', '')
            # 处理粗体
            text = text.replace('<strong>', '<b>').replace('</strong>', '</b>')
            text = text.replace('<b>', '<b>').replace('</b>', '</b>')
            story.append(Paragraph(text, normal_style))
            continue

        # 处理列表
        if line.startswith('<ul>'):
            in_list = True
            continue

        if line.startswith('</ul>'):
            for item in list_items:
                story.append(Paragraph(f'• {item}', normal_style))
            list_items = []
            in_list = False
            continue

        if line.startswith('<li>') and line.endswith('</li>'):
            text = line.replace('<li>', '').replace('</li>', '')
            list_items.append(text)
            continue

        # 处理分割线
        if line.startswith('<hr />'):
            story.append(Spacer(1, 0.5*cm))
            continue

    # 构建PDF
    doc.build(story)
    print(f'PDF生成成功!')
    print(f'保存位置: {pdf_file}')

if __name__ == '__main__':
    md_file = r'C:\Users\manke\Downloads\Video\一口气讲透Meme币和A股热点炒作_口播稿_优化版.md'
    pdf_file = r'C:\Users\manke\Downloads\Video\一口气讲透Meme币和A股热点炒作_口播稿_优化版.pdf'

    md_to_pdf(md_file, pdf_file)
