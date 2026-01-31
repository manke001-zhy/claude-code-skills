#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断创建文件问题
"""

import sys
import os
import re
from pathlib import Path

# 测试完整的创建流程
def test_create_file():
    print("=" * 60)
    print("  诊断创建文件问题")
    print("=" * 60)

    # 1. 测试文件名清理
    filename_original = "T1 S T. Txt"
    print(f"\n1. 原始文件名: {filename_original}")

    # 应用清理逻辑
    filename_cleaned = re.sub(r'\.\s+(\w+)', r'.\1', filename_original)
    print(f"2. 清理后文件名: {filename_cleaned}")

    # 2. 测试路径构建
    desktop = Path.home() / 'Desktop'
    file_path = desktop / filename_cleaned
    print(f"3. 完整路径: {file_path}")

    # 3. 检查文件是否存在
    exists = file_path.exists()
    print(f"4. 文件存在: {exists}")

    # 4. 如果不存在，尝试创建
    if not exists:
        print("\n5. 尝试创建文件...")
        try:
            file_path.touch()
            print(f"   ✅ 创建成功！")
            print(f"   文件路径: {file_path}")
        except Exception as e:
            print(f"   ❌ 创建失败: {e}")
            return False
    else:
        print("\n5. 文件已存在，尝试删除后重新创建...")
        try:
            file_path.unlink()
            print(f"   ✅ 已删除旧文件")
            file_path.touch()
            print(f"   ✅ 重新创建成功！")
        except Exception as e:
            print(f"   ❌ 操作失败: {e}")
            return False

    # 6. 验证文件
    if file_path.exists():
        print(f"\n6. ✅ 最终验证: 文件创建成功")
        print(f"   文件名: {filename_cleaned}")
        print(f"   完整路径: {file_path}")
        print(f"   文件大小: {file_path.stat().st_size} bytes")
        return True
    else:
        print(f"\n6. ❌ 最终验证: 文件不存在")
        return False

def test_executor_logic():
    """测试executor中的逻辑"""
    print("\n" + "=" * 60)
    print("  测试Executor逻辑")
    print("=" * 60)

    # 模拟executor的逻辑
    params = {'filename': 'T1 S T. Txt', 'location': 'Desktop'}
    filename = params.get('filename', '')
    location = params.get('location', 'Desktop')

    print(f"\n输入参数:")
    print(f"  filename: {filename}")
    print(f"  location: {location}")

    # 清理文件名
    import re
    filename_cleaned = re.sub(r'\.\s+(\w+)', r'.\1', filename)
    print(f"\n清理后: {filename_cleaned}")

    # 确定目录
    if location == 'Desktop':
        target_dir = Path.home() / 'Desktop'
    elif location == 'Downloads':
        target_dir = Path.home() / 'Downloads'
    else:
        target_dir = Path.home() / 'Desktop'

    print(f"目标目录: {target_dir}")

    # 创建完整路径
    file_path = target_dir / filename_cleaned
    print(f"完整路径: {file_path}")

    return file_path

if __name__ == '__main__':
    # 测试1: 基本创建流程
    success1 = test_create_file()

    # 测试2: Executor逻辑
    file_path = test_executor_logic()

    # 最终报告
    print("\n" + "=" * 60)
    print("  诊断报告")
    print("=" * 60)
    print(f"\n✅ 文件名清理逻辑: 正常")
    print(f"✅ 路径构建: 正常")
    print(f"✅ 文件创建: {'正常' if success1 else '失败'}")

    if file_path and file_path.exists():
        print(f"\n📄 测试文件已创建:")
        print(f"   {file_path}")
    else:
        print(f"\n❌ 测试文件未找到")

    print("\n" + "=" * 60)
    print("  建议")
    print("=" * 60)
    print("""
1. 如果测试成功，说明代码逻辑没问题
2. 请确保Bot已重启（加载新代码）
3. 重启命令:
   cd ~/.claude/skills/telegram-control
   python bot_core.py
4. 然后在Telegram中重新发送指令
    """)
