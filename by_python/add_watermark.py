#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import re

RED = '\033[38;2;243;139;168m'
GREEN = '\033[38;2;166;227;161m'
BLUE = '\033[38;2;137;180;250m'
YELLOW = '\033[38;2;249;226;175m'
NC = '\033[0m'

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print(f"{RED}❌ ffmpeg is not installed{NC}")
        sys.exit(1)

def get_duration(input_file):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", input_file
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
        return float(out)
    except:
        return None

def main():
    check_ffmpeg()

    if len(sys.argv) >= 3:
        video_file = sys.argv[1]
        logo_file = sys.argv[2]
    else:
        print(f"{BLUE}🎬 Please enter the VIDEO file path enclosed in quotes \" \":{NC}")
        video_file = input("> ").strip().strip('"\'')
        print(f"{BLUE}🖼️ Please enter the LOGO file path (PNG with transparency) enclosed in quotes \" \":{NC}")
        logo_file = input("> ").strip().strip('"\'')

    if not os.path.isfile(video_file):
        print(f"{RED}❌ Video file does not exist: {video_file}{NC}")
        sys.exit(1)
    if not os.path.isfile(logo_file):
        print(f"{RED}❌ Logo file does not exist: {logo_file}{NC}")
        sys.exit(1)

    print(f"{BLUE}📍 Select Watermark Position:{NC}")
    print("1) Top-Left")
    print("2) Top-Right")
    print("3) Bottom-Left")
    print("4) Bottom-Right")
    print("5) Center")
    pos_choice = input("> ").strip()

    pos_map = {
        "1": "10:10",
        "2": "W-w-10:10",
        "3": "10:H-h-10",
        "4": "W-w-10:H-h-10",
        "5": "(W-w)/2:(H-h)/2"
    }
    overlay_pos = pos_map.get(pos_choice, "W-w-10:H-h-10")

    print(f"{BLUE}👻 Enter Opacity level (0.1 to 1.0) [default 1.0]:{NC}")
    opacity = input("> ").strip()
    if not opacity:
        opacity = "1.0"

    filename = os.path.basename(video_file)
    name, ext = os.path.splitext(filename)
    output_file = f"{name}_watermarked{ext}"

    duration = get_duration(video_file)

    print(f"{YELLOW}⏳ Adding watermark (Opacity: {opacity}) to position...{NC}")

    filter_str = f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[logo];[0:v][logo]overlay={overlay_pos}"
    
    cmd = [
        "ffmpeg", "-y", "-i", video_file, "-i", logo_file,
        "-filter_complex", filter_str,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "copy", output_file
    ]

    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

    for line in process.stderr:
        if duration:
            match = time_pattern.search(line)
            if match:
                hours, minutes, seconds = map(float, match.groups())
                current_time = (hours * 3600) + (minutes * 60) + seconds
                percent = min(100, int((current_time / duration) * 100))
                print(f"\r{YELLOW}🔄 Progress: {percent}%{NC}", end="", flush=True)

    process.wait()
    if duration:
        print()

    if process.returncode == 0:
        print(f"{GREEN}✅ Watermark added successfully: {output_file}{NC}")
    else:
        print(f"{RED}❌ Process failed{NC}")

if __name__ == "__main__":
    main()