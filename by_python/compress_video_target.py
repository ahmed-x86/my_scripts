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

def check_requirements():
    for cmd in ["ffmpeg", "ffprobe"]:
        if not shutil.which(cmd):
            print(f"{RED}❌ {cmd} is not installed{NC}")
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

def run_ffmpeg_pass(cmd, duration, pass_num):
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

    for line in process.stderr:
        if duration:
            match = time_pattern.search(line)
            if match:
                hours, minutes, seconds = map(float, match.groups())
                current_time = (hours * 3600) + (minutes * 60) + seconds
                percent = min(100, int((current_time / duration) * 100))
                print(f"\r{YELLOW}🔄 Pass {pass_num} Progress: {percent}%{NC}", end="", flush=True)
    
    process.wait()
    print()
    return process.returncode

def main():
    check_requirements()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}🎞️ Please enter the video path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip().strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    print(f"{BLUE}🎯 Enter target file size in MB (e.g., 8, 25):{NC}")
    try:
        target_size_mb = float(input("> ").strip())
    except ValueError:
        print(f"{RED}❌ Invalid size{NC}")
        sys.exit(1)

    duration = get_duration(input_file)
    if not duration:
        print(f"{RED}❌ Could not determine video duration{NC}")
        sys.exit(1)

    audio_bitrate = 128
    video_bitrate = int(((target_size_mb * 8192) / duration) - audio_bitrate)
    if video_bitrate < 10:
        video_bitrate = 10

    filename = os.path.basename(input_file)
    name, _ = os.path.splitext(filename)
    output_file = f"{name}_{int(target_size_mb)}MB.mp4"

    print(f"{YELLOW}⏳ Compressing to ~{target_size_mb}MB (Video: {video_bitrate}kbps, Audio: {audio_bitrate}kbps)...{NC}")

    pass1_cmd = [
        "ffmpeg", "-y", "-i", input_file, "-c:v", "libx264",
        "-b:v", f"{video_bitrate}k", "-pass", "1", "-an", "-f", "mp4", os.devnull
    ]
    
    if run_ffmpeg_pass(pass1_cmd, duration, 1) != 0:
        print(f"{RED}❌ Pass 1 failed{NC}")
        sys.exit(1)

    pass2_cmd = [
        "ffmpeg", "-y", "-i", input_file, "-c:v", "libx264",
        "-b:v", f"{video_bitrate}k", "-pass", "2", "-c:a", "aac",
        "-b:a", f"{audio_bitrate}k", output_file
    ]

    if run_ffmpeg_pass(pass2_cmd, duration, 2) == 0:
        print(f"{GREEN}✅ Compression completed: {output_file}{NC}")
    else:
        print(f"{RED}❌ Compression failed{NC}")

    for f in ["ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()