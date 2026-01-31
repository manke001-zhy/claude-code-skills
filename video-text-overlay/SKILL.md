---
name: video-text-overlay
description: 为视频添加文字叠加层。使用 Python moviepy 库在视频任意位置添加自定义文字，支持中文字体、文字颜色、大小、描边等样式调整。当用户需要：给视频加字幕、添加标题、添加水印文字、在视频中显示文字信息、添加飘动文字效果时使用此技能。
---

# Video Text Overlay

在视频上添加文字叠加层的技能，使用 Python moviepy 库实现。

## 功能

- **静态文字**：在视频固定位置显示文字（全程或指定时长）
- **飘动文字**：多组文字从右向左飘过画面，自动分布在上中下位置
- **闪烁效果**：文字忽大忽小的动画效果

## 快速开始

### 1. 安装依赖

首次使用前需要安装 moviepy：

```bash
pip install moviepy
```

### 2. 基础用法

使用 scripts/add_text_to_video.py 脚本：

```python
from scripts.add_text_to_video import add_text_to_video

add_text_to_video(
    video_path="path/to/video.mp4",
    text="要添加的文字"
)
```

### 3. 自定义样式

```python
add_text_to_video(
    video_path="path/to/video.mp4",
    text="祝灵动的游戏大卖",
    font_size=100,           # 字体大小
    color='yellow',          # 文字颜色（white/red/blue/green/yellow等）
    stroke_color='black',    # 描边颜色
    stroke_width=4,          # 描边宽度
    font='C:/Windows/fonts/msyh.ttc',  # 字体文件路径
    duration=5.0             # 文字显示时长（秒），None=全程显示
)
```

## 常用中文字体路径

- **微软雅黑**: `C:/Windows/fonts/msyh.ttc`
- **黑体**: `C:/Windows/fonts/simhei.ttf`
- **宋体**: `C:/Windows/fonts/simsun.ttc`

## 参数说明

### 静态文字 (add_text_to_video)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `video_path` | str | 必填 | 输入视频路径 |
| `text` | str | 必填 | 要添加的文字内容 |
| `output_path` | str | auto | 输出视频路径（默认在原文件名后加 _with_text） |
| `font_size` | int | 80 | 字体大小 |
| `color` | str | 'white' | 文字颜色 |
| `stroke_color` | str | 'black' | 描边颜色 |
| `stroke_width` | int | 3 | 描边宽度 |
| `font` | str | 微软雅黑 | 字体文件路径 |
| `duration` | float | None | 文字显示时长（秒），None 表示全程显示 |
| `vertical_position` | str | 'center' | 垂直位置（center/top/bottom 或比例值如 '0.66'） |
| `blink` | bool | False | 是否启用闪烁效果 |
| `blink_speed` | float | 2.0 | 闪烁速度（每秒次数） |
| `blink_min_scale` | float | 0.7 | 最小缩放比例 |
| `blink_max_scale` | float | 1.3 | 最大缩放比例 |

### 飘动文字 (add_floating_text)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `video_path` | str | 必填 | 输入视频路径 |
| `text` | str | 必填 | 要添加的文字内容 |
| `output_path` | str | auto | 输出视频路径（默认在原文件名后加 _floating） |
| `num_groups` | int | 7 | 飘动文字组数 |
| `duration` | float | 4.0 | 每组文字飘动时长（秒） |
| `font_size` | int | 60 | 字体大小 |
| `color` | str | 'cyan' | 文字颜色 |
| `stroke_color` | str | 'white' | 描边颜色 |
| `stroke_width` | int | 3 | 描边宽度 |
| `font` | str | 微软雅黑 | 字体文件路径 |

## 工作流程

1. 检查 moviepy 是否安装，如未安装则执行 `pip install moviepy`
2. 根据用户需求设置参数（文字内容、位置、样式）
3. 运行脚本生成新视频
4. 输出文件保存在原视频同目录，文件名添加 `_with_text` 后缀

## 使用示例

### 示例1：基础静态文字

```python
from scripts.add_text_to_video import add_text_to_video

add_text_to_video(
    video_path="path/to/video.mp4",
    text="祝灵动的游戏大卖"
)
```

### 示例2：自定义位置和样式

```python
add_text_to_video(
    video_path="path/to/video.mp4",
    text="祝灵动 Steam游戏大卖",
    font_size=100,
    color='yellow',
    stroke_color='black',
    stroke_width=4,
    vertical_position='0.66'  # 画面下方1/3处
)
```

### 示例3：闪烁文字效果

```python
add_text_to_video(
    video_path="path/to/video.mp4",
    text="重要通知",
    font_size=120,
    color='red',
    blink=True,           # 启用闪烁
    blink_speed=2.0,      # 每秒闪烁2次
    blink_min_scale=0.7,  # 缩小到70%
    blink_max_scale=1.3   # 放大到130%
)
```

### 示例4：飘动文字效果

```python
from scripts.add_floating_text import add_floating_text

add_floating_text(
    video_path="path/to/video.mp4",
    text="太冷了",
    num_groups=7,          # 7组文字
    duration=4.0,          # 每组飘动4秒
    font_size=100,
    color='cyan',          # 青色文字
    stroke_color='white',  # 白色描边
    stroke_width=3
)
```

## 注意事项

- moviepy 2.2.1+ 版本已移除 `moviepy.editor` 子模块，直接从 `moviepy` 导入
- 方法名从 `set_position()`/`set_duration()` 改为 `with_position()`/`with_duration()`
- 中文字体必须使用完整路径，不能使用字体名称
- 文字位置通过 `vertical_position` 参数控制，支持 'center'/'top'/'bottom' 或比例值
- **智能字体调整**: 脚本会自动检测字体大小是否适合视频宽度，如果过大会自动调整
- **飘动文字**：使用 `VideoClip` 的 `make_frame` 函数实现，避免 MoviePy 的 `with_position()` 函数 bug
- **飘动文字分布**：自动在上中下三个高度均匀分布，每组文字独立飘动
