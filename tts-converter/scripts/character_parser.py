#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色信息解析模块
从脚本中识别和解析角色特征（年龄、性别、性格）
"""

import re
from typing import Dict, List, Tuple


class CharacterParser:
    """角色信息解析器"""

    # 年龄识别关键词
    AGE_KEYWORDS = {
        '年轻': ['少年', '青年', '年轻', '少女', '女孩', '男孩', '小姐', '见习', '学生'],
        '成熟': ['成年', '成熟', '青年', '二十', '三十'],
        '中年': ['中年', '中年人', '大叔', '阿姨', '国王', '女王', '父亲', '母亲']
    }

    # 女性识别关键词（按优先级）
    FEMALE_KEYWORDS = ['女主角', '她', '公主', '女王', '少女', '女孩', '小姐', '艾莉丝', '艾米', '星空', '母亲']

    # 男性识别关键词（按优先级）
    MALE_KEYWORDS = ['男主角', '他', '骑士', '王子', '国王', '魔王', '少年', '男孩', '莱昂', '汤姆', '和也', '父亲']

    # 性格识别关键词
    PERSONALITY_KEYWORDS = {
        '急躁': ['急躁', '热血', '冲动', '急切', '火爆', '正义感过剩'],
        '沉稳': ['沉稳', '冷静', '成熟', '稳重', '优雅', '疲惫', '温柔'],
        '活泼': ['活泼', '开朗', '欢快', '愉快', '兴奋', '天真']
    }

    def __init__(self):
        """初始化解析器"""
        pass

    def parse_script(self, script_text: str) -> Dict:
        """
        解析脚本，提取角色信息

        Args:
            script_text: 脚本文本内容

        Returns:
            {
                'characters': Dict[str, Dict],  # 角色信息字典
                'role_list_start': int,        # 角色列表起始行号
                'role_list_end': int            # 角色列表结束行号
            }
        """
        lines = script_text.split('\n')

        # 识别角色列表区域
        role_start, role_end = self._identify_role_list(lines)

        if role_start == -1:
            # 没有找到角色列表
            return {
                'characters': {},
                'role_list_start': -1,
                'role_list_end': -1
            }

        # 提取角色信息
        characters = self._extract_characters(lines[role_start:role_end + 1])

        return {
            'characters': characters,
            'role_list_start': role_start,
            'role_list_end': role_end
        }

    def _identify_role_list(self, lines: List[str]) -> Tuple[int, int]:
        """
        识别角色列表的起止位置

        Args:
            lines: 脚本行列表

        Returns:
            (起始行号, 结束行号)，找不到则返回(-1, -1)
        """
        role_start = -1
        role_end = -1

        # 角色列表可能的标题（支持markdown加粗格式）
        role_list_patterns = [
            r'^#+\s*\*{0,2}\s*角色列表\s*\*{0,2}',
            r'^#+\s*\*{0,2}\s*人物\s*\*{0,2}',
            r'^#+\s*\*{0,2}\s*角色设定\s*\*{0,2}',
            r'^#+\s*\*{0,2}\s*Cast\s*\*{0,2}',
            r'^#+\s*\*{0,2}\s*角色介绍\s*\*{0,2}'
        ]

        # 查找角色列表标题
        for i, line in enumerate(lines):
            line = line.strip()

            for pattern in role_list_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    role_start = i
                    break

            if role_start != -1:
                break

        if role_start == -1:
            return (-1, -1)

        # 查找角色列表结束位置
        # 通常是遇到第一个空行后，接一个对话行
        in_role_list = True
        found_gap = False

        for i in range(role_start + 1, len(lines)):
            line = lines[i].strip()

            # 空行
            if not line:
                found_gap = True
                continue

            # 如果已经找到过空行，现在遇到对话，说明角色列表结束
            if found_gap and re.match(r'^【.+?】.+$', line):
                role_end = i - 1
                break

            # 如果遇到新的章节标题，角色列表结束
            if re.match(r'^#+\s', line) and '角色' not in line:
                role_end = i - 1
                break

        # 如果没找到明确结束位置，到文件末尾
        if role_end == -1:
            role_end = len(lines) - 1

        return (role_start, role_end)

    def _extract_characters(self, role_lines: List[str]) -> Dict[str, Dict]:
        """
        从角色列表行中提取角色信息

        Args:
            role_lines: 角色列表区域的行

        Returns:
            角色信息字典 {角色名: {gender, age, personality, description}}
        """
        characters = {}

        for line in role_lines:
            line = line.strip()

            # 匹配【角色名】描述格式
            match = re.match(r'^【(.+?)】(.+)$', line)
            if not match:
                continue

            name = match.group(1).strip()
            description = match.group(2).strip()

            # 解析角色特征
            char_info = self._parse_character_info(name, description)

            characters[name] = char_info

        return characters

    def _parse_character_info(self, name: str, description: str) -> Dict:
        """
        解析单个角色的特征

        Args:
            name: 角色名
            description: 角色描述

        Returns:
            {gender, age, personality, description}
        """
        # 解析性别
        gender = self._identify_gender(name, description)

        # 解析年龄
        age = self._identify_age(description)

        # 解析性格
        personality = self._identify_personality(description)

        return {
            'name': name,
            'gender': gender,
            'age': age,
            'personality': personality,
            'description': description
        }

    def _identify_gender(self, name: str, description: str) -> str:
        """
        识别角色性别

        Args:
            name: 角色名
            description: 角色描述

        Returns:
            '男', '女', 或 '旁白'
        """
        # 特殊角色：旁白
        if '旁白' in name or '旁白' in description:
            return '旁白'

        # 先检查角色名中的关键词（优先级更高）
        # 检查男性关键词
        for keyword in self.MALE_KEYWORDS:
            if keyword in name:
                return '男'

        # 检查女性关键词
        for keyword in self.FEMALE_KEYWORDS:
            if keyword in name:
                return '女'

        # 再检查描述中的关键词
        # 检查男性关键词
        for keyword in self.MALE_KEYWORDS:
            if keyword in description:
                return '男'

        # 检查女性关键词
        for keyword in self.FEMALE_KEYWORDS:
            if keyword in description:
                return '女'

        # 默认：女
        return '女'

    def _identify_age(self, description: str) -> str:
        """
        识别角色年龄

        Args:
            description: 角色描述

        Returns:
            '年轻', '成熟', 或 '中年'
        """
        # 检查具体数字年龄
        age_match = re.search(r'(\d+)岁', description)
        if age_match:
            age = int(age_match.group(1))
            if age <= 25:
                return '年轻'
            elif age <= 45:
                return '成熟'
            else:
                return '中年'

        # 检查关键词
        for age_type, keywords in self.AGE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description:
                    return age_type

        # 默认：年轻
        return '年轻'

    def _identify_personality(self, description: str) -> str:
        """
        识别角色性格

        Args:
            description: 角色描述

        Returns:
            '急躁', '沉稳', '活泼', 或 '正常'
        """
        for personality, keywords in self.PERSONALITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description:
                    return personality

        # 默认：正常
        return '正常'


# 测试代码
if __name__ == '__main__':
    # 测试脚本
    test_script = """
## 角色列表

【莱昂】男主角，二十二岁，原本是见习骑士。内心充满槽点。

【汤姆】莱昂的侍从，热血少年，正义感过剩，声音宏亮。

【艾莉丝】公主，温柔善良的少女。

【魔王】魔王城之主，优雅但疲惫。

【国王】艾莉丝的父亲，成熟稳重。

【旁白】场景描述。

---

【莱昂】唉，人生剧本是不是拿错了。
"""

    parser = CharacterParser()
    result = parser.parse_script(test_script)

    print(f"识别到 {len(result['characters'])} 个角色\n")

    for name, info in result['characters'].items():
        print(f"{name}:")
        print(f"  性别: {info['gender']}")
        print(f"  年龄: {info['age']}")
        print(f"  性格: {info['personality']}")
        print(f"  描述: {info['description']}")
        print()
