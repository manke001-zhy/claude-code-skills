#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新增的声音库功能
"""

from voice_matcher import VoiceMatcher


def main():
    print("=" * 80)
    print("扩展声音库测试")
    print("=" * 80)

    # 测试角色(包含小孩和老人)
    test_characters = {
        '小宝': {'name': '小宝', 'gender': '男', 'age': '小孩', 'personality': '活泼', 'description': '小男孩'},
        '小红': {'name': '小红', 'gender': '女', 'age': '小孩', 'personality': '活泼', 'description': '小女孩'},
        '爷爷': {'name': '爷爷', 'gender': '男', 'age': '老人', 'personality': '沉稳', 'description': '老年男性'},
        '奶奶': {'name': '奶奶', 'gender': '女', 'age': '老人', 'personality': '温和', 'description': '老年女性'},
        '莱昂': {'name': '莱昂', 'gender': '男', 'age': '年轻', 'personality': '正常', 'description': '男主角'},
        '艾莉丝': {'name': '艾莉丝', 'gender': '女', 'age': '年轻', 'personality': '活泼', 'description': '公主'},
        '汤姆': {'name': '汤姆', 'gender': '男', 'age': '年轻', 'personality': '急躁', 'description': '侍从'},
        '魔王': {'name': '魔王', 'gender': '男', 'age': '成熟', 'personality': '沉稳', 'description': '魔王'},
        '国王': {'name': '国王', 'gender': '男', 'age': '成熟', 'personality': '沉稳', 'description': '国王'},
        '东北大姐': {'name': '东北大姐', 'gender': '女', 'age': '成熟', 'personality': '活泼', 'description': '东北口音'},
        '旁白': {'name': '旁白', 'gender': '旁白', 'age': '年轻', 'personality': 'normal', 'description': '旁白'}
    }

    matcher = VoiceMatcher()
    assignments = matcher.assign_voices(test_characters)

    print("\n[声音分配结果]\n")
    print("=" * 80)

    for name, info in assignments.items():
        rate_str = f" [语速{info['rate']}]" if info['rate'] != '+0%' else ""
        print(f"[角色] {name:12s}: {info['voice_description']:20s}{rate_str}")

    print("\n" + "=" * 80)
    print("\n[新增声音说明]")
    print("-" * 80)
    print("[小孩声音]")
    print("   - 小男孩: 使用云希(年轻男声) + 30%快语速")
    print("   - 小女孩: 使用晓晓(年轻女声) + 30%快语速")
    print("\n[老人声音]")
    print("   - 老年男性: 使用云健(成熟男声) - 20%慢语速")
    print("   - 老年女性: 使用晓伊(成熟女声) - 20%慢语速")
    print("\n[方言声音]")
    print("   - 东北口音: 晓北(豪爽女性)")
    print("   - 陕西口音: 晓尼(西北女性)")
    print("=" * 80)


if __name__ == '__main__':
    main()
