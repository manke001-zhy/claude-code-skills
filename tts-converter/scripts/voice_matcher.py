#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能声音匹配模块
根据角色特征自动选择合适的声音
"""

from typing import Dict, List


class VoiceMatcher:
    """声音匹配器"""

    # 声音库定义
    VOICE_LIBRARY = {
        '旁白': {
            'voice': 'zh-CN-YunjianNeural',
            'description': '成熟男声',
            'category': 'male-mature'
        },
        '男-年轻': {
            'voice': 'zh-CN-YunxiNeural',
            'description': '年轻男声',
            'category': 'male-young'
        },
        '男-温和': {
            'voice': 'zh-CN-YunxiaNeural',
            'description': '温和男声',
            'category': 'male-young'
        },
        '男-成熟': {
            'voice': 'zh-CN-YunjianNeural',
            'description': '成熟男声',
            'category': 'male-mature'
        },
        '男-中年': {
            'voice': 'zh-CN-YunyangNeural',
            'description': '中年男声',
            'category': 'male-middle'
        },
        '女-年轻-温柔': {
            'voice': 'zh-CN-XiaoxiaoNeural',
            'description': '温柔女声',
            'category': 'female-young'
        },
        '女-年轻-活泼': {
            'voice': 'zh-CN-YunxiNeural',
            'description': '活泼女声',
            'category': 'female-young'
        },
        '女-成熟': {
            'voice': 'zh-CN-XiaoyiNeural',
            'description': '成熟女声',
            'category': 'female-mature'
        },
        '女-东北': {
            'voice': 'zh-CN-liaoning-XiaobeiNeural',
            'description': '东北口音女声',
            'category': 'female-accent'
        },
        '女-陕西': {
            'voice': 'zh-CN-shaanxi-XiaoniNeural',
            'description': '陕西口音女声',
            'category': 'female-accent'
        },
        # 特殊声音(通过语速模拟)
        '小孩-男': {
            'voice': 'zh-CN-YunxiNeural',
            'description': '小男孩(快语速)',
            'category': 'child',
            'rate': '+30%',
            'note': '使用年轻声音+快语速模拟'
        },
        '小孩-女': {
            'voice': 'zh-CN-XiaoxiaoNeural',
            'description': '小女孩(快语速)',
            'category': 'child',
            'rate': '+30%',
            'note': '使用年轻声音+快语速模拟'
        },
        '老人-男': {
            'voice': 'zh-CN-YunjianNeural',
            'description': '老年男性(慢语速)',
            'category': 'elderly',
            'rate': '-20%',
            'note': '使用成熟声音+慢语速模拟'
        },
        '老人-女': {
            'voice': 'zh-CN-XiaoyiNeural',
            'description': '老年女性(慢语速)',
            'category': 'elderly',
            'rate': '-20%',
            'note': '使用成熟声音+慢语速模拟'
        },
    }

    # 备选声音列表（用于解决冲突）
    BACKUP_VOICES = {
        'male-young': [
            'zh-CN-YunxiNeural',
            'zh-CN-YunxiaNeural',
            'zh-CN-YunyangNeural'
        ],
        'male-mature': [
            'zh-CN-YunjianNeural',
            'zh-CN-YunyangNeural'
        ],
        'male-middle': [
            'zh-CN-YunyangNeural',
            'zh-CN-YunjianNeural'
        ],
        'female-young': [
            'zh-CN-XiaoxiaoNeural',
            'zh-CN-YunxiNeural'
        ],
        'female-mature': [
            'zh-CN-XiaoyiNeural',
            'zh-CN-XiaoxiaoNeural'
        ],
        'female-accent': [
            'zh-CN-liaoning-XiaobeiNeural',
            'zh-CN-shaanxi-XiaoniNeural'
        ],
        'child': [
            'zh-CN-YunxiNeural',
            'zh-CN-XiaoxiaoNeural'
        ],
        'elderly': [
            'zh-CN-YunjianNeural',
            'zh-CN-XiaoyiNeural'
        ]
    }

    def __init__(self):
        """初始化匹配器"""
        self.used_voices = set()  # 已使用的声音

    def assign_voices(self, characters: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        为所有角色分配声音

        Args:
            characters: 角色信息字典 {角色名: {gender, age, personality, ...}}

        Returns:
            声音分配字典 {角色名: {voice, voice_description, rate, ...}}
        """
        assignments = {}

        # 第一轮：根据规则分配声音
        voice_counts = {}  # 记录每个声音被使用的次数

        for name, char_info in characters.items():
            voice, desc = self._assign_voice_by_rules(char_info)

            # 获取语速
            age = char_info['age']
            if age == '小孩':
                # 小孩使用快语速
                rate = '+30%'
            elif age == '老人':
                # 老人使用慢语速
                rate = '-20%'
            else:
                # 其他角色根据性格调整语速
                rate = self._get_rate_by_personality(char_info['personality'])

            assignments[name] = {
                'voice': voice,
                'voice_description': desc,
                'rate': rate,
                'gender': char_info['gender'],
                'age': char_info['age'],
                'personality': char_info['personality']
            }

            # 统计声音使用次数
            if voice not in voice_counts:
                voice_counts[voice] = 0
            voice_counts[voice] += 1

        # 第二轮：解决冲突
        assignments = self._resolve_conflicts(assignments, voice_counts)

        return assignments

    def _assign_voice_by_rules(self, char_info: Dict) -> tuple:
        """
        根据规则分配单个角色声音

        Args:
            char_info: 角色信息

        Returns:
            (voice_name, voice_description)
        """
        gender = char_info['gender']
        age = char_info['age']
        personality = char_info['personality']

        # 旁白
        if gender == '旁白':
            return self.VOICE_LIBRARY['旁白']['voice'], self.VOICE_LIBRARY['旁白']['description']

        # 小孩
        if age == '小孩':
            if gender == '男':
                return self.VOICE_LIBRARY['小孩-男']['voice'], self.VOICE_LIBRARY['小孩-男']['description']
            else:
                return self.VOICE_LIBRARY['小孩-女']['voice'], self.VOICE_LIBRARY['小孩-女']['description']

        # 老人
        if age == '老人':
            if gender == '男':
                return self.VOICE_LIBRARY['老人-男']['voice'], self.VOICE_LIBRARY['老人-男']['description']
            else:
                return self.VOICE_LIBRARY['老人-女']['voice'], self.VOICE_LIBRARY['老人-女']['description']

        # 男性
        if gender == '男':
            if age == '年轻':
                if personality == '沉稳':
                    # 年轻沉稳男声
                    return self.VOICE_LIBRARY['男-成熟']['voice'], self.VOICE_LIBRARY['男-成熟']['description']
                elif personality == '温和':
                    # 年轻温和男声
                    return self.VOICE_LIBRARY['男-温和']['voice'], self.VOICE_LIBRARY['男-温和']['description']
                else:
                    # 普通年轻男声
                    return self.VOICE_LIBRARY['男-年轻']['voice'], self.VOICE_LIBRARY['男-年轻']['description']
            elif age == '成熟':
                return self.VOICE_LIBRARY['男-成熟']['voice'], self.VOICE_LIBRARY['男-成熟']['description']
            else:  # 中年
                return self.VOICE_LIBRARY['男-中年']['voice'], self.VOICE_LIBRARY['男-中年']['description']

        # 女性
        if gender == '女':
            if age == '年轻':
                if personality == '活泼':
                    return self.VOICE_LIBRARY['女-年轻-活泼']['voice'], self.VOICE_LIBRARY['女-年轻-活泼']['description']
                else:
                    return self.VOICE_LIBRARY['女-年轻-温柔']['voice'], self.VOICE_LIBRARY['女-年轻-温柔']['description']
            else:  # 成熟
                return self.VOICE_LIBRARY['女-成熟']['voice'], self.VOICE_LIBRARY['女-成熟']['description']

        # 默认：年轻男声
        return self.VOICE_LIBRARY['男-年轻']['voice'], self.VOICE_LIBRARY['男-年轻']['description']

    def _get_rate_by_personality(self, personality: str) -> str:
        """
        根据性格获取语速

        Args:
            personality: 性格类型

        Returns:
            Edge TTS格式的语速字符串
        """
        # 温和调整
        rate_map = {
            '急躁': '+20%',   # 1.2倍速
            '沉稳': '-15%',   # 0.85倍速
            '活泼': '+0%',    # 1.0倍速
            '正常': '+0%'     # 1.0倍速
        }

        return rate_map.get(personality, '+0%')

    def _resolve_conflicts(self, assignments: Dict, voice_counts: Dict) -> Dict:
        """
        解决声音冲突

        Args:
            assignments: 声音分配字典
            voice_counts: 声音使用统计

        Returns:
            解决冲突后的分配字典
        """
        # 找出冲突的声音
        conflicts = {voice: count for voice, count in voice_counts.items() if count > 1}

        if not conflicts:
            return assignments

        # 对每个冲突的声音，尝试重新分配
        for voice, count in conflicts.items():
            # 找出使用该声音的所有角色
            conflict_roles = [
                (name, info)
                for name, info in assignments.items()
                if info['voice'] == voice
            ]

            # 第一个角色保持不变，其他角色尝试更换声音
            for i, (name, info) in enumerate(conflict_roles[1:], 1):
                # 获取角色的声音类别
                original_voice_key = self._get_voice_key_by_voice(voice)

                if original_voice_key is None:
                    continue

                # 获取备选声音列表
                backup_list = self.BACKUP_VOICES.get(original_voice_key, [])

                # 尝试使用备选声音
                for backup_voice in backup_list:
                    if backup_voice != voice:
                        # 检查备选声音是否已被使用
                        already_used = any(
                            assign['voice'] == backup_voice
                            for assign in assignments.values()
                        )

                        if not already_used:
                            # 使用备选声音
                            assignments[name]['voice'] = backup_voice
                            assignments[name]['voice_description'] = self._get_description_by_voice(backup_voice)
                            break

        return assignments

    def _get_voice_key_by_voice(self, voice_name: str) -> str:
        """
        根据声音名称获取声音类别

        Args:
            voice_name: 声音名称

        Returns:
            声音类别，如 'male-young'
        """
        for key, info in self.VOICE_LIBRARY.items():
            if info['voice'] == voice_name:
                return info['category']

        return None

    def _get_description_by_voice(self, voice_name: str) -> str:
        """
        根据声音名称获取描述

        Args:
            voice_name: 声音名称

        Returns:
            声音描述
        """
        for info in self.VOICE_LIBRARY.values():
            if info['voice'] == voice_name:
                return info['description']

        return '未知声音'


# 测试代码
if __name__ == '__main__':
    # 测试角色
    test_characters = {
        '莱昂': {'name': '莱昂', 'gender': '男', 'age': '年轻', 'personality': 'normal', 'description': '男主角'},
        '艾莉丝': {'name': '艾莉丝', 'gender': '女', 'age': '年轻', 'personality': '活泼', 'description': '公主'},
        '汤姆': {'name': '汤姆', 'gender': '男', 'age': '年轻', 'personality': '急躁', 'description': '侍从'},
        '魔王': {'name': '魔王', 'gender': '男', 'age': '成熟', 'personality': '沉稳', 'description': '魔王'},
        '国王': {'name': '国王', 'gender': '男', 'age': '成熟', 'personality': '沉稳', 'description': '国王'},
        '旁白': {'name': '旁白', 'gender': '旁白', 'age': '年轻', 'personality': 'normal', 'description': '旁白'}
    }

    matcher = VoiceMatcher()
    assignments = matcher.assign_voices(test_characters)

    print("声音分配结果:\n")

    for name, info in assignments.items():
        rate_str = f" 语速{info['rate']}" if info['rate'] != '+0%' else ""
        print(f"{name}: {info['voice_description']}{rate_str}")
