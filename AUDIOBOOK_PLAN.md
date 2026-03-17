# 《代码山》有声书制作方案

## 项目概述
将《代码山》20章小说（约12万字）转换为有声书格式

## 技术方案：Edge TTS

### 选型理由
- **完全免费**：微软Edge语音合成，无额度限制
- **中文质量高**：晓晓、云希等语音自然度好
- **支持长文本**：自动切片处理
- **输出格式**：MP3 + VTT字幕

### 可用语音角色
| 语音ID | 性别 | 风格 | 适用场景 |
|--------|------|------|----------|
| zh-CN-XiaoxiaoNeural | 女 | 温暖 | 旁白、女主 |
| zh-CN-YunxiNeural | 男 | 活泼阳光 | 男主吴辰 |
| zh-CN-YunjianNeural | 男 | 激情 | 程俊、动作场景 |
| zh-CN-XiaoyiNeural | 女 | 可爱 | 豆包、 female角色 |

## 样例测试
已生成第一章开头样例：
- 文件：`audio_samples/chapter_01_sample.mp3` (1.8MB)
- 时长：约3-4分钟
- 语音：晓晓 (zh-CN-XiaoxiaoNeural)

## 制作计划

### 阶段一：样例确认（已完成）
- [x] 安装Edge TTS工具
- [x] 生成第1章样例
- [ ] 用户试听确认效果

### 阶段二：批量生成（预计1-2天）
- [ ] 编写批量转换脚本
- [ ] 处理20章全部内容
- [ ] 添加章节间过渡音效
- [ ] 生成字幕文件

### 阶段三：整合发布（预计半天）
- [ ] 合并为完整有声书（MP3 + M4B格式）
- [ ] 生成章节索引
- [ ] 上传GitHub Release
- [ ] 制作封面和元数据

## 预估产出
| 项目 | 预估数据 |
|------|----------|
| 总时长 | 约10-12小时 |
| 文件大小 | 约500-800MB |
| 格式 | MP3 (128kbps) + M4B |
| 章节 | 20章 + 片头片尾 |

## 使用方法
```bash
# 单章转换
edge-tts --voice zh-CN-XiaoxiaoNeural \
  --file chapter_01.txt \
  --write-media chapter_01.mp3 \
  --write-subtitles chapter_01.vtt

# 批量转换（脚本）
python scripts/batch_tts.py --input chapters/ --output audio/
```

## 下一步
等待用户确认样例效果，确认后开始批量制作。
