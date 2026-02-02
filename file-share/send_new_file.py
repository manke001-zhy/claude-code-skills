#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import formataddr
from pathlib import Path

# 读取配置
config_path = Path(__file__).parent / 'email_config.local.json'
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

sender = config['sender']
password = config['password']
receiver = config['receiver']
email_type = config.get('type', '1')

# 新文件路径
file_path = r'C:\Users\manke\Desktop\bilibili_history_1769975079004.md'

try:
    msg = MIMEMultipart()
    msg['From'] = formataddr(["Claude Code", sender])
    msg['To'] = formataddr(["User", receiver])
    msg['Subject'] = Header('哔哩哔哩历史记录（修正版）', 'utf-8')

    body = '''
您好！

这是您的哔哩哔哩观看历史记录文档（修正版）。

本次更新：
- 修复了链接重复问题
- 使用BV号去重，确保每个视频唯一
- 包含视频标题、链接和封面

文件：bilibili_history_1769975079004.md
---
由 Claude Code 自动发送
'''
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 附件
    with open(file_path, 'rb') as f:
        part = MIMEApplication(f.read())
        part.add_header('Content-Disposition', 'attachment',
                       filename='bilibili_history_corrected.md')
        msg.attach(part)

    # 发送
    if email_type == "1":
        server = smtplib.SMTP("smtp.qq.com", 587, timeout=30)
        server.starttls()
    else:
        server = smtplib.SMTP_SSL("smtp.163.com", 465, timeout=30)

    server.login(sender, password)
    server.sendmail(sender, [receiver], msg.as_string())
    server.quit()

    print('[OK] 邮件发送成功！')
    print(f'收件人: {receiver}')
    print(f'文件: bilibili_history_1769975079004.md')

except Exception as e:
    print(f'[ERROR] {e}')
