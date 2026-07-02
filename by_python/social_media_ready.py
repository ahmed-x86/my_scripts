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

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}📱 Please enter the video path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip().strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    print(f"{BLUE}📏 Select Social Media Resolution:{NC}")
    print("1) 1080x1920 (9:16 - TikTok / Reels / Shorts)")
    print("2) 1080x1350 (4:5 - Instagram Portrait)")
    print("3) 1080x1080 (1:1 - Square Post)")
    print("4) 1920x1080 (16:9 - YouTube Landscape)")
    print("5) 720x1280  (9:16 - 720p Vertical)")
    print("6) Custom Size")
    
    choice = input("> ").strip()

    if choice == "1":
        width, height = 1080, 1920
    elif choice == "2":
        width, height = 1080, 1350
    elif choice == "3":
        width, height = 1080, 1080
    elif choice == "4":
        width, height = 1920, 1080
    elif choice == "5":
        width, height = 720, 1280
    elif choice == "6":
        width = input(f"{YELLOW}Enter width (e.g., 1080):{NC} ")
        height = input(f"{YELLOW}Enter height (e.g., 1920):{NC} ")
    else:
        print(f"{RED}Invalid choice, defaulting to 1080x1920{NC}")
        width, height = 1080, 1920

    filename = os.path.basename(input_file)
    name, ext = os.path.splitext(filename)
    output_file = f"{name}_{width}x{height}{ext}"

    duration = get_duration(input_file)

    print(f"{YELLOW}⏳ Resizing video to [{width}x{height}]...{NC}")

    # FFmpeg filter to scale and pad with black bars to maintain aspect ratio
    vf_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"

    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-vf", vf_filter,
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
        print(f"{GREEN}✅ Video ready for social media: {output_file}{NC}")
    else:
        print(f"{RED}❌ Video resizing failed{NC}")

if __name__ == "__main__":
    main()