#!/usr/bin/env python3
"""
《代码山》第一章 - 二次元风格动画
使用PIL + FFmpeg制作
"""

import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

OUTPUT_DIR = Path("/root/.openclaw/workspace/code-mountain-full/video_anime")
OUTPUT_DIR.mkdir(exist_ok=True)

# 二次元配色
COLORS = {
    'bg_dark': (26, 26, 46),
    'bg_light': (22, 33, 62),
    'pink': (255, 107, 157),
    'blue': (78, 205, 196),
    'purple': (168, 85, 247),
    'white': (255, 255, 255),
    'green': (0, 255, 136),
    'red': (255, 68, 68),
}

WIDTH, HEIGHT = 1280, 720
FPS = 30

def create_gradient_background(width, height, color1, color2):
    """创建渐变背景"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img

def add_glow(draw, x, y, radius, color, intensity=0.5):
    """添加发光效果"""
    for r in range(radius, 0, -2):
        alpha = int(255 * intensity * (r / radius))
        glow_color = (*color, alpha)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=glow_color)

def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def create_frame_text(text, subtext=None, frame_idx=0, total_frames=30, effect=None):
    """创建文字帧"""
    # 渐变背景
    img = create_gradient_background(WIDTH, HEIGHT, COLORS['bg_dark'], COLORS['bg_light'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # 尝试加载字体
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large
    
    # 进度动画
    progress = frame_idx / total_frames
    
    # 效果：淡入
    if effect == "fade_in":
        alpha = int(255 * progress)
    elif effect == "typewriter":
        chars_to_show = int(len(text) * progress)
        text = text[:chars_to_show]
        alpha = 255
    else:
        alpha = 255
    
    # 主文字
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (WIDTH - text_width) // 2
    y = (HEIGHT - text_height) // 2 - 50
    
    # 发光效果
    if effect == "glow":
        glow_intensity = 0.5 + 0.5 * np.sin(progress * np.pi * 4)
        for offset in range(20, 0, -4):
            glow_alpha = int(100 * glow_intensity * (1 - offset/20))
            draw.text((x, y), text, font=font_large, fill=(*COLORS['pink'], glow_alpha))
    
    # 主文字（带描边）
    text_color = (*COLORS['white'], alpha)
    for dx, dy in [(-2,0), (2,0), (0,-2), (0,2)]:
        draw.text((x+dx, y+dy), text, font=font_large, fill=(*COLORS['pink'], alpha))
    draw.text((x, y), text, font=font_large, fill=text_color)
    
    # 副标题
    if subtext:
        bbox2 = draw.textbbox((0, 0), subtext, font=font_medium)
        sub_width = bbox2[2] - bbox2[0]
        x2 = (WIDTH - sub_width) // 2
        y2 = y + text_height + 30
        draw.text((x2, y2), subtext, font=font_medium, fill=(*COLORS['blue'], alpha))
    
    return img

def create_code_rain_frame(frame_idx, total_frames):
    """代码雨效果"""
    img = create_gradient_background(WIDTH, HEIGHT, COLORS['bg_dark'], (10, 10, 20))
    draw = ImageDraw.Draw(img, 'RGBA')
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Mono.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    chars = ['0', '1', '{', '}', '<', '>', '/', ';', 'int', 'def', 'return', 'import']
    np.random.seed(42)  # 固定随机种子
    
    for col in range(0, WIDTH, 20):
        speed = 2 + (col % 5)
        y = (frame_idx * speed + col * 3) % (HEIGHT + 100) - 50
        
        if y > -20 and y < HEIGHT:
            char = chars[col % len(chars)]
            # 头部亮色
            draw.text((col, y), char, font=font, fill=COLORS['green'])
            # 拖尾
            for trail in range(1, 8):
                trail_y = y - trail * 20
                if trail_y > 0:
                    alpha = int(255 * (1 - trail/8) * 0.5)
                    draw.text((col, trail_y), char, font=font, fill=(*COLORS['green'], alpha))
    
    return img

def create_error_frame(frame_idx, total_frames):
    """报错场景"""
    img = create_gradient_background(WIDTH, HEIGHT, (40, 0, 0), (20, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
    
    # 抖动效果
    shake_x = int(5 * np.sin(frame_idx * 0.5)) if frame_idx % 4 < 2 else 0
    
    # 错误框
    box_x, box_y = 200 + shake_x, 200
    draw.rounded_rectangle([box_x, box_y, box_x+880, box_y+320], radius=10, 
                          fill=(255, 0, 0, 30), outline=COLORS['red'], width=3)
    
    # 错误文字
    draw.text((box_x + 50, box_y + 50), "RuntimeError", font=font_large, fill=COLORS['red'])
    draw.text((box_x + 50, box_y + 130), "CUDA out of memory", font=font_medium, fill=COLORS['white'])
    
    return img

def create_hand_frame(frame_idx, total_frames):
    """代码之手伸出"""
    img = create_gradient_background(WIDTH, HEIGHT, COLORS['bg_dark'], COLORS['bg_light'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    progress = min(1.0, frame_idx / (total_frames * 0.6))
    
    # 手的起始位置（屏幕下方）和结束位置
    start_y = HEIGHT + 100
    end_y = HEIGHT // 2
    current_y = start_y - (start_y - end_y) * progress
    
    # 绘制手掌
    palm_x, palm_y = WIDTH // 2, int(current_y)
    
    # 发光效果
    for r in range(80, 0, -10):
        alpha = int(100 * (1 - r/80))
        draw.ellipse([palm_x-r, palm_y-r, palm_x+r, palm_y+r], 
                    fill=(*COLORS['green'], alpha))
    
    # 手掌
    draw.ellipse([palm_x-60, palm_y-80, palm_x+60, palm_y+80], 
                fill=(*COLORS['green'], 100), outline=COLORS['green'], width=3)
    
    # 手指
    for i in range(5):
        finger_x = palm_x - 80 + i * 40
        finger_y = palm_y - 100
        draw.rounded_rectangle([finger_x-15, finger_y-60, finger_x+15, finger_y+20], 
                              radius=10, fill=(*COLORS['green'], 80), 
                              outline=COLORS['green'], width=2)
    
    return img

def create_portal_frame(frame_idx, total_frames):
    """传送门效果"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['bg_dark'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    progress = frame_idx / total_frames
    center_x, center_y = WIDTH // 2, HEIGHT // 2
    
    # 旋转的光芒
    for i in range(12):
        angle = (i / 12) * 2 * np.pi + progress * 4 * np.pi
        length = 200 + 100 * np.sin(progress * np.pi * 2)
        
        x1 = center_x + np.cos(angle) * 50
        y1 = center_y + np.sin(angle) * 50
        x2 = center_x + np.cos(angle) * length
        y2 = center_y + np.sin(angle) * length
        
        color = COLORS['pink'] if i % 2 == 0 else COLORS['purple']
        draw.line([(x1, y1), (x2, y2)], fill=color, width=5)
    
    # 中心光圈
    radius = int(20 + 200 * progress)
    for r in range(radius, 0, -10):
        alpha = int(255 * (1 - r/radius) * 0.5)
        draw.ellipse([center_x-r, center_y-r, center_x+r, center_y+r],
                    fill=(*COLORS['blue'], alpha))
    
    return img

def create_ending_frame(frame_idx, total_frames):
    """结尾帧"""
    img = create_gradient_background(WIDTH, HEIGHT, COLORS['bg_light'], COLORS['bg_dark'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
    
    # 粒子效果
    np.random.seed(42)
    for _ in range(30):
        x = np.random.randint(0, WIDTH)
        y = np.random.randint(0, HEIGHT)
        size = np.random.randint(2, 8)
        color = [COLORS['pink'], COLORS['blue'], COLORS['purple']][np.random.randint(0, 3)]
        offset_y = int(frame_idx * 2 % HEIGHT)
        draw.ellipse([x, (y + offset_y) % HEIGHT, x+size, (y + offset_y) % HEIGHT + size], fill=color)
    
    # 文字
    title = "代码山"
    bbox = draw.textbbox((0, 0), title, font=font_large)
    x = (WIDTH - (bbox[2] - bbox[0])) // 2
    y = HEIGHT // 2 - 50
    
    draw.text((x, y), title, font=font_large, fill=COLORS['white'])
    draw.text((x, y+80), "To be continued...", font=font_medium, fill=COLORS['blue'])
    
    return img

def render_scene(frames_func, total_frames, scene_name):
    """渲染场景"""
    print(f"渲染场景: {scene_name} ({total_frames}帧)")
    
    temp_dir = OUTPUT_DIR / f"temp_{scene_name}"
    temp_dir.mkdir(exist_ok=True)
    
    for i in range(total_frames):
        frame = frames_func(i, total_frames)
        frame.save(temp_dir / f"frame_{i:04d}.png")
        
        if i % 10 == 0:
            print(f"  {i}/{total_frames}", end='\r')
    
    print(f"  {total_frames}/{total_frames} ✓")
    return temp_dir

def combine_scenes(scene_dirs, output_path):
    """合并所有场景"""
    print("\n合并视频...")
    
    # 收集所有帧
    all_frames = []
    for scene_dir in scene_dirs:
        frames = sorted(scene_dir.glob("frame_*.png"))
        all_frames.extend(frames)
    
    # 复制到临时目录
    temp_combine = OUTPUT_DIR / "temp_combine"
    temp_combine.mkdir(exist_ok=True)
    
    for i, frame in enumerate(all_frames):
        os.rename(frame, temp_combine / f"frame_{i:05d}.png")
    
    # 使用ffmpeg合成视频
    cmd = [
        'ffmpeg', '-y',
        '-framerate', str(FPS),
        '-pattern_type', 'glob',
        '-i', str(temp_combine / 'frame_*.png'),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-crf', '23',
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    # 清理
    for f in temp_combine.glob("*"):
        f.unlink()
    temp_combine.rmdir()
    
    return result.returncode == 0

def main():
    print("="*60)
    print("《代码山》第一章 - 二次元风格动画制作")
    print("="*60)
    
    scenes = []
    
    # 场景1: 开场标题 (3秒 = 90帧)
    print("\n[1/6] 制作开场...")
    def opening_frames(i, total):
        if i < 30:
            return create_frame_text("代码山", "Code Mountain", i, 30, "fade_in")
        elif i < 60:
            return create_frame_text("代码山", "Code Mountain", 30, 30, None)
        else:
            return create_frame_text("第一章", "commit之后不要立即push", i-60, 30, "fade_in")
    
    scene1 = render_scene(opening_frames, 90, "opening")
    scenes.append(scene1)
    
    # 场景2: 深夜加班 (2秒 = 60帧)
    print("\n[2/6] 制作深夜场景...")
    def night_frames(i, total):
        img = create_gradient_background(WIDTH, HEIGHT, COLORS['bg_dark'], COLORS['bg_light'])
        draw = ImageDraw.Draw(img)
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            font_large = ImageFont.load_default()
            font_small = font_large
        
        # 时间
        draw.text((WIDTH//2-100, 100), "02:17", font=font_large, fill=COLORS['blue'])
        draw.text((WIDTH//2-80, 180), "上海 · 张江", font=font_small, fill=COLORS['white'])
        
        # 代码行
        for j in range(5):
            y = 300 + j * 40
            width = 400 + j * 50
            draw.rectangle([200, y, 200+width, y+20], fill=(*COLORS['green'], 100))
        
        return img
    
    scene2 = render_scene(night_frames, 60, "night")
    scenes.append(scene2)
    
    # 场景3: 代码雨 (2秒 = 60帧)
    print("\n[3/6] 制作代码雨...")
    scene3 = render_scene(create_code_rain_frame, 60, "code_rain")
    scenes.append(scene3)
    
    # 场景4: 报错 (2秒 = 60帧)
    print("\n[4/6] 制作报错场景...")
    scene4 = render_scene(create_error_frame, 60, "error")
    scenes.append(scene4)
    
    # 场景5: 代码之手 (3秒 = 90帧)
    print("\n[5/6] 制作代码之手...")
    scene5 = render_scene(create_hand_frame, 90, "hand")
    scenes.append(scene5)
    
    # 场景6: 传送门+结尾 (3秒 = 90帧)
    print("\n[6/6] 制作结尾...")
    def ending_frames(i, total):
        if i < 60:
            return create_portal_frame(i, 60)
        else:
            return create_ending_frame(i-60, 30)
    
    scene6 = render_scene(ending_frames, 90, "ending")
    scenes.append(scene6)
    
    # 合并
    output_path = OUTPUT_DIR / "chapter_01_anime.mp4"
    if combine_scenes(scenes, output_path):
        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ 视频生成完成!")
        print(f"  文件: {output_path}")
        print(f"  大小: {file_size:.1f}MB")
        print(f"  时长: ~15秒")
    
    # 清理临时文件
    for scene_dir in scenes:
        for f in scene_dir.glob("*"):
            f.unlink()
        scene_dir.rmdir()

if __name__ == '__main__':
    main()
