#!/usr/bin/env python3
"""
《代码山》有声书批量制作脚本
每章完成后自动上传GitHub
"""

import os
import subprocess
import time
from pathlib import Path

# 配置
CHAPTERS_DIR = Path("/root/.openclaw/workspace/code-mountain-full/chapters")
AUDIO_DIR = Path("/root/.openclaw/workspace/code-mountain-full/audiobook")
VOICE = "zh-CN-XiaoxiaoNeural"  # 晓晓 - 温暖女声
RATE = "+0%"  # 语速
VOLUME = "+0%"  # 音量

def clean_text(text):
    """清理文本，移除markdown标记"""
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        # 移除标题标记
        if line.startswith('#'):
            line = line.lstrip('#').strip()
        # 移除分隔线
        if line.strip() == '---':
            continue
        # 移除代码块标记
        if line.strip().startswith('```'):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)

def convert_chapter(chapter_file, output_file):
    """转换单章为音频"""
    # 读取并清理文本
    with open(chapter_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    cleaned_text = clean_text(text)
    
    # 创建临时文本文件
    temp_file = output_file.with_suffix('.txt')
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)
    
    # 使用edge-tts转换
    cmd = [
        'edge-tts',
        '--voice', VOICE,
        '--rate', RATE,
        '--volume', VOLUME,
        '--file', str(temp_file),
        '--write-media', str(output_file),
        '--write-subtitles', str(output_file.with_suffix('.vtt'))
    ]
    
    print(f"正在转换: {chapter_file.name} -> {output_file.name}")
    start_time = time.time()
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    elapsed = time.time() - start_time
    
    # 清理临时文件
    temp_file.unlink(missing_ok=True)
    
    if result.returncode == 0:
        file_size = output_file.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ 完成: {output_file.name} ({file_size:.1f}MB, {elapsed:.1f}秒)")
        return True
    else:
        print(f"❌ 失败: {result.stderr}")
        return False

def git_upload(chapter_name):
    """上传单章到GitHub"""
    os.chdir("/root/.openclaw/workspace/code-mountain-full")
    
    # 添加文件
    subprocess.run(['git', 'add', f'audiobook/{chapter_name}*'], capture_output=True)
    
    # 提交
    result = subprocess.run(
        ['git', 'commit', '-m', f'Add audiobook: {chapter_name}'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0 or 'nothing to commit' in result.stderr:
        # 推送
        subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True)
        print(f"📤 已上传GitHub: {chapter_name}")
        return True
    return False

def main():
    """主函数"""
    # 创建输出目录
    AUDIO_DIR.mkdir(exist_ok=True)
    
    # 获取所有章节文件
    chapter_files = sorted(CHAPTERS_DIR.glob("chapter_*.md"))
    total = len(chapter_files)
    
    print(f"=" * 50)
    print(f"《代码山》有声书制作开始")
    print(f"总计: {total}章")
    print(f"语音: {VOICE}")
    print(f"=" * 50)
    
    success_count = 0
    
    for i, chapter_file in enumerate(chapter_files, 1):
        chapter_name = chapter_file.stem  # chapter_01
        output_file = AUDIO_DIR / f"{chapter_name}.mp3"
        
        # 检查是否已存在
        if output_file.exists():
            print(f"⏭️  跳过: {chapter_name} (已存在)")
            success_count += 1
            continue
        
        print(f"\n[{i}/{total}] 处理 {chapter_name}...")
        
        # 转换
        if convert_chapter(chapter_file, output_file):
            # 上传
            git_upload(chapter_name)
            success_count += 1
            
            # 短暂休息，避免API限制
            time.sleep(2)
        else:
            print(f"⚠️  {chapter_name} 转换失败，继续下一章")
    
    print(f"\n{'=' * 50}")
    print(f"制作完成: {success_count}/{total}章")
    print(f"输出目录: {AUDIO_DIR}")
    print(f"{'=' * 50}")

if __name__ == '__main__':
    main()
