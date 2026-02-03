#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"发送微博热搜文档到邮箱"
import os
import smtplib
import json
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import formataddr
from pathlib import Path

"读取配置"
config_path = Path(__file__).parent / 'email_config.local.json'
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

sender = config['sender']
password = config['password']
receiver = config['receiver']
email_type = config.get('type', '1')

"获取文件路径参数"
if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    file_path = r'C:\Users\manke\Desktop\weibo_hot_search.md'

try:
    "检查文件是否存在"
    if not os.path.exists(file_path):
        print(f'[ERROR] 文件不存在: {file_path}')
        sys.exit(1)

    "创建邮件"
    msg = MIMEMultipart()
    msg['From'] = formataddr(["编剧小助理", sender])
    msg['To'] = formataddr(["导演", receiver])
    msg['Subject'] = Header('微博热搜榜日报 - 2026-02-03', 'utf-8')

    body = '''
导演您好！

这是今天的微博热搜榜日报。

报告包含：
- 今日热搜TOP 10
- 每条热搜的详细解读
- 热度标签和剧情简介

祝您创作愉快！

---
编剧小助理 自动发送
'''
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    "添加附件"
    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        part = MIMEApplication(f.read())
    part.add_header('Content-Disposition', 'attachment',
                   filename=Header(filename, 'utf-8').encode())
    msg.attach(part)

    "发送邮件"
    print(f'[*] 正在连接邮件服务器...')
    if email_type == "1":
        server = smtplib.SMTP("smtp.qq.com", 587, timeout=30)
        server.starttls()
    else:
        server = smtplib.SMTP_SSL("smtp.163.com", 465, timeout=30)

    print('[*] 正在登录...')
    server.login(sender, password)

    print('[*] 正在发送邮件...')
    server.sendmail(sender, [receiver], msg.as_string())
    server.quit()

    print('')
    print('[OK] 邮件发送成功！')
    print(f'收件人: {receiver}')
    print(f'文件: {filename}')
    print('')

except Exception as e:
    print(f'[ERROR] 发送失败: {e}')
    import traceback
    traceback.print_exc()
