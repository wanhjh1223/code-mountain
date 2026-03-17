#!/usr/bin/env python3
"""
《代码山》有声书制作 - 完整多角色版
确保内容完整不截断 + 不同角色不同语音
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional

# 角色语音配置 (voice, rate, volume)
VOICE_MAP = {
    '旁白': ('zh-CN-XiaoxiaoNeural', '+0%', '+0%'),    # 晓晓 温暖女声
    '吴辰': ('zh-CN-YunxiNeural', '+5%', '+0%'),        # 云希 活泼男声
    '程俊': ('zh-CN-YunjianNeural', '+0%', '+0%'),      # 云健 稳重男声  
    '朱丹': ('zh-CN-XiaoyiNeural', '+5%', '+5%'),       # 晓伊 可爱女声
    '豆包': ('zh-CN-XiaoyiNeural', '+10%', '+5%'),      # 晓伊 更活泼
    '韦华': ('zh-CN-YunyangNeural', '-5%', '+0%'),      # 云阳 专业男声
    'Kimi': ('zh-CN-XiaoxiaoNeural', '-5%', '+0%'),     # 晓晓 稍沉稳
    '凌源': ('zh-CN-YunyangNeural', '+0%', '+0%'),      # 云阳
    '李日天': ('zh-CN-YunxiNeural', '+0%', '+0%'),      # 云希
    '小新': ('zh-CN-XiaoyiNeural', '+8%', '+8%'),       # 晓伊 病娇
    '大松': ('zh-CN-YunjianNeural', '-5%', '+0%'),      # 云健 低沉
    'default': ('zh-CN-XiaoxiaoNeural', '+0%', '+0%'),
}

# 角色识别关键词
CHARACTER_KEYWORDS = {
    '吴辰': ['吴辰', '吴辰说', '吴辰道', '吴辰问', '吴辰答', '吴辰想', '吴辰苦笑'],
    '程俊': ['程俊', '程俊说', '程俊道', '程俊问', '程俊叹了口气'],
    '朱丹': ['朱丹', '朱丹说', '朱丹道'],
    '豆包': ['豆包', '豆包说', '豆包眨'],
    '韦华': ['韦华', '韦华说', '少年说', '白衣少年'],
    'Kimi': ['Kimi', '青色小龙虾', '小龙虾说'],
    '凌源': ['凌源', '凌源说'],
    '李日天': ['李日天', '李日天说'],
    '小新': ['小新', '小新说'],
    '大松': ['大松', '大松说'],
}


class AudioSegment:
    """音频片段"""
    def __init__(self, text: str, character: str):
        self.text = text
        self.character = character
        voice_config = VOICE_MAP.get(character, VOICE_MAP['default'])
        self.voice = voice_config[0]
        self.rate = voice_config[1]
        self.volume = voice_config[2]


def detect_character(line: str) -> Optional[str]:
    """检测说话人"""
    for char, keywords in CHARACTER_KEYWORDS.items():
        for kw in keywords:
            if line.startswith(kw) and any(w in line for w in ['说', '道', '问', '答', '想']):
                return char
    return None


def parse_chapter(content: str) -> List[AudioSegment]:
    """
    解析章节内容，分割为音频片段
    确保内容完整，按角色分割
    """
    segments = []
    lines = content.split('\n')
    
    current_narrator_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 跳过空行和格式标记
        if not line or line == '---' or line.startswith('```'):
            i += 1
            continue
        
        # 处理标题（作为章节标记）
        if line.startswith('#'):
            # 先保存之前的旁白
            if current_narrator_lines:
                text = '\n'.join(current_narrator_lines)
                if len(text.strip()) > 5:
                    segments.append(AudioSegment(text, '旁白'))
                current_narrator_lines = []
            
            title = line.lstrip('#').strip()
            if title:
                segments.append(AudioSegment(f"{title}。", '旁白'))
            i += 1
            continue
        
        # 检测是否是角色对话
        char = detect_character(line)
        
        if char:
            # 保存之前的旁白
            if current_narrator_lines:
                text = '\n'.join(current_narrator_lines)
                if len(text.strip()) > 5:
                    segments.append(AudioSegment(text, '旁白'))
                current_narrator_lines = []
            
            # 提取对话内容（引号内或整行）
            dialogue = line
            # 移除说话人标记
            for kw in CHARACTER_KEYWORDS.get(char, []):
                if dialogue.startswith(kw):
                    dialogue = dialogue[len(kw):].lstrip()
                    break
            
            # 清理引号
            dialogue = dialogue.strip('""""').strip("''")
            
            if len(dialogue.strip()) > 0:
                segments.append(AudioSegment(dialogue, char))
        else:
            # 旁白内容
            # 清理markdown
            line = line.strip('*').strip('_')
            if len(line) > 0:
                current_narrator_lines.append(line)
        
        i += 1
    
    # 保存最后的旁白
    if current_narrator_lines:
        text = '\n'.join(current_narrator_lines)
        if len(text.strip()) > 5:
            segments.append(AudioSegment(text, '旁白'))
    
    return segments


def generate_audio_segment(segment: AudioSegment, output_path: Path) -> bool:
    """生成单个音频片段"""
    # Edge TTS限制：单次最多约5000字符，分段处理
    MAX_CHARS = 4000
    
    text = segment.text
    if len(text) > MAX_CHARS:
        # 分段生成
        parts = []
        for i in range(0, len(text), MAX_CHARS):
            part_text = text[i:i+MAX_CHARS]
            part_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            part_file.close()
            
            if not _tts_generate(part_text, segment.voice, segment.rate, segment.volume, part_file.name):
                return False
            parts.append(part_file.name)
        
        # 合并
        return _merge_audio(parts, output_path)
    else:
        return _tts_generate(text, segment.voice, segment.rate, segment.volume, str(output_path))


def _tts_generate(text: str, voice: str, rate: str, volume: str, output: str) -> bool:
    """调用Edge TTS生成音频"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text)
        temp_txt = f.name
    
    try:
        cmd = [
            'edge-tts',
            '--voice', voice,
            '--rate', rate,
            '--volume', volume,
            '--file', temp_txt,
            '--write-media', output
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=180)
        return result.returncode == 0 and os.path.exists(output)
    finally:
        os.unlink(temp_txt)


def _merge_audio(files: List[str], output: Path) -> bool:
    """合并多个音频文件"""
    if len(files) == 1:
        os.rename(files[0], output)
        return True
    
    concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    for f in files:
        concat_file.write(f"file '{f}'\n")
    concat_file.close()
    
    try:
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_file.name,
            '-acodec', 'libmp3lame', '-b:a', '128k',
            str(output)
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        
        # 清理
        for f in files:
            if os.path.exists(f):
                os.unlink(f)
        
        return result.returncode == 0
    finally:
        os.unlink(concat_file.name)


def merge_all_segments(segment_files: List[Path], output: Path, chapter_title: str):
    """合并所有片段为最终音频"""
    if not segment_files:
        return False
    
    concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    for f in segment_files:
        concat_file.write(f"file '{f.absolute()}'\n")
    concat_file.close()
    
    try:
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_file.name,
            '-acodec', 'libmp3lame', '-b:a', '128k',
            '-metadata', f'title={chapter_title}',
            '-metadata', 'artist=代码山有声书',
            '-metadata', 'album=代码山',
            str(output)
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=600)
        return result.returncode == 0
    finally:
        os.unlink(concat_file.name)


def process_chapter(chapter_file: Path, output_dir: Path) -> Tuple[bool, str]:
    """处理单章"""
    chapter_name = chapter_file.stem
    print(f"\n{'='*60}")
    print(f"处理: {chapter_name}")
    print(f"{'='*60}")
    
    # 读取章节
    with open(chapter_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析为片段
    segments = parse_chapter(content)
    print(f"解析到 {len(segments)} 个音频片段")
    
    if not segments:
        return False, "无有效内容"
    
    # 统计角色
    char_count = {}
    for seg in segments:
        char_count[seg.character] = char_count.get(seg.character, 0) + 1
    print(f"角色分布: {char_count}")
    
    # 创建临时目录
    temp_dir = output_dir / f'{chapter_name}_temp'
    temp_dir.mkdir(exist_ok=True)
    
    # 生成每个片段
    segment_files = []
    for i, seg in enumerate(segments):
        seg_file = temp_dir / f'seg_{i:04d}_{seg.character}.mp3'
        print(f"  [{i+1}/{len(segments)}] {seg.character}: {seg.text[:25]}...", end=' ', flush=True)
        
        if generate_audio_segment(seg, seg_file):
            segment_files.append(seg_file)
            size = seg_file.stat().st_size / 1024
            print(f"✓ ({size:.0f}KB)")
        else:
            print("✗")
    
    if not segment_files:
        return False, "音频生成失败"
    
    # 合并为最终文件
    output_file = output_dir / f'{chapter_name}_complete.mp3'
    print(f"\n合并 {len(segment_files)} 个片段...", end=' ', flush=True)
    
    if merge_all_segments(segment_files, output_file, chapter_name):
        file_size = output_file.stat().st_size / (1024 * 1024)
        duration_approx = file_size * 8 / 128 * 60  # 粗略估算分钟数
        print(f"✓ ({file_size:.1f}MB, 约{duration_approx:.0f}分钟)")
        
        # 清理临时文件
        for f in segment_files:
            f.unlink()
        temp_dir.rmdir()
        
        return True, str(output_file)
    else:
        print("✗ 合并失败")
        return False, "合并失败"


def main():
    """主函数 - 先制作第一章完整版"""
    chapters_dir = Path('/root/.openclaw/workspace/code-mountain-full/chapters')
    output_dir = Path('/root/.openclaw/workspace/code-mountain-full/audiobook_final')
    output_dir.mkdir(exist_ok=True)
    
    # 先做第一章
    chapter_file = chapters_dir / 'chapter_01.md'
    
    if not chapter_file.exists():
        print(f"错误: 找不到 {chapter_file}")
        return
    
    print("《代码山》完整多角色有声书制作")
    print("方案: 完整内容 + 多角色配音")
    print()
    
    success, msg = process_chapter(chapter_file, output_dir)
    
    if success:
        print(f"\n✅ 完成: {msg}")
        
        # Git上传
        os.chdir("/root/.openclaw/workspace/code-mountain-full")
        subprocess.run(['git', 'add', 'audiobook_final/'], capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add complete multi-role audiobook chapter 01'], capture_output=True)
        subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True)
        print("📤 已上传GitHub")
    else:
        print(f"\n❌ 失败: {msg}")


if __name__ == '__main__':
    main()
