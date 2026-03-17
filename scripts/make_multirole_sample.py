#!/usr/bin/env python3
"""
制作多角色样例（第一章片段）
展示吴辰、程俊、朱丹的不同声音
"""

import os
import subprocess
import tempfile
from pathlib import Path

# 角色语音配置
VOICES = {
    '旁白': ('zh-CN-XiaoxiaoNeural', '+0%'),  # 晓晓 温暖
    '吴辰': ('zh-CN-YunxiNeural', '+0%'),      # 云希 活泼男声
    '程俊': ('zh-CN-YunjianNeural', '+0%'),   # 云健 稳重
    '朱丹': ('zh-CN-XiaoyiNeural', '+0%'),    # 晓伊 可爱女声
}

# 第一章片段（包含多角色对话）
SAMPLE_TEXT = """
[旁白]
凌晨两点十七分，上海张江。
吴辰盯着屏幕上那行报错，感觉自己的灵魂正在从眼眶里缓缓飘出来。
这是他连续加班的第七天。

[吴辰]
我allocate你大爷。

[旁白]
他机械地端起冷掉的咖啡，发现杯底沉着一层白色絮状物。
屏幕右下角的时间显示两点十七分。

[程俊]
吴辰，你还没走？

[旁白]
程俊从茶水间探出头，手里端着两杯速溶咖啡。

[吴辰]
最后一个bug，改完这个就commit。

[程俊]
你两小时前就这么说的。

[吴辰]
这次是真的。

[程俊]
你三小时前也这么说的。

[旁白]
吴辰决定不反驳。
朱丹跟着程俊后面，抱着一箱刚外卖到的关东煮。

[朱丹]
关东煮还热着，萝卜煮得很烂，你最爱的那种。
"""

def generate_segment(text, voice, rate, output_file):
    """生成单个片段"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text)
        temp_txt = f.name
    
    try:
        cmd = [
            'edge-tts',
            '--voice', voice,
            '--rate', rate,
            '--file', temp_txt,
            '--write-media', output_file
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        return result.returncode == 0
    finally:
        os.unlink(temp_txt)

def main():
    output_dir = Path('/root/.openclaw/workspace/code-mountain-full/audio_samples')
    output_dir.mkdir(exist_ok=True)
    
    # 解析片段
    segments = []
    current_role = None
    current_text = []
    
    for line in SAMPLE_TEXT.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('[') and line.endswith(']'):
            # 保存之前的片段
            if current_role and current_text:
                segments.append((current_role, '\n'.join(current_text)))
            # 开始新角色
            current_role = line[1:-1]
            current_text = []
        else:
            current_text.append(line)
    
    # 保存最后一个片段
    if current_role and current_text:
        segments.append((current_role, '\n'.join(current_text)))
    
    print(f"生成多角色样例，共 {len(segments)} 个片段")
    
    # 生成每个片段
    temp_files = []
    for i, (role, text) in enumerate(segments):
        if role not in VOICES:
            role = '旁白'
        voice, rate = VOICES[role]
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_file.close()
        
        print(f"[{i+1}/{len(segments)}] {role}: {text[:20]}...", end=' ')
        if generate_segment(text, voice, rate, temp_file.name):
            temp_files.append(temp_file.name)
            print("✓")
        else:
            print("✗")
    
    # 合并
    if temp_files:
        output_file = output_dir / 'chapter_01_multirole_sample.mp3'
        
        # 创建concat列表
        concat_list = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        for f in temp_files:
            concat_list.write(f"file '{f}'\n")
        concat_list.close()
        
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', concat_list.name,
            '-acodec', 'libmp3lame', '-b:a', '128k',
            str(output_file)
        ]
        
        print(f"\n合并音频...", end=' ')
        result = subprocess.run(cmd, capture_output=True)
        
        os.unlink(concat_list.name)
        for f in temp_files:
            os.unlink(f)
        
        if result.returncode == 0:
            size = output_file.stat().st_size / (1024 * 1024)
            print(f"✓ ({size:.1f}MB)")
            print(f"\n样例文件: {output_file}")
            print("\n角色分配:")
            for role, (voice, _) in VOICES.items():
                print(f"  {role}: {voice}")
        else:
            print(f"✗ 合并失败")

if __name__ == '__main__':
    main()
