#!/usr/bin/env python3
"""
《代码山》有声书制作 - 完整版（内容不截断）
使用单一语音，但确保每章内容完整转换
"""

import os
import subprocess
import tempfile
from pathlib import Path
import time

# 配置
VOICE = "zh-CN-XiaoxiaoNeural"  # 晓晓 - 最自然的中文女声
CHAPTERS_DIR = Path("/root/.openclaw/workspace/code-mountain-full/chapters")
OUTPUT_DIR = Path("/root/.openclaw/workspace/code-mountain-full/audiobook_complete")

def clean_text(text: str) -> str:
    """清理文本，保留所有内容"""
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        # 保留标题作为章节标记
        if line.startswith('#'):
            # 移除#号但保留文字
            line = line.lstrip('#').strip()
            lines.append(line)
        # 跳过代码块标记和分隔线
        elif line == '---' or line.startswith('```'):
            continue
        # 保留其他所有内容
        elif line:
            lines.append(line)
    return '\n'.join(lines)

def generate_chapter(chapter_file: Path, output_file: Path) -> bool:
    """生成单章音频"""
    print(f"处理: {chapter_file.name}...")
    
    # 读取并清理
    with open(chapter_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    cleaned = clean_text(text)
    char_count = len(cleaned)
    print(f"  文本长度: {char_count} 字符")
    
    # Edge TTS有长度限制，需要分段处理
    # 每段约5000字符（Edge TTS限制约5000-6000字符）
    SEGMENT_SIZE = 4500
    segments = []
    
    for i in range(0, len(cleaned), SEGMENT_SIZE):
        segment_text = cleaned[i:i+SEGMENT_SIZE]
        segments.append(segment_text)
    
    print(f"  分 {len(segments)} 段处理")
    
    # 生成每段音频
    temp_files = []
    for i, seg_text in enumerate(segments):
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.close()
        temp_files.append(temp_file.name)
        
        # 创建临时文本文件
        temp_txt = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
        temp_txt.write(seg_text)
        temp_txt.close()
        
        cmd = [
            'edge-tts',
            '--voice', VOICE,
            '--file', temp_txt.name,
            '--write-media', temp_file.name
        ]
        
        print(f"  生成第 {i+1}/{len(segments)} 段...", end=' ', flush=True)
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        
        os.unlink(temp_txt.name)
        
        if result.returncode == 0:
            print("✓")
        else:
            print(f"✗ {result.stderr[:100]}")
            return False
    
    # 合并音频
    if len(temp_files) == 1:
        os.rename(temp_files[0], output_file)
    else:
        print(f"  合并 {len(temp_files)} 段音频...", end=' ', flush=True)
        # 使用ffmpeg合并
        concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        for f in temp_files:
            concat_file.write(f"file '{f}'\n")
        concat_file.close()
        
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_file.name,
            '-acodec', 'libmp3lame', '-b:a', '128k',
            '-metadata', f'title={chapter_file.stem}',
            '-metadata', 'artist=代码山有声书',
            str(output_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        os.unlink(concat_file.name)
        
        if result.returncode == 0:
            print("✓")
        else:
            print(f"✗ 合并失败")
            # 回退：使用第一个段
            os.rename(temp_files[0], output_file)
        
        # 清理临时文件
        for f in temp_files:
            if os.path.exists(f):
                os.unlink(f)
    
    file_size = output_file.stat().st_size / (1024 * 1024)
    print(f"  输出: {file_size:.1f}MB")
    return True

def git_upload(chapter_name: str):
    """上传GitHub"""
    os.chdir("/root/.openclaw/workspace/code-mountain-full")
    subprocess.run(['git', 'add', f'audiobook_complete/{chapter_name}.mp3'], capture_output=True)
    subprocess.run(['git', 'commit', '-m', f'Add complete audiobook: {chapter_name}'], capture_output=True)
    subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True)
    print(f"  📤 已上传GitHub")

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    chapter_files = sorted(CHAPTERS_DIR.glob('chapter_*.md'))
    print(f"《代码山》完整有声书制作")
    print(f"共 {len(chapter_files)} 章\n")
    
    for i, chapter_file in enumerate(chapter_files, 1):
        output_file = OUTPUT_DIR / f'{chapter_file.stem}.mp3'
        
        if output_file.exists():
            print(f"[{i}/{len(chapter_files)}] {chapter_file.stem} 已存在，跳过")
            continue
        
        print(f"\n[{i}/{len(chapter_files)}] {chapter_file.stem}")
        if generate_chapter(chapter_file, output_file):
            git_upload(chapter_file.stem)
        else:
            print(f"  失败，跳过")
        
        time.sleep(1)  # 避免限流
    
    print(f"\n全部完成！输出目录: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
