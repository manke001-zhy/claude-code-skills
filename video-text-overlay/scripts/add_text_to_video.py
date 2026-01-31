"""
为视频添加文字叠加层
使用 moviepy 库在视频中间添加文字
"""

from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def add_text_to_video(
    video_path: str,
    text: str,
    output_path: str = None,
    font_size: int = 80,
    color: str = 'white',
    stroke_color: str = 'black',
    stroke_width: int = 3,
    font: str = 'C:/Windows/fonts/msyh.ttc',  # 微软雅黑，支持中文
    duration: float = None,  # 文字显示时长（秒），None表示全程显示
    blink: bool = False,  # 是否启用闪烁效果
    blink_speed: float = 2.0,  # 闪烁速度（每秒闪烁次数）
    blink_min_scale: float = 0.7,  # 最小缩放比例
    blink_max_scale: float = 1.3,  # 最大缩放比例
    vertical_position: str = 'center'  # 垂直位置：'center', 'top', 'bottom', 或 '0.66'（从顶部算起的比例）
):
    """
    在视频中间添加文字

    参数：
        video_path: 输入视频路径
        text: 要添加的文字
        output_path: 输出视频路径（默认在原文件名后加 _with_text）
        font_size: 字体大小
        color: 文字颜色
        stroke_color: 描边颜色
        stroke_width: 描边宽度
        font: 字体文件路径（C:/Windows/fonts/msyh.ttc=微软雅黑, C:/Windows/fonts/simhei.ttf=黑体）
        duration: 文字显示时长（秒）
    """
    # 加载视频
    print(f"正在加载视频: {video_path}")
    video = VideoFileClip(video_path)

    # 设置输出路径
    if output_path is None:
        base_name = os.path.splitext(video_path)[0]
        output_path = f"{base_name}_with_text.mp4"

    # 智能调整字体大小（如果未指定或太大）
    # 根据视频宽度和文字长度自动计算合适的字体大小
    # 假设每个中文字符宽度约为字体大小的1.1倍（包括字符间距）
    text_char_count = len(text)
    max_font_size = int(video.w / (text_char_count * 1.15))  # 留5%边距

    if font_size > max_font_size:
        print(f"字体大小 {font_size} 对视频宽度 {video.w} 太大，自动调整为 {max_font_size}")
        font_size = max_font_size

    # 创建文字剪辑（使用 PIL 渲染以确保完整显示）
    print(f"正在添加文字: {text} (字体大小: {font_size})")

    # 使用 PIL 渲染文字
    try:
        # 加载字体
        pil_font = ImageFont.truetype(font, font_size)

        # 获取文字边界框
        bbox = pil_font.getbbox(text)
        left, top, right, bottom = bbox
        text_width = right - left
        text_height = bottom - top

        print(f"文字 bbox: {bbox}, 宽度: {text_width}, 高度: {text_height}")

        # 创建足够大的图像（注意：需要考虑 bbox 的 top 偏移）
        padding_top = 30
        padding_bottom = 30
        img_width = text_width + stroke_width * 4 + 40
        img_height = text_height + padding_top + padding_bottom + stroke_width * 4

        # 创建透明图像
        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 转换颜色
        color_map = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'yellow': (255, 255, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
        }
        color_rgb = color_map.get(color, (255, 255, 255)) if isinstance(color, str) else color
        stroke_rgb = color_map.get(stroke_color, (0, 0, 0)) if isinstance(stroke_color, str) else stroke_color

        # 计算绘制位置（关键：需要减去 bbox 的 top）
        x_pos = img_width // 2 - text_width // 2
        y_pos = padding_top - top

        # 绘制描边
        if stroke_width > 0:
            for x_offset in range(-stroke_width, stroke_width + 1):
                for y_offset in range(-stroke_width, stroke_width + 1):
                    if x_offset**2 + y_offset**2 <= stroke_width**2:
                        draw.text((x_pos + x_offset, y_pos + y_offset),
                                text, font=pil_font, fill=stroke_rgb + (255,))

        # 绘制文字
        draw.text((x_pos, y_pos), text, font=pil_font, fill=color_rgb + (255,))

        # 转换为 numpy 数组
        img_array = np.array(img)

        # 创建文字剪辑
        from moviepy import ImageClip
        txt_clip = ImageClip(img_array).with_duration(duration if duration else video.duration)

        print(f"文字尺寸: {txt_clip.size} (完整包含下行部分)")

    except Exception as e:
        print(f"PIL 渲染失败: {e}，使用 TextClip 后备方案")
        txt_clip = TextClip(
            text=text,
            font=font,
            font_size=font_size,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            method='label'
        )

    # 设置文字位置
    if vertical_position == 'center':
        txt_clip = txt_clip.with_position('center')
    elif vertical_position == 'top':
        txt_clip = txt_clip.with_position(('center', 0.1 * video.h))  # 上方10%位置
    elif vertical_position == 'bottom':
        txt_clip = txt_clip.with_position(('center', 0.9 * video.h))  # 下方10%位置
    else:
        # 尝试解析为比例值
        try:
            ratio = float(vertical_position)
            y_pos = ratio * video.h
            txt_clip = txt_clip.with_position(('center', y_pos))
            print(f"自定义垂直位置：从顶部 {ratio*100:.1f}% 的位置")
        except:
            txt_clip = txt_clip.with_position('center')
            print(f"无法解析位置参数 '{vertical_position}'，使用居中位置")

    txt_clip = txt_clip.with_duration(duration if duration else video.duration)

    # 添加闪烁效果（忽大忽小）
    if blink:
        import math
        def resize_func(t):
            # 使用正弦波产生平滑的缩放效果
            # t 是当前时间（秒）
            scale_range = blink_max_scale - blink_min_scale
            # 正弦波：从 -1 到 1，调整到从 min 到 max
            scale = blink_min_scale + (math.sin(t * blink_speed * 2 * math.pi) + 1) / 2 * scale_range
            return scale

        # 应用缩放效果（使用 resized 方法）
        txt_clip = txt_clip.resized(resize_func)
        print(f"已启用闪烁效果：速度 {blink_speed} 次/秒，缩放范围 {blink_min_scale}-{blink_max_scale}")

    # 合成视频
    final = CompositeVideoClip([video, txt_clip])

    # 导出视频
    print(f"正在渲染视频，保存到: {output_path}")
    final.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=video.fps,
        preset='medium'
    )

    print(f"[OK] 完成！视频已保存到: {output_path}")
    return output_path

if __name__ == "__main__":
    # 使用示例
    video_path = r"C:\Users\manke\Desktop\IMG_7417.MP4"
    text = "祝灵动的游戏大卖"

    # 基础用法（无闪烁）
    # add_text_to_video(
    #     video_path=video_path,
    #     text=text,
    #     font_size=100,
    #     color='yellow',
    #     stroke_color='black',
    #     stroke_width=4
    # )

    # 带闪烁效果的用法
    add_text_to_video(
        video_path=video_path,
        text=text,
        font_size=100,
        color='yellow',
        stroke_color='black',
        stroke_width=4,
        blink=True,  # 启用闪烁
        blink_speed=2.0,  # 每秒闪烁2次
        blink_min_scale=0.7,  # 缩小到70%
        blink_max_scale=1.3  # 放大到130%
    )
