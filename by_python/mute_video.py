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
        print(f"{BLUE}🔇 Please enter the video path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip().strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name, ext = os.path.splitext(filename)
    output_file = f"{name}_muted{ext}"

    duration = get_duration(input_file)

    print(f"{YELLOW}⏳ Removing audio losslessly...{NC}")

    cmd = [
        "ffmpeg", "-y", "-i", input_file,
        "-c:v", "copy", "-an",
        output_file
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
        print(f"{GREEN}✅ Audio removed successfully: {output_file}{NC}")
    else:
        print(f"{RED}❌ Process failed{NC}")

if __name__ == "__main__":
    main()