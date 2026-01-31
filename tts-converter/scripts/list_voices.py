#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出所有可用的中文TTS声音
"""

import edge_tts
import asyncio


async def list_chinese_voices():
    """列出所有中文声音"""
    voices = await edge_tts.list_voices()
    zh_voices = [v for v in voices if v['Locale'].startswith('zh-CN')]

    print(f"\n共找到 {len(zh_voices)} 个中文声音:\n")
    print("=" * 80)

    for v in sorted(zh_voices, key=lambda x: x['Name']):
        print(f"名称: {v['Name']}")
        print(f"描述: {v['FriendlyName']}")
        print(f"性别: {v.get('Gender', '未知')}")
        print("-" * 80)

    print("\n按声音名称分组:\n")
    print("=" * 80)

    # 按声音类型分组
    categories = {
        '男声': [],
        '女声': [],
        '其他': []
    }

    for v in zh_voices:
        gender = v.get('Gender', '未知')
        if gender == 'Male':
            categories['男声'].append(v)
        elif gender == 'Female':
            categories['女声'].append(v)
        else:
            categories['其他'].append(v)

    for category, voice_list in categories.items():
        if voice_list:
            print(f"\n{category} ({len(voice_list)}个):")
            for v in sorted(voice_list, key=lambda x: x['Name']):
                print(f"  - {v['Name']}: {v['FriendlyName']}")


if __name__ == '__main__':
    asyncio.run(list_chinese_voices())
