# YouTube 视频下载工具 (中文字幕版)

下载 YouTube 视频并自动嵌入中文字幕。

## 功能

- 下载 YouTube 视频
- 使用 Whisper 进行语音识别生成字幕
- 使用 Google 翻译将字幕翻译成中文
- 将中文字幕嵌入视频
- 自动检查和安装依赖

## 快速开始

```bash
git clone https://github.com/haha25526/youtube-dl-zh.git
cd youtube-dl-zh
pip install -r requirements.txt
python3 download.py "https://www.youtube.com/watch?v=Brj5QnphFxg" ~/Videos
```

## 依赖

- Python 3.8+
- yt-dlp
- ffmpeg
- openai-whisper

## 安装依赖

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# 安装 Python 包
pip install openai-whisper

# 安装 yt-dlp
pip install yt-dlp
```

## 用法

```bash
python3 download.py <YouTube_URL> [输出目录]
```

### 示例

```bash
# 下载到 ~/Videos 目录
python3 download.py "https://www.youtube.com/watch?v=Brj5QnphFxg" ~/Videos

# 下载到指定目录
python3 download.py "https://www.youtube.com/watch?v=Brj5QnphFxg" /path/to/output
```

## 输出

- `原视频名.mp4` - 原始视频
- `原视频名_zh.mp4` - 嵌入中文字幕的视频

## 许可证

MIT
