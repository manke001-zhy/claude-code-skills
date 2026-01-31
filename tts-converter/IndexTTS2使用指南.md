# IndexTTS2 - 你已安装的TTS系统

## 🎉 好消息！

**你电脑上已经安装了 IndexTTS2！**

这是一个非常强大的零样本TTS系统，由Bilibili开发！

---

## 📊 IndexTTS2 是什么？

### 核心特性

IndexTTS2 是一个**零样本TTS系统**，具有以下强大功能：

1. ✅ **零样本声音克隆** - 只需几秒音频即可克隆声音
2. ✅ **情感控制** - 可以生成不同情感的语音
3. ✅ **时长控制** - 可以精确控制语音时长
4. ✅ **高音质** - 音质接近真实人声
5. ✅ **多语言支持** - 支持中英文混合
6. ✅ **已安装模型** - 你已经有4.4GB的模型文件

### 与其他TTS对比

| 特性 | Edge TTS | GPT-SoVITS | **IndexTTS2** |
|------|----------|------------|---------------|
| 声音数量 | 8个固定 | 需训练 | **零样本克隆** ⭐ |
| 情感控制 | ❌ | ❌ | **✅ 支持** ⭐ |
| 时长控制 | ❌ | ❌ | **✅ 支持** ⭐ |
| 音质 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **⭐⭐⭐⭐⭐** |
| 部署难度 | 简单 | 中等 | **已安装！** ⭐ |
| 数据需求 | - | 5-10秒 | **3-5秒** ⭐ |

**结论：IndexTTS2是你最佳选择！已经安装好了！**

---

## 🚀 如何使用

### 步骤1: 启动IndexTTS2

```bash
# 进入目录
cd F:/index-tts-new

# 启动WebUI
python app.py

# 或指定端口
python app.py --port 7860
```

### 步骤2: 打开Web界面

启动后会显示:
```
Running on local URL:  http://0.0.0.0:7860
```

浏览器打开: **http://localhost:7860**

### 步骤3: 使用界面

你会看到以下功能:

#### 1. **零样本TTS** (Zero-Shot TTS)
```
功能: 输入3-5秒音频样本 + 文本 → 生成目标声音的语音

输入:
- 音频提示(Audio Prompt): 上传或录制声音样本
- 文本(Text): 要合成的文本
- 情感(Emotion): 可选(如:开心、悲伤、愤怒)
- 语言(Language): 中文/英文

输出:
- 生成与样本声音相似的语音
```

#### 2. **情感TTS** (Emotional TTS)
```
功能: 指定情感风格生成语音

支持的情感:
- 开心(Happy)
- 悲伤(Sad)
- 愤怒(Angry)
- 惊讶(Surprised)
- 平静(Neutral)
- 等等...
```

#### 3. **时长控制TTS** (Duration-Controlled TTS)
```
功能: 精确控制生成语音的时长

用途:
- 视频配音(对口型)
- 固定时长音频
- 节奏控制
```

---

## 🎬 用于广播剧制作

### 方案1: 直接使用WebUI(最简单)

#### 制作流程:

1. **准备声音样本** (3-5秒)
```
小孩样本: "我叫小宝，今年七岁"
老人样本: "咳咳，我是你们的爷爷"
公主样本: "大家好，我是艾莉丝公主"
```

2. **启动IndexTTS2**
```bash
cd F:/index-tts-new
python app.py
```

3. **打开浏览器** → http://localhost:7860

4. **逐个角色生成音频**

**角色1: 小宝**
- 上传小宝的音频样本
- 输入文本: "爷爷，你看我找到了什么！"
- 选择情感: 开心
- 点击生成
- 下载音频

**角色2: 爷爷**
- 上传爷爷的音频样本
- 输入文本: "艾莉丝，父皇好想你"
- 选择情感: 慈祥/平静
- 点击生成
- 下载音频

5. **用音频编辑软件合并**
- 使用 Audacity
- 按脚本顺序排列音频
- 导出最终MP3

---

### 方案2: 使用API(自动化)

#### IndexTTS2 API调用示例:

```python
import requests
import json

# IndexTTS2 API地址
api_url = "http://localhost:7860/api/tts"

# 生成语音
def generate_tts(text, audio_prompt_path, emotion="neutral"):
    """
    使用IndexTTS2生成语音

    Args:
        text: 要合成的文本
        audio_prompt_path: 音频样本路径
        emotion: 情感 (happy, sad, angry, neutral等)

    Returns:
        音频数据
    """

    # 准备数据
    files = {
        'audio_prompt': open(audio_prompt_path, 'rb')
    }

    data = {
        'text': text,
        'emotion': emotion,
        'language': 'zh',
        'speed': 1.0
    }

    # 发送请求
    response = requests.post(api_url, files=files, data=data)

    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: {response.status_code}")
        return None

# 使用示例
audio = generate_tts(
    text="爷爷，你看我找到了什么！",
    audio_prompt_path="voices/xiaobao_sample.wav",
    emotion="happy"
)

# 保存音频
if audio:
    with open("xiaobao_output.mp3", "wb") as f:
        f.write(audio)
```

---

## 🔧 集成到现有项目

### 修改drama_to_audio_v2.py支持IndexTTS2

我已经为你创建了IndexTTS2适配器:

```python
# 文件: indextts_backend.py

import requests
import os
from pathlib import Path

class IndexTTS2Backend:
    """IndexTTS2后端"""

    def __init__(self, api_url="http://localhost:7860"):
        self.api_url = api_url

    async def synthesize(self, text, voice_sample_path, emotion="neutral", **kwargs):
        """使用IndexTTS2合成语音"""

        # 检查服务是否运行
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
        except:
            print("[ERROR] IndexTTS2服务未启动")
            print("[INFO] 请运行: cd F:/index-tts-new && python app.py")
            return None

        # 调用TTS API
        files = {
            'audio_prompt': open(voice_sample_path, 'rb')
        }

        data = {
            'text': text,
            'emotion': emotion,
            'language': 'zh'
        }

        response = requests.post(
            f"{self.api_url}/api/tts",
            files=files,
            data=data,
            timeout=60
        )

        if response.status_code == 200:
            return response.content
        else:
            print(f"[ERROR] 生成失败: {response.status_code}")
            return None
```

---

## 📋 完整工作流程

### 准备阶段

1. **收集声音样本** (每个角色3-5秒)
```
voices/
├── xiaobao.wav      # 小男孩样本
├── grandpa.wav      # 老年男性样本
├── alice.wav        # 公主样本
├── demon.wav        # 魔王样本
└── narrator.wav     # 旁白样本
```

2. **准备脚本**
```
script.md
```

### 制作阶段

1. **启动IndexTTS2**
```bash
cd F:/index-tts-new
python app.py
```

2. **生成音频**
```
方式A: WebUI手动生成
方式B: API自动生成
```

3. **合并音频**
```
使用Audacity或Adobe Audition
```

---

## 💡 IndexTTS2 优势

### ✅ 优势1: 零样本克隆
- 不需要训练模型
- 3-5秒样本即可
- 即时生成

### ✅ 优势2: 情感控制
```
【莱昂】唉，人生剧本是不是拿错了。
        → 情感: 无奈/叹气

【国王】艾莉丝——父皇来救你了——
        → 情感: 激动/喜悦

【魔王】救命——谁来把这个女人带走——
        → 情感: 绝望/恳求
```

### ✅ 优势3: 已安装
- 模型已下载(4.4GB)
- 无需重新部署
- 直接可用

### ✅ 优势4: 高质量
- Bilibili出品
- 学术论文支持
- 音质顶级

---

## 🎯 推荐使用方式

### 对于你现在的需求:

**✅ 强烈推荐使用IndexTTS2！**

**理由:**
1. ✅ 已经安装好了
2. ✅ 零样本克隆，无需训练
3. ✅ 支持情感控制(更生动)
4. ✅ 音质比Edge TTS好
5. ✅ 比GPT-SoVITS简单(无需训练)

### 使用建议:

**短期(今天):**
1. 启动IndexTTS2: `cd F:/index-tts-new && python app.py`
2. 打开WebUI: http://localhost:7860
3. 测试生成几个音频
4. 验证音质

**中期(本周):**
1. 准备所有角色的声音样本(3-5秒)
2. 用WebUI生成所有台词
3. 用Audacity合并
4. 制作完整广播剧

**长期(未来):**
1. 学习API调用
2. 编写自动化脚本
3. 集成到现有项目

---

## 📊 三种TTS方案对比(你的情况)

| 方案 | 是否已安装 | 声音质量 | 使用难度 | 推荐度 |
|------|-----------|----------|----------|--------|
| Edge TTS | ✅ | ⭐⭐⭐⭐ | 简单 | ⭐⭐⭐⭐ |
| **IndexTTS2** | **✅** | **⭐⭐⭐⭐⭐** | **中等** | **⭐⭐⭐⭐⭐** |
| GPT-SoVITS | ❌ | ⭐⭐⭐⭐⭐ | 复杂 | ⭐⭐⭐⭐ |

**结论: IndexTTS2是你的最佳选择！**

---

## 🚀 快速开始(3步)

### 1. 启动服务
```bash
cd F:/index-tts-new
python app.py
```

### 2. 打开浏览器
```
http://localhost:7860
```

### 3. 测试
- 上传一段3秒的声音样本
- 输入要合成的文本
- 点击生成
- 听效果

---

## 📝 示例脚本

### 测试脚本

```python
# test_indextts.py
import requests
import os

# 配置
API_URL = "http://localhost:7860"
AUDIO_SAMPLE = "voices/xiaobao.wav"
TEXT = "爷爷，你看我找到了什么！"

# 生成语音
def test_indextts():
    print("=" * 80)
    print("IndexTTS2 测试")
    print("=" * 80)

    # 检查样本文件
    if not os.path.exists(AUDIO_SAMPLE):
        print(f"[ERROR] 样本文件不存在: {AUDIO_SAMPLE}")
        print("[INFO] 请准备3-5秒的声音样本")
        return

    # 调用API
    files = {'audio_prompt': open(AUDIO_SAMPLE, 'rb')}
    data = {
        'text': TEXT,
        'emotion': 'happy',
        'language': 'zh'
    }

    print(f"\n[INFO] 文本: {TEXT}")
    print(f"[INFO] 情感: happy")
    print(f"[INFO] 样本: {AUDIO_SAMPLE}")

    try:
        response = requests.post(
            f"{API_URL}/api/tts",
            files=files,
            data=data,
            timeout=60
        )

        if response.status_code == 200:
            # 保存音频
            with open("test_output.mp3", "wb") as f:
                f.write(response.content)

            print("[OK] ✓ 音频生成成功!")
            print(f"[INFO] 文件大小: {len(response.content)} bytes")
            print(f"[INFO] 已保存到: test_output.mp3")
        else:
            print(f"[ERROR] 生成失败: {response.status_code}")

    except Exception as e:
        print(f"[ERROR] {e}")
        print("\n可能的原因:")
        print("1. IndexTTS2服务未启动")
        print("   解决: cd F:/index-tts-new && python app.py")
        print("2. 端口被占用")
        print("   解决: 检查7860端口是否被占用")

if __name__ == '__main__':
    test_indextts()
```

---

## ❓ 常见问题

### Q1: IndexTTS2和GPT-SoVITS哪个更好？

**A: 对于你，IndexTTS2更好**
- ✅ 已安装
- ✅ 零样本(无需训练)
- ✅ 情感控制
- ✅ 音质相当

### Q2: 可以生成小孩声和老人声吗？

**A: 可以！**
- 上传真实小孩的3秒样本 → 生成小孩声
- 上传真实老人的3秒样本 → 生成老人声
- 音质非常逼真！

### Q3: 如何获取声音样本？

**A: 几种方式:**
1. 让亲戚朋友录音
2. 从视频/动画提取(注意版权)
3. 自己用不同声音录制
4. 使用公开的语音数据集

### Q4: 服务占用资源多吗？

**A: 中等**
- CPU: 中等占用
- GPU: 推荐使用(你的RTX 3070 Ti)
- 内存: 约8-16GB
- 你的配置完全够用！

### Q5: 可以商用吗？

**A: 需要确认**
- 联系 Bilibili: indexspeech@bilibili.com
- 或查看许可证文件
- 个人使用一般没问题

---

## 🎉 总结

**好消息：你已经有了IndexTTS2！**

**推荐行动：**
1. ✅ **现在就试试** - 启动服务测试一下
2. ✅ **准备声音样本** - 收集角色的声音样本
3. ✅ **制作广播剧** - 用IndexTTS2生成所有音频

**相比其他方案的优势：**
- ✅ 已安装(无需部署)
- ✅ 零样本(无需训练)
- ✅ 情感控制(更生动)
- ✅ 高音质(Bilibili出品)

**最终建议：用IndexTTS2！它是最适合你的！**

---

**下一步：**
1. 运行: `cd F:/index-tts-new && python app.py`
2. 打开: http://localhost:7860
3. 开始创作！

有问题随时问我！🚀
