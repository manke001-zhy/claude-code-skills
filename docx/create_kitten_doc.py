# -*- coding: utf-8 -*-
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 创建文档
doc = Document()

# 添加标题
title = doc.add_heading('小猫咪烧鸡', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 添加副标题
doc.add_paragraph('一个关于美食与友谊的温暖故事')

# 添加章节
doc.add_heading('第一章：神秘的香味', 1)
doc.add_paragraph(
    '清晨的阳光透过窗户洒进小厨房，小猫咪Mia揉了揉眼睛，'
    '闻到了一股奇妙的香味。那不是普通的鱼干，也不是她最爱的猫罐头，'
    '而是一种她从未闻过的诱人味道。'
)

doc.add_heading('第二章：意外的发现', 1)
doc.add_paragraph(
    'Mia顺着香味来到后院，发现邻居小王正在烤制一只金黄油亮的烧鸡。'
    '那诱人的色泽和浓郁的香气让小猫咪的口水都要流下来了。'
)

doc.add_heading('第三章：友谊的开始', 1)
doc.add_paragraph(
    '小王发现了躲在墙角偷看的Mia，笑着撕下一小块鸡肉递给她。'
    '从那天起，小猫咪和小王成为了最好的朋友，'
    '每个周末都能一起分享美味的烧鸡。'
)

# 添加结尾
doc.add_paragraph(
    '有时候，最美好的友谊就藏在美食和分享之间。',
    style='Intense Quote'
)

# 添加分隔线
doc.add_paragraph('_' * 50)

# 添加作者信息
p = doc.add_paragraph()
run = p.add_run('— 这是一个温馨的小故事 —')
run.bold = True
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 保存文档
import os
desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
doc.save(os.path.join(desktop, '小猫咪烧鸡.docx'))
print('[OK] Word document created successfully!')
print(f'[Path] {os.path.join(desktop, "小猫咪烧鸡.docx")}')
