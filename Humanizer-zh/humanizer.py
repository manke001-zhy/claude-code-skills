#!/usr/bin/env python3
"""
Humanizer-zh - AI 写作去痕工具

这个脚本用于消除 AI 生成的文本痕迹，使文本更自然、更像人类写作。
"""

import re
import random
from typing import List, Dict, Optional

class HumanizerZH:
    """中文 AI 文本人类化处理器"""
    
    def __init__(self):
        # AI 常用词汇替换表
        self.ai_words = {
            "首先": ["一开始", "首先来说", "在开始之前"],
            "其次": ["然后", "接下来", "之后"],
            "再次": ["还有", "另外", "此外"],
            "最后": ["最终", "总的来说", "到最后"],
            "总之": ["总而言之", "概括来说", "简单总结"],
            "因此": ["所以", "正因为如此", "于是"],
            "然而": ["不过", "但是", "只是"],
            "并且": ["而且", "同时", "此外"],
            "此外": ["还有", "另外", "并且"],
            "综上所述": ["总的来说", "从整体来看", "总体而言"],
            "值得注意的是": ["需要注意的是", "特别要说明的是"],
            "从本质上讲": ["从根本上说", "本质上"],
            "一般来说": ["通常来说", "一般而言", "在多数情况下"],
            "换句话说": ["也就是说", "换种说法"],
            "与此同时": ["与此同时", "同时", "在这期间"],
            "进一步来说": ["而且", "更重要的是"],
            "这就意味着": ["这说明", "意味着"],
            "不可否认的是": ["不可否认", "确实"],
            "有鉴于此": ["因此", "所以", "鉴于这种情况"],
        }
        
        # 需要避免的句式模式
        self.ai_patterns = [
            r"首先，.*",
            r"其次，.*",
            r"最后，.*",
            r"综上所述，.*",
            r"因此，.*",
            r"然而，.*",
            r"从.*角度来说",
            r"值得注意的是",
            r"不可否认的是",
            r"从本质上讲",
            r"换句话说",
            r"这就意味着",
            r"有鉴于此",
            r"更进一步地说",
            r"在.*方面",
            r"不仅.*而且.*",
        ]
        
        # 人类写作特征词
        self.human_markers = [
            "说实话", "我觉得", "老实说", "说真的",
            "我个人认为", "按我的经验", "说实话",
        ]
    
    def humanize(self, text: str, intensity: str = "medium") -> str:
        """
        人类化文本
        
        Args:
            text: 输入的 AI 生成的文本
            intensity: 处理强度 ('light', 'medium', 'heavy')
        
        Returns:
            人类化后的文本
        """
        if not text or not text.strip():
            return text
        
        result = text
        
        # 词汇替换
        result = self._replace_ai_words(result, intensity)
        
        # 句式变化
        result = self._vary_sentence_structures(result, intensity)
        
        # 添加人类特征
        result = self._add_human_markers(result, intensity)
        
        # 清理过度使用的前缀词
        result = self._clean_up_starters(result)
        
        return result
    
    def _replace_ai_words(self, text: str, intensity: str) -> str:
        """替换 AI 常用词汇"""
        replacements_count = {"light": 1, "medium": 2, "heavy": 3}
        max_replacements = replacements_count.get(intensity, 2)
        
        result = text
        replacements_made = 0
        
        for ai_word, alternatives in self.ai_words.items():
            if replacements_made >= max_replacements:
                break
            
            if ai_word in result:
                # 随机选择替换词
                alt = random.choice(alternatives)
                # 确保只替换一次出现
                result = result.replace(ai_word, alt, 1)
                replacements_made += 1
        
        return result
    
    def _vary_sentence_structures(self, text: str, intensity: str) -> str:
        """变化句式结构"""
        sentences = re.split(r'([。！？])', text)
        
        varied_sentences = []
        for i, sent in enumerate(sentences):
            if sent and len(sent) > 10:
                # 随机添加一些变化
                if random.random() < 0.3:
                    # 添加插入语
                    insert_markers = ["（其实）", "（说真的）", "（你知道）", "（说实话）"]
                    marker = random.choice(insert_markers)
                    # 在句子中间插入
                    if len(sent) > 20:
                        insert_pos = len(sent) // 2
                        sent = sent[:insert_pos] + marker + sent[insert_pos:]
            
            varied_sentences.append(sent)
        
        return ''.join(varied_sentences)
    
    def _add_human_markers(self, text: str, intensity: str) -> str:
        """添加人类写作特征"""
        if intensity == "light":
            return text
        
        # 在适当位置添加人类特征词
        if random.random() < 0.4:
            marker = random.choice(self.human_markers)
            sentences = re.split(r'([。！？])', text)
            if len(sentences) >= 4:
                # 在第二句后添加
                insert_pos = 2
                sentences.insert(insert_pos, marker)
                return ''.join(sentences)
        
        return text
    
    def _clean_up_starters(self, text: str) -> str:
        """清理过度使用的前缀词"""
        # 减少 "首先"、"其次" 等的使用频率
        cleaners = [
            (r"首先，", ""),
            (r"其次，", ""),
            (r"再次，", ""),
            (r"最后，", "最终，"),
        ]
        
        for pattern, replacement in cleaners:
            # 随机清理一半的出现
            matches = list(re.finditer(pattern, text))
            for match in matches[::2]:  # 每隔一个清理
                text = text[:match.start()] + replacement + text[match.end():]
        
        return text
    
    def process_batch(self, texts: List[str], intensity: str = "medium") -> List[str]:
        """批量处理多个文本"""
        return [self.humanize(text, intensity) for text in texts]


def main():
    """主函数 - 处理命令行输入"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python humanizer.py <text> [--light|--medium|--heavy]")
        print("\nOptions:")
        print("  --light   轻度处理，保留更多原始内容")
        print("  --medium  中度处理（默认）")
        print("  --heavy   重度处理，最大程度人类化")
        return
    
    text = sys.argv[1]
    intensity = "medium"
    
    if "--light" in sys.argv:
        intensity = "light"
    elif "--heavy" in sys.argv:
        intensity = "heavy"
    
    humanizer = HumanizerZH()
    result = humanizer.humanize(text, intensity)
    
    print(result)


if __name__ == "__main__":
    main()
