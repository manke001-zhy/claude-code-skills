#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-SoVITS连接测试脚本
用于测试GPT-SoVITS服务是否可用
"""

import asyncio
import requests
import sys
from pathlib import Path


def test_gptsovits_connection(api_url="http://localhost:9882"):
    """测试GPT-SoVITS服务连接"""

    print("=" * 80)
    print("GPT-SoVITS连接测试")
    print("=" * 80)

    print(f"\n[INFO] 尝试连接到: {api_url}")

    try:
        # 测试健康检查接口
        response = requests.get(f"{api_url}/health", timeout=5)

        if response.status_code == 200:
            print("[OK] ✓ GPT-SoVITS服务正常运行")
            return True
        else:
            print(f"[WARN] 服务返回状态码: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("[ERROR] ✗ 无法连接到GPT-SoVITS服务")
        print("\n可能的原因:")
        print("1. GPT-SoVITS服务未启动")
        print("2. 端口号不正确(默认9882)")
        print("3. 防火墙阻止了连接")
        print("\n解决方法:")
        print("1. 确认GPT-SoVITS已启动")
        print("2. 检查端口: python api.py --port 9882")
        print("3. 检查防火墙设置")
        return False

    except Exception as e:
        print(f"[ERROR] ✗ 连接错误: {e}")
        return False


async def test_voice_generation(api_url="http://localhost:9882"):
    """测试语音生成"""

    print("\n" + "=" * 80)
    print("语音生成测试")
    print("=" * 80)

    # 测试文本
    test_text = "你好，这是一个测试。"

    print(f"\n[INFO] 测试文本: {test_text}")

    # 这里需要你提供已训练好的模型名称
    model = input("\n请输入模型名称(如 xiaobao_model.pth，或按跳过): ").strip()

    if not model:
        print("[INFO] 跳过语音生成测试")
        return True

    try:
        response = requests.post(
            f"{api_url}/tts",
            json={
                "text": test_text,
                "model": model,
                "speed": 1.0
            },
            timeout=60
        )

        if response.status_code == 200:
            # 保存音频
            output_file = Path("test_output.mp3")
            output_file.write_bytes(response.content)

            print(f"[OK] ✓ 音频生成成功")
            print(f"[INFO] 文件大小: {len(response.content)} bytes")
            print(f"[INFO] 已保存到: {output_file.absolute()}")

            return True
        else:
            print(f"[ERROR] ✗ 生成失败，状态码: {response.status_code}")
            print(f"[INFO] 响应: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] ✗ 生成错误: {e}")
        return False


def print_setup_guide():
    """打印部署指南"""

    print("\n" + "=" * 80)
    print("GPT-SoVITS快速部署指南")
    print("=" * 80)

    print("\n方式1: 使用整合包(推荐新手)")
    print("-" * 80)
    print("1. 淘宝搜索 'GPT-SoVITS整合包'")
    print("2. 购买并下载(约¥9.9-29.9)")
    print("3. 解压到本地目录")
    print("4. 双击 '启动.exe'")
    print("5. 等待服务启动")
    print("6. 打开浏览器访问 http://localhost:9872")

    print("\n方式2: 手动部署(免费)")
    print("-" * 80)
    print("1. git clone https://github.com/RVC-Boss/GPT-SoVITS.git")
    print("2. cd GPT-SoVITS")
    print("3. python -m venv venv")
    print("4. venv\\Scripts\\activate  (Windows)")
    print("5. pip install -r requirements.txt")
    print("6. python tools/download_models.py")
    print("7. python api.py --port 9882")

    print("\n训练声音模型:")
    print("-" * 80)
    print("1. 准备5-10秒音频样本")
    print("2. 打开WebUI: http://localhost:9872")
    print("3. 上传音频样本")
    print("4. 点击'开始训练'")
    print("5. 等待3-5分钟")
    print("6. 测试生成语音")


async def main():
    """主函数"""

    # 打印部署指南
    print_setup_guide()

    # 询问是否继续测试
    print("\n" + "=" * 80)
    choice = input("是否已启动GPT-SoVITS服务？(y/n): ").strip().lower()

    if choice != 'y':
        print("\n[INFO] 请先启动GPT-SoVITS服务，然后重新运行此脚本")
        print("[INFO] 服务启动命令: python api.py --port 9882")
        return

    # 测试连接
    api_url = "http://localhost:9882"

    if not test_gptsovits_connection(api_url):
        print("\n[FAIL] 连接测试失败")
        print("[INFO] 请检查GPT-SoVITS服务是否正常运行")
        return

    # 测试语音生成
    await test_voice_generation(api_url)

    print("\n" + "=" * 80)
    print("测试完成!")
    print("=" * 80)

    if test_gptsovits_connection(api_url):
        print("\n[OK] ✓ GPT-SoVITS可用，可以集成到项目中")
        print("\n下一步:")
        print("1. 训练你需要的声音模型(小孩、老人等)")
        print("2. 使用 tts_factory.py 集成到项目")
        print("3. 运行 drama_to_audio_v2.py 生成广播剧")
    else:
        print("\n[INFO] 请先解决连接问题")


if __name__ == '__main__':
    asyncio.run(main())
