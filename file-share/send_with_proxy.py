#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送文件到邮箱（支持代理）
"""

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

# 文件路径
file_path = r'C:\Users\manke\Desktop\bilibili_history_20260202_0334.md'

print('=' * 50)
print('  文件邮件发送工具')
print('=' * 50)
print()

# SMTP配置
if email_type == "1":  # QQ邮箱
    smtp_server = "smtp.qq.com"
    smtp_port = 587
    use_tls = True
elif email_type == "2":  # 163邮箱
    smtp_server = "smtp.163.com"
    smtp_port = 465
    use_ssl = True
else:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    use_tls = True

try:
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = formataddr(["Claude Code", sender])
    msg['To'] = formataddr(["User", receiver])
    msg['Subject'] = Header('哔哩哔哩历史记录', 'utf-8')

    # 邮件正文
    body = '''
您好！

这是您的哔哩哔哩观看历史记录文档。

文件信息：
- 文件名：bilibili_history_20260202_0334.md
- 内容：前5条观看历史记录
- 包含视频标题和链接

---
由 Claude Code 自动发送
'''
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 添加附件
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            part = MIMEApplication(f.read())
            part.add_header('Content-Disposition', 'attachment',
                           filename='bilibili_history_20260202_0334.md')
            msg.attach(part)
        print(f'[OK] 找到文件: {os.path.basename(file_path)}')
    else:
        print(f'[ERROR] 文件不存在: {file_path}')
        exit(1)

    # 连接SMTP服务器
    print(f'[*] 正在连接 {smtp_server}:{smtp_port}...')

    if use_tls:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.starttls()
    else:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)

    # 登录
    print('[*] 正在登录...')
    server.login(sender, password)

    # 发送
    print('[*] 正在发送邮件...')
    server.sendmail(sender, [receiver], msg.as_string())
    server.quit()

    print()
    print('=' * 50)
    print('  [OK] 邮件发送成功！')
    print('=' * 50)
    print(f'收件人: {receiver}')
    print(f'附件: bilibili_history_20260202_0334.md')
    print()

except Exception as e:
    print()
    print('=' * 50)
    print('  [ERROR] 发送失败')
    print('=' * 50)
    print(f'错误信息: {e}')
    print()
    print('可能的原因：')
    print('1. 网络连接问题')
    print('2. SMTP授权码错误')
    print('3. 邮箱服务器限制')
    print('4. 需要使用代理')
    print()
