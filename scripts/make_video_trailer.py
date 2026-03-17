#!/usr/bin/env python3
"""
《代码山》第一章 - 短视频制作 (纯FFmpeg版本)
无需ImageMagick
"""

import os
import subprocess
from pathlib import Path

OUTPUT_DIR = Path("/root/.openclaw/workspace/code-mountain-full/video")
OUTPUT_DIR.mkdir(exist_ok=True)

def create_video():
    """创建视频"""
    
    print("="*60)
    print("《代码山》第一章 - 短视频制作")
    print("="*60)
    
    # 场景文本和时长
    scenes = [
        ("《代码山》", 3),
        ("第一章", 2),
        ("commit之后不要立即push", 3),
        ("凌晨两点十七分", 2.5),
        ("上海张江", 2),
        ("吴辰盯着报错", 2.5),
        ("CUDA out of memory", 2.5),
        ("我allocate你大爷", 2.5),
        ("连续加班第七天", 2.5),
        ("屏幕突然闪了一下", 2.5),
        ("深渊眨了眨眼", 2.5),
        ("屏幕里伸出了一只手", 3),
        ("纯黑代码构成", 2.5),
        ("欢迎来到玳瑁山界", 3),
        ("你已经死了", 3),
    ]
    
    total_duration = sum(d for _, d in scenes)
    print(f"\n视频信息: {len(scenes)} 个场景, 总时长 {total_duration} 秒")
    
    # 创建复杂的滤镜链
    print("\n[1/2] 创建视频滤镜...")
    
    filter_parts = []
    current_time = 0
    
    for i, (text, duration) in enumerate(scenes):
        # 计算起始和结束时间
        start = current_time
        end = current_time + duration
        
        # 转义特殊字符
        safe_text = text.replace(":", "\\:").replace("'", "\\'")
        
        # 创建文字滤镜
        filter_parts.append(
            f"drawtext=text='{safe_text}':"
            f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"fontsize=48:fontcolor=white:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"enable='between(t\\,{start}\\,{end})'"
        )
        
        current_time += duration
    
    # 合并滤镜
    filter_complex = ','.join(filter_parts)
    
    print("✓ 滤镜创建完成")
    
    # 使用ffmpeg生成视频
    print("\n[2/2] 生成视频...")
    
    output_path = OUTPUT_DIR / "chapter_01_trailer.mp4"
    
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', 'color=c=#0a0a14:s=1280x720:d=' + str(total_duration),
        '-vf', filter_complex,
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-r', '24',
        '-crf', '23',
        str(output_path)
    ]
    
    print(f"执行: ffmpeg ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and output_path.exists():
        file_size = output_path.stat().st_size / (1024 * 1024)
        print(f"\n✓ 视频制作完成!")
        print(f"  文件: {output_path}")
        print(f"  大小: {file_size:.1f}MB")
        print(f"  时长: {total_duration}秒")
        print(f"  分辨率: 1280x720")
        return True
    else:
        print(f"\n✗ 视频生成失败")
        print(f"错误: {result.stderr[:500]}")
        return False

if __name__ == '__main__':
    create_video()
