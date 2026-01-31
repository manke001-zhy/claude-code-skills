"""
使用 VideoClip 的 make_frame 函数来创建动画
避免使用 with_position() 函数
"""

from moviepy import VideoFileClip, CompositeVideoClip, VideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def create_floating_text_videoclip(
    video_path: str,
    text: str = "太冷了",
    output_path: str = None,
    num_groups: int = 7,
    duration: float = 4.0,
    font_size: int = 60,
    color: str = 'cyan',
    stroke_color: str = 'white',
    stroke_width: int = 3,
    font: str = 'C:/Windows/fonts/msyh.ttc'
):
    """
    添加多组从右到左飘动的文字（使用 VideoClip make_frame）
    """
    # 加载视频
    print(f"正在加载视频: {video_path}")
    video = VideoFileClip(video_path)

    # 设置输出路径
    if output_path is None:
        base_name = os.path.splitext(video_path)[0]
        output_path = f"{base_name}_floating_videoclip.mp4"

    # 计算字体大小
    text_char_count = len(text)
    max_font_size = int(video.w / (text_char_count * 1.3))
    if font_size > max_font_size:
        print(f"字体大小 {font_size} 自动调整为 {max_font_size}")
        font_size = max_font_size

    # 使用 PIL 创建文字图像
    pil_font = ImageFont.truetype(font, font_size)
    bbox = pil_font.getbbox(text)
    left, top, right, bottom = bbox
    text_width = right - left
    text_height = bottom - top

    padding_top = 20
    padding_bottom = 20
    img_width = text_width + stroke_width * 4 + 30
    img_height = text_height + padding_top + padding_bottom + stroke_width * 4

    # 颜色映射
    color_map = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'red': (255, 0, 0),
        'yellow': (255, 255, 0),
        'blue': (0, 0, 255),
        'green': (0, 255, 0),
        'cyan': (0, 255, 255),
    }
    color_rgb = color_map.get(color, (255, 255, 255)) if isinstance(color, str) else color
    stroke_rgb = color_map.get(stroke_color, (0, 0, 0)) if isinstance(stroke_color, str) else stroke_color

    # 计算每组的时间和位置
    available_time = video.duration - duration
    interval = available_time / (num_groups - 1) if num_groups > 1 else 0

    vertical_positions = []
    for i in range(num_groups):
        if num_groups <= 7:
            layer = i % 3
            if layer == 0:
                pos_ratio = 0.2 + (i // 3) * 0.05
            elif layer == 1:
                pos_ratio = 0.5 + (i // 3) * 0.05
            else:
                pos_ratio = 0.8 + (i // 3) * 0.05
        else:
            pos_ratio = 0.2 + (i / num_groups) * 0.6
        vertical_positions.append(pos_ratio)

    print(f"创建 {num_groups} 组飘动文字")

    # 创建文字图像数组
    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x_pos = img_width // 2 - text_width // 2
    y_draw_pos = padding_top - top

    # 绘制描边
    if stroke_width > 0:
        for x_offset in range(-stroke_width, stroke_width + 1):
            for y_offset in range(-stroke_width, stroke_width + 1):
                if x_offset**2 + y_offset**2 <= stroke_width**2:
                    draw.text((x_pos + x_offset, y_draw_pos + y_offset),
                            text, font=pil_font, fill=stroke_rgb + (255,))

    # 绘制文字
    draw.text((x_pos, y_draw_pos), text, font=pil_font, fill=color_rgb + (255,))

    text_img_array = np.array(img)

    # 为每组创建配置
    groups = []
    for i in range(num_groups):
        start_time = i * interval
        y_pos = vertical_positions[i] * video.h
        groups.append({
            'start': start_time,
            'end': start_time + duration,
            'y': y_pos
        })
        print(f"  第 {i+1} 组: {start_time:.1f}s-{start_time+duration:.1f}s, y={y_pos:.0f}px")

    # 创建一个包含所有文字的 VideoClip
    def make_frame(t):
        # 创建透明画布（RGBA）
        frame = np.zeros((video.h, video.w, 4), dtype=np.uint8)

        # 检查每个组是否应该在当前时间显示
        for group in groups:
            if group['start'] <= t < group['end']:
                # 计算当前进度
                progress = (t - group['start']) / duration
                progress = max(0, min(1, progress))

                # 计算x位置（从右到左）
                x = video.w * (1 - progress) - img_width * progress
                y = int(group['y'])

                # 确保文字在画面内（或刚好移出）
                if -img_width < x < video.w:
                    # 计算放置位置
                    x_start = int(max(0, x))
                    x_end = int(min(video.w, x + img_width))
                    y_start = y
                    y_end = y + img_height

                    # 计算源图像的对应区域
                    src_x_start = int(max(0, -x))
                    src_x_end = src_x_start + (x_end - x_start)

                    # 只有当目标区域有效时才绘制
                    if 0 <= y_start < video.h and y_end <= video.h and x_end > x_start:
                        # 复制文字图像的对应区域
                        text_slice = text_img_array[:, src_x_start:src_x_end, :]

                        # 处理边界情况
                        if text_slice.shape[1] == (x_end - x_start):
                            # Alpha blending - 保持透明度
                            alpha = text_slice[:, :, 3:4].astype(np.float32) / 255.0
                            bg = frame[y_start:y_end, x_start:x_end, :3].astype(np.float32)
                            fg = text_slice[:, :, :3].astype(np.float32)

                            blended = bg * (1 - alpha) + fg * alpha
                            frame[y_start:y_end, x_start:x_end, :3] = blended.astype(np.uint8)
                            # 保持原始 alpha 值，而不是强制设为 255
                            frame[y_start:y_end, x_start:x_end, 3] = text_slice[:, :, 3]

        return frame

    # 创建文字 VideoClip
    text_clip = VideoClip(make_frame, duration=video.duration)

    # 合成视频
    print(f"正在合成视频...")
    final = CompositeVideoClip([video, text_clip])

    # 导出
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
    video_path = r"C:\Users\manke\Desktop\IMG_7407.MP4"

    create_floating_text_videoclip(
        video_path=video_path,
        text="太冷了",
        num_groups=7,
        duration=4.0,
        font_size=100,
        color='cyan',
        stroke_color='white',
        stroke_width=3
    )
