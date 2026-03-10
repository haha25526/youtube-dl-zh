#!/usr/bin/env python3
"""
YouTube 视频下载工具 - 下载视频并生成中文字幕

用法:
    python3 download.py <YouTube_URL> [输出目录]

示例:
    python3 download.py "https://www.youtube.com/watch?v=Brj5QnphFxg" ~/Videos
"""

import os
import sys
import re
import json
import urllib.request
import urllib.parse
import subprocess
import shutil


def check_dependency(name, install_cmd=None):
    """检查依赖是否安装，未安装则尝试安装"""
    if shutil.which(name):
        return True

    print(f"未找到 {name}，尝试安装...")

    if install_cmd:
        result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{name} 安装成功")
            return shutil.which(name) is not None
        else:
            print(f"{name} 安装失败：{result.stderr}")
            return False
    return False


def check_dependencies():
    """检查所有依赖"""
    deps = {
        'yt-dlp': 'pip install --user yt-dlp',
        'ffmpeg': None,  # 需要系统安装
        'whisper': 'pip install --user openai-whisper',
    }

    missing = []
    for name, install_cmd in deps.items():
        if not check_dependency(name, install_cmd):
            missing.append(name)

    if missing:
        print(f"\n缺少依赖：{', '.join(missing)}")
        if 'ffmpeg' in missing:
            print("请手动安装 ffmpeg:")
            print("  Ubuntu/Debian: sudo apt install ffmpeg")
            print("  macOS: brew install ffmpeg")
        return False
    return True


def run_command(cmd, cwd=None):
    """运行 shell 命令"""
    print(f"执行：{cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0


def translate_text(text):
    """使用 Google 翻译 API 翻译文本"""
    if not text.strip():
        return text

    url = f"https://translate.googleapis.com/translate_a/t?client=gtx&sl=en&tl=zh-CN&dt=t&q={urllib.parse.quote(text)}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        resp = opener.open(req, timeout=10)
        data = json.loads(resp.read())
        return ''.join([sentence[0] for sentence in data[0]])
    except Exception as e:
        print(f"翻译失败：{e}")
        return text


def translate_srt(input_file, output_file):
    """翻译 SRT 字幕文件"""
    print(f"正在翻译字幕：{input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    result = []
    count = 0

    for line in lines:
        if not line.strip() or re.match(r'^\d+$', line.strip()) or re.match(r'^\d{2}:\d{2}:\d{2}', line.strip()):
            result.append(line)
        else:
            translated = translate_text(line)
            count += 1
            print(f"  [{count}] {line[:50]}... -> {translated[:50]}...")
            result.append(translated)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result))

    print(f"翻译完成：{output_file}")


def download_video(url, output_dir):
    """下载 YouTube 视频"""
    os.makedirs(output_dir, exist_ok=True)

    # 使用 yt-dlp 下载视频
    cmd = f'yt-dlp -o "%(title)s.%(ext)s" -f "best[ext=mp4]/best" "{url}"'
    print(f"正在下载视频...")
    if not run_command(cmd, cwd=output_dir):
        return None

    # 查找下载的视频文件
    video_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
    if not video_files:
        print("未找到下载的视频文件")
        return None

    video_file = os.path.join(output_dir, video_files[0])
    print(f"视频已下载：{video_file}")
    return video_file


def extract_audio(video_file, output_dir):
    """从视频提取音频"""
    audio_file = os.path.join(output_dir, 'audio_temp.mp3')
    cmd = f'ffmpeg -i "{video_file}" -vn -acodec libmp3lame -qscale:a 2 "{audio_file}" -y'
    print(f"正在提取音频...")
    run_command(cmd)
    if os.path.exists(audio_file):
        return audio_file
    return None


def generate_subtitle(audio_file, output_dir):
    """使用 whisper 生成字幕"""
    cmd = f'whisper "{audio_file}" --model base --language en --output_format srt --output_dir "{output_dir}"'
    print(f"正在生成字幕...")
    run_command(cmd)

    # 查找生成的字幕文件
    srt_files = [f for f in os.listdir(output_dir) if f.endswith('.srt') and f.startswith('audio')]
    if srt_files:
        return os.path.join(output_dir, srt_files[0])
    return None


def embed_subtitle(video_file, subtitle_file, output_file):
    """将字幕嵌入视频"""
    cmd = f'ffmpeg -i "{video_file}" -vf "subtitles={subtitle_file}:force_style=\'FontName=SimHei,FontSize=14,PrimaryColour=&HFFFFFF,BackColour=&H000000,BorderStyle=4\'" -c:a copy "{output_file}" -y'
    print(f"正在嵌入字幕...")
    run_command(cmd)
    if os.path.exists(output_file):
        return output_file
    return None


def cleanup(output_dir):
    """清理临时文件"""
    temp_files = ['audio_temp.mp3', 'audio.srt']
    for f in temp_files:
        path = os.path.join(output_dir, f)
        if os.path.exists(path):
            os.remove(path)
            print(f"清理临时文件：{f}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/Videos')

    print(f"YouTube 视频下载工具")
    print(f"URL: {url}")
    print(f"输出目录：{output_dir}")
    print("-" * 50)

    # 1. 下载视频
    video_file = download_video(url, output_dir)
    if not video_file:
        print("视频下载失败")
        sys.exit(1)

    # 2. 提取音频
    audio_file = extract_audio(video_file, output_dir)
    if not audio_file:
        print("音频提取失败")
        sys.exit(1)

    # 3. 生成英文字幕
    en_subtitle = generate_subtitle(audio_file, output_dir)
    if not en_subtitle:
        print("字幕生成失败")
        sys.exit(1)

    # 4. 翻译字幕
    zh_subtitle = os.path.join(output_dir, 'subtitle_zh.srt')
    translate_srt(en_subtitle, zh_subtitle)

    # 5. 嵌入字幕
    base_name = os.path.splitext(os.path.basename(video_file))[0]
    output_file = os.path.join(output_dir, f'{base_name}_zh.mp4')
    embed_subtitle(video_file, zh_subtitle, output_file)

    # 6. 清理
    cleanup(output_dir)

    print("-" * 50)
    print(f"完成！输出文件：{output_file}")


if __name__ == '__main__':
    main()
