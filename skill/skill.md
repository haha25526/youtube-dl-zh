---
name: youtube-dl-zh
description: 下载 YouTube 视频并生成中文字幕
version: 1.0.0
---

# YouTube 视频下载 + 中文字幕 Skill

## 功能

下载 YouTube 视频并自动生成嵌入中文字幕的视频。

## 触发条件

当用户要求：
- 下载 YouTube 视频
- 给视频配中文字幕
- 下载视频并翻译

## 执行流程

### 1. 检查并安装依赖

```bash
# 检查必要工具
which yt-dlp ffmpeg whisper

# 安装 ffmpeg (如缺失)
sudo apt-get update
sudo apt-get install -y ffmpeg

# 安装 Python 包 (如缺失)
pip3 install --break-system-packages openai-whisper yt-dlp
```

### 2. 下载视频

```bash
URL="<youtube_url>"
OUTPUT_DIR=~/Videos

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"
yt-dlp -o "%(title)s.%(ext)s" -f "best[ext=mp4]/best" "$URL"
```

### 3. 提取音频

```bash
VIDEO_FILE="<video_file>.mp4"
ffmpeg -i "$VIDEO_FILE" -vn -acodec libmp3lame -qscale:a 2 audio_temp.mp3 -y
```

### 4. 生成英文字幕

```bash
whisper audio_temp.mp3 --model base --language en --output_format srt --output_dir ./
```

### 5. 翻译字幕为中文

使用 Python 脚本调用 Google 翻译 API 将英文字幕翻译成中文。

### 6. 嵌入中文字幕

```bash
ffmpeg -i "$VIDEO_FILE" -vf "subtitles=subtitle_zh.srt:force_style='FontName=SimHei,FontSize=14,PrimaryColour=&HFFFFFF,BackColour=&H000000,BorderStyle=4'" -c:a copy "${VIDEO_FILE%.mp4}_zh.mp4" -y
```

### 7. 清理临时文件

```bash
rm audio_temp.mp3 audio.srt 2>/dev/null
```

## 输出

- `~/Videos/<视频名>_zh.mp4` - 带中文字幕的视频文件
- `~/Videos/<视频名>.mp4` - 原始视频文件

## 使用脚本

也可以使用独立脚本：

```bash
# 克隆仓库
git clone https://github.com/haha25526/youtube-dl-zh.git
cd youtube-dl-zh

# 安装依赖
pip install -r requirements.txt

# 运行
python3 download.py <YouTube_URL> [输出目录]
```

## 相关仓库

https://github.com/haha25526/youtube-dl-zh
