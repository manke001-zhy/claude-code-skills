#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色识别工具 - 改进版
使用更智能的算法识别小说中的角色
"""

import re
import json
from collections import defaultdict
from pathlib import Path


def extract_potential_names(text):
    """
    提取潜在的角色名

    规则：
    1. 2-4个字符
    2. 可能是中日韩人名
    3. 排除常见非角色词
    """
    # 常见非角色词
    exclude_words = {
        '这个', '那个', '什么', '怎么', '因为', '所以', '但是', '不过',
        '而且', '然后', '接着', '最后', '另外', '此外', '总之', '因此',
        '感觉', '觉得', '发现', '看到', '听到', '知道', '明白', '理解',
        '开始', '结束', '继续', '停止', '时候', '地方', '东西', '事情',
        '问题', '办法', '可能', '应该', '能够', '可以', '需要', '想要',
        '非常', '特别', '十分', '相当', '比较', '有点', '一些', '一般',
        '一下', '一直', '一起', '已经', '还是', '或者', '虽然', '如果',
        '只有', '只要', '无论', '不管', '即使', '哪怕', '尽管', '然而',
        '后来', '之前', '以后', '之前', '现在', '今天', '昨天', '明天',
        '突然', '立刻', '马上', '赶紧', '连忙', '急忙', '慢慢', '渐渐',
        '完全', '彻底', '确实', '实在', '真正', '其实', '毕竟', '到底',
        '我知', '你知', '他知', '不知', '深知', '深知', '须知', '据悉',
    }

    # 提取对话和说话人
    lines = text.split('\n')
    potential_names = defaultdict(int)

    for line in lines:
        # 查找对话
        dialogue_pattern = r'[「『]([^「」『』]+)[」』]'
        dialogues = re.findall(dialogue_pattern, line)

        if not dialogues:
            continue

        # 查找说话人：XX说、XX道、XX问等
        speaker_patterns = [
            r'(\w{2,4})(说|道|问|喊|笑道|解释|补充|嘟囔|回答)',
            r'(\w{2,4})(?:，)(?:说|道|问)',
        ]

        for pattern in speaker_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                name = match[0] if isinstance(match, tuple) else match
                if name and name not in exclude_words and len(name) >= 2:
                    potential_names[name] += 1

    # 只保留出现2次以上的
    return {name: count for name, count in potential_names.items() if count >= 2}


def infer_gender_from_context(text, name):
    """
    从上下文推断角色性别

    返回: (性别, 置信度)
    """
    # 查找名字前后的代词
    patterns = [
        rf'{{0,20}}{name}{{0,20}}([他她])',
        rf'([他她]){{0,20}}{name}{{0,20}}',
    ]

    female_count = 0
    male_count = 0

    for pattern in patterns:
        matches = re.findall(pattern.format(name=name), text)
        for match in matches:
            if '她' in match:
                female_count += 1
            elif '他' in match:
                male_count += 1

    # 判断
    if female_count > male_count * 2:
        return '女', '高'
    elif male_count > female_count * 2:
        return '男', '高'
    elif female_count > male_count:
        return '女', '中'
    elif male_count > female_count:
        return '男', '中'
    else:
        return '未知', '低'


def analyze_novel(text):
    """
    分析小说文本，提取角色信息

    返回: 角色字典
    """
    print("=" * 60)
    print("开始分析小说...")
    print("=" * 60)

    # 提取潜在角色名
    potential_names = extract_potential_names(text)

    print(f"\n找到 {len(potential_names)} 个潜在角色：")
    for name, count in sorted(potential_names.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {name}: {count}次")

    # 创建角色对象
    characters = {}

    for name, count in sorted(potential_names.items(), key=lambda x: x[1], reverse=True):
        # 推断性别
        gender, confidence = infer_gender_from_context(text, name)

        characters[name] = {
            'name': name,
            'dialogue_count': count,
            'gender': gender,
            'gender_confidence': confidence
        }

    # 添加主角（我）
    protagonist_gender = '男'
    text_sample = text[:1000]

    if '她' in text_sample and text_sample.count('她') > text_sample.count('他'):
        protagonist_gender = '女'

    characters['我（旁白）'] = {
        'name': '我（旁白）',
        'dialogue_count': 0,
        'gender': protagonist_gender,
        'gender_confidence': '高',
        'is_protagonist': True
    }

    return characters


def main():
    if len(sys.argv) < 2:
        print("用法: python analyze_characters.py <小说文件路径>")
        sys.exit(1)

    input_file = sys.argv[1]

    print(f"[INFO] 读取文件: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"[INFO] 文本长度: {len(text)} 字符")

    # 分析
    characters = analyze_novel(text)

    # 显示结果
    print("\n" + "=" * 60)
    print("角色识别结果")
    print("=" * 60)

    for name, char in characters.items():
        protagonist_flag = " [主角]" if char.get('is_protagonist') else ""
        print(f"\n角色: {name}{protagonist_flag}")
        print(f"  对话次数: {char['dialogue_count']}")
        print(f"  性别: {char['gender']} (置信度: {char['gender_confidence']})")

    # 保存配置
    output_file = Path(input_file).stem + '_角色配置_改进版.json'

    # 转换为TTS配置格式
    tts_config = {
        'characters': {}
    }

    voice_map = {
        '男': 'zh-CN-YunxiNeural',
        '女': 'zh-CN-XiaoxiaoNeural',
        '未知': 'zh-CN-XiaoxiaoNeural'
    }

    for name, char in characters.items():
        tts_config['characters'][name] = {
            'name': name,
            'gender': char['gender'],
            'age': '年轻',
            'voice': voice_map.get(char['gender'], 'zh-CN-XiaoxiaoNeural')
        }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tts_config, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"配置已保存到: {output_file}")
    print("=" * 60)


if __name__ == '__main__':
    import sys
    main()
