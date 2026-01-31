#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多后端TTS适配器
支持Edge TTS、GPT-SoVITS、科大讯飞等多种TTS服务
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import asyncio


class TTSBackend(ABC):
    """TTS后端抽象基类"""

    @abstractmethod
    async def synthesize(self, text: str, voice: str, rate: str = '+0%', **kwargs) -> bytes:
        """
        合成语音

        Args:
            text: 要合成的文本
            voice: 声音ID
            rate: 语速 (Edge TTS格式: '+20%', '-15%')
            **kwargs: 其他参数

        Returns:
            音频数据(MP3格式)
        """
        pass

    @abstractmethod
    def get_voice_description(self, voice: str) -> str:
        """获取声音描述"""
        pass


class EdgeTTSBackend(TTSBackend):
    """Edge TTS后端"""

    def __init__(self):
        import edge_tts
        self.edge_tts = edge_tts

    async def synthesize(self, text: str, voice: str, rate: str = '+0%', **kwargs) -> bytes:
        """使用Edge TTS合成语音"""
        communicate = self.edge_tts.Communicate(text, voice)

        # Edge TTS的语速格式
        if rate != '+0%':
            communicate = self.edge_tts.Communicate(text, voice, rate=rate)

        # 返回音频数据
        return await communicate.to_mp3()

    def get_voice_description(self, voice: str) -> str:
        """获取声音描述"""
        voice_map = {
            'zh-CN-YunxiNeural': '年轻男声',
            'zh-CN-YunjianNeural': '成熟男声',
            'zh-CN-XiaoxiaoNeural': '温柔女声',
            'zh-CN-XiaoyiNeural': '成熟女声',
        }
        return voice_map.get(voice, '未知声音')


class GPTSoVITSBackend(TTSBackend):
    """GPT-SoVITS后端"""

    def __init__(self, api_url: str = "http://localhost:9882"):
        """
        初始化GPT-SoVITS后端

        Args:
            api_url: GPT-SoVITS API地址
        """
        self.api_url = api_url
        self.voice_models = {}  # 声音模型映射

        # 加载声音模型配置
        self._load_voice_models()

    def _load_voice_models(self):
        """加载声音模型配置"""
        # 这里可以配置不同角色对应的模型
        self.voice_models = {
            'child_male': {
                'model': 'xiaobao_model.pth',
                'description': '小男孩',
                'speed': 1.3  # 小孩语速较快
            },
            'child_female': {
                'model': 'xiaohong_model.pth',
                'description': '小女孩',
                'speed': 1.3
            },
            'elderly_male': {
                'model': 'grandpa_model.pth',
                'description': '老年男性',
                'speed': 0.8  # 老人语速较慢
            },
            'elderly_female': {
                'model': 'grandma_model.pth',
                'description': '老年女性',
                'speed': 0.8
            },
        }

    async def synthesize(self, text: str, voice: str, rate: str = '+0%', **kwargs) -> bytes:
        """使用GPT-SoVITS合成语音"""
        import requests

        # 获取声音配置
        voice_config = self.voice_models.get(voice, {
            'model': voice,
            'description': '未知',
            'speed': 1.0
        })

        # 解析语速 (从Edge TTS格式转换为倍速)
        speed = self._parse_rate_to_speed(rate, voice_config['speed'])

        # 调用GPT-SoVITS API
        try:
            response = requests.post(
                f"{self.api_url}/tts",
                json={
                    "text": text,
                    "model": voice_config['model'],
                    "speed": speed,
                    **kwargs
                },
                timeout=60
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"[ERROR] GPT-SoVITS调用失败: {e}")
            # 返回空音频
            return b''

    def _parse_rate_to_speed(self, rate: str, default_speed: float = 1.0) -> float:
        """将Edge TTS语速格式转换为倍速"""
        if rate == '+0%':
            return default_speed
        elif rate.endswith('%'):
            try:
                percentage = int(rate[:-1]) / 100
                return default_speed * (1 + percentage)
            except:
                return default_speed
        return default_speed

    def get_voice_description(self, voice: str) -> str:
        """获取声音描述"""
        return self.voice_models.get(voice, {}).get('description', '未知声音')


class XunfeiTTSBackend(TTSBackend):
    """科大讯飞TTS后端"""

    def __init__(self, app_id: str, api_key: str, api_secret: str):
        """
        初始化讯飞TTS后端

        Args:
            app_id: 讯飞应用ID
            api_key: 讯飞API Key
            api_secret: 讯飞API Secret
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret

        # 声音映射
        self.voice_map = {
            'child_male': 'xiaoyan_child',
            'child_female': 'xiaoyan_child',
            'elderly_male': 'xiaoyan_old',
            'elderly_female': 'xiaoyan_old',
        }

    async def synthesize(self, text: str, voice: str, rate: str = '+0%', **kwargs) -> bytes:
        """使用科大讯飞合成语音"""
        # 这里需要实现讯飞的API调用
        # 暂时返回空音频
        print(f"[INFO] 讯飞TTS: voice={voice}, text={text[:20]}...")
        return b''

    def get_voice_description(self, voice: str) -> str:
        """获取声音描述"""
        return '讯飞声音'


class TTSFactory:
    """TTS工厂类"""

    @staticmethod
    def create_backend(backend_type: str, **config) -> TTSBackend:
        """
        创建TTS后端

        Args:
            backend_type: 后端类型 ('edge', 'gptsovits', 'xunfei')
            **config: 后端配置

        Returns:
            TTS后端实例
        """
        if backend_type == 'edge':
            return EdgeTTSBackend()

        elif backend_type == 'gptsovits':
            api_url = config.get('api_url', 'http://localhost:9882')
            return GPTSoVITSBackend(api_url=api_url)

        elif backend_type == 'xunfei':
            app_id = config.get('app_id')
            api_key = config.get('api_key')
            api_secret = config.get('api_secret')

            if not all([app_id, api_key, api_secret]):
                raise ValueError("讯飞TTS需要app_id、api_key、api_secret参数")

            return XunfeiTTSBackend(app_id, api_key, api_secret)

        else:
            raise ValueError(f"不支持的TTS后端: {backend_type}")


class HybridTTSBackend(TTSBackend):
    """
    混合TTS后端
    根据声音类型自动选择合适的TTS服务
    """

    def __init__(self, default_backend: TTSBackend, special_backends: Dict[str, TTSBackend] = None):
        """
        初始化混合TTS后端

        Args:
            default_backend: 默认TTS后端
            special_backends: 特殊声音的后端映射 {voice_id: backend}
        """
        self.default_backend = default_backend
        self.special_backends = special_backends or {}

        # 定义哪些声音使用特殊后端
        self.voice_routing = {
            # GPT-SoVITS处理的声音
            'child_male': 'gptsovits',
            'child_female': 'gptsovits',
            'elderly_male': 'gptsovits',
            'elderly_female': 'gptsovits',
        }

    async def synthesize(self, text: str, voice: str, rate: str = '+0%', **kwargs) -> bytes:
        """根据声音类型路由到合适的后端"""
        # 确定使用哪个后端
        backend_type = self.voice_routing.get(voice, 'default')

        if backend_type == 'default' or backend_type not in self.special_backends:
            # 使用默认后端
            return await self.default_backend.synthesize(text, voice, rate, **kwargs)
        else:
            # 使用特殊后端
            backend = self.special_backends[backend_type]
            return await backend.synthesize(text, voice, rate, **kwargs)

    def get_voice_description(self, voice: str) -> str:
        """获取声音描述"""
        backend_type = self.voice_routing.get(voice, 'default')

        if backend_type == 'default' or backend_type not in self.special_backends:
            return self.default_backend.get_voice_description(voice)
        else:
            return self.special_backends[backend_type].get_voice_description(voice)


# 测试代码
if __name__ == '__main__':
    import asyncio

    async def test_tts():
        """测试TTS后端"""
        print("=" * 80)
        print("TTS后端测试")
        print("=" * 80)

        # 测试Edge TTS
        print("\n[1] 测试Edge TTS后端")
        edge_backend = TTSFactory.create_backend('edge')
        audio = await edge_backend.synthesize("你好，世界", "zh-CN-YunxiNeural")
        print(f"✓ 音频大小: {len(audio)} bytes")

        # 测试GPT-SoVITS (如果服务运行中)
        print("\n[2] 测试GPT-SoVITS后端 (需要服务运行)")
        try:
            gptsovits_backend = TTSFactory.create_backend('gptsovits')
            audio = await gptsovits_backend.synthesize("你好", "child_male")
            print(f"✓ 音频大小: {len(audio)} bytes")
        except Exception as e:
            print(f"✗ 连接失败: {e}")

        # 测试混合后端
        print("\n[3] 测试混合后端")
        hybrid_backend = HybridTTSBackend(
            default_backend=edge_backend,
            special_backends={'gptsovits': gptsovits_backend}
        )
        print("✓ 混合后端创建成功")

    asyncio.run(test_tts())
