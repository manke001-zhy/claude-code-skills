#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件邮件发送工具
支持多种邮箱服务商，交互式配置
"""

import os
import smtplib
import sys
import argparse
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import formataddr
import getpass

# 预设配置
DEFAULT_FILE = r"C:\Users\manke\Desktop\长江之谜.md"
DEFAULT_RECEIVER = "manke_zhy@qq.com"
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "email_config.json")

# SMTP配置
SMTP_CONFIGS = {
    "1": {
        "name": "QQ邮箱",
        "server": "smtp.qq.com",
        "port": 587,
        "use_tls": True
    },
    "2": {
        "name": "163邮箱",
        "server": "smtp.163.com",
        "port": 465,
        "use_tls": False,
        "use_ssl": True
    },
    "3": {
        "name": "Gmail",
        "server": "smtp.gmail.com",
        "port": 587,
        "use_tls": True
    },
    "4": {
        "name": "其他",
        "custom": True
    }
}


def get_file_size(file_path):
    """获取文件大小"""
    size = os.path.getsize(file_path)
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f}KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f}MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f}GB"


def check_file(file_path):
    """检查文件是否存在和大小"""
    if not os.path.exists(file_path):
        print(f"[错误] 文件不存在 - {file_path}")
        return False

    size = os.path.getsize(file_path)
    size_mb = size / (1024 * 1024)

    if size_mb > 50:
        print(f"[警告] 文件大小 {get_file_size(file_path)}，超过50MB限制")
        print("[提示] 这可能导致发送失败")
        return False

    print(f"[OK] 找到文件：{os.path.basename(file_path)} ({get_file_size(file_path)})")
    return True


def create_email(sender, receiver, subject, file_path):
    """创建邮件对象"""
    msg = MIMEMultipart()
    msg['From'] = formataddr(["文件发送工具", sender])
    msg['To'] = formataddr(["收件人", receiver])
    msg['Subject'] = Header(subject, 'utf-8')

    # 邮件正文
    body = f"""您好！

这是通过文件发送工具发送的邮件。

文件信息：
- 文件名：{os.path.basename(file_path)}
- 文件大小：{get_file_size(file_path)}

如有问题，请忽略此邮件。

---
由Claude Code文件分享工具发送
"""

    msg.attach(MIMEText(body.strip(), 'plain', 'utf-8'))

    # 添加附件
    with open(file_path, 'rb') as f:
        part = MIMEApplication(f.read())

    # 处理附件文件名（支持中文）
    filename = os.path.basename(file_path)
    part.add_header('Content-Disposition', 'attachment',
                    filename=Header(filename, 'utf-8').encode())

    msg.attach(part)

    return msg


def send_email(msg, sender, password, smtp_config, receiver):
    """发送邮件"""
    server = smtp_config['server']
    port = smtp_config['port']
    use_tls = smtp_config.get('use_tls', False)
    use_ssl = smtp_config.get('use_ssl', False)

    print(f"\n[*] 正在连接 {smtp_config['name']} SMTP服务器 ({server}:{port})...")

    try:
        if use_ssl:
            # SSL连接（如163邮箱）
            smtp = smtplib.SMTP_SSL(server, port)
        else:
            # 普通连接
            smtp = smtplib.SMTP(server, port)
            if use_tls:
                # 启动TLS加密
                smtp.starttls()

        # 登录
        print("[*] 正在验证发件邮箱...")
        smtp.login(sender, password)

        # 发送
        print("[*] 正在发送邮件...")
        smtp.send_message(msg)

        # 关闭
        smtp.quit()

        print("\n[SUCCESS] 发送成功！请检查收件箱（可能需要稍等片刻）")
        print(f"[SUCCESS] 收件人：{receiver}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("\n[ERROR] 认证失败！")
        print("[提示] 请检查：")
        print("  1. 授权码是否正确")
        print("  2. IMAP/SMTP服务是否已开启")
        print("  3. 发件邮箱地址是否正确")
        return False

    except smtplib.SMTPException as e:
        print(f"\n[ERROR] SMTP错误：{e}")
        return False

    except Exception as e:
        print(f"\n[ERROR] 发送失败：{e}")
        return False


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def main():
    """主函数（命令行版本）"""
    # 加载默认配置
    config = load_config()

    parser = argparse.ArgumentParser(description='文件邮件发送工具')
    parser.add_argument('--file', default=DEFAULT_FILE, help='要发送的文件路径')
    parser.add_argument('--receiver', default=config.get('receiver', DEFAULT_RECEIVER), help='收件人邮箱')
    parser.add_argument('--sender', default=config.get('sender', ''), help='发件邮箱地址')
    parser.add_argument('--password', default=config.get('password', ''), help='SMTP授权码')
    parser.add_argument('--type', default=config.get('type', '1'), choices=['1', '2', '3', '4'],
                       help='邮箱类型：1=QQ, 2=163, 3=Gmail, 4=其他')

    args = parser.parse_args()

    # 如果没有配置发件人和密码，提示错误
    if not args.sender or not args.password:
        print("[ERROR] 未配置发件邮箱或授权码")
        print("[提示] 请编辑 email_config.json 文件，添加您的邮箱配置")
        return 1

    print("=" * 50)
    print("  文件邮件发送工具 v1.0")
    print("  由Claude Code提供支持")
    print("=" * 50)
    print(f"[INFO] 发件人：{args.sender}")
    print(f"[INFO] 收件人：{args.receiver}")

    # 获取SMTP配置
    smtp_config = SMTP_CONFIGS[args.type]

    # 检查文件
    if not check_file(args.file):
        return 1

    # 邮件主题
    filename = os.path.basename(args.file)
    subject = f"文件分享：{filename}"

    # 创建邮件
    print("\n[*] 正在创建邮件...")
    msg = create_email(args.sender, args.receiver, subject, args.file)

    # 发送邮件
    success = send_email(msg, args.sender, args.password, smtp_config, args.receiver)

    if success:
        print("\n" + "=" * 50)
        print("[SUCCESS] 任务完成！")
        print("=" * 50)
        return 0
    else:
        print("\n发送失败，请检查配置后重试")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 发生错误：{e}")
        sys.exit(1)
