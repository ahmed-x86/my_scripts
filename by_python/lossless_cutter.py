#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import re

# Colors
RED = '\033[38;2;243;139;168m'
GREEN = '\033[38;2;166;227;161m'
BLUE = '\033[38;2;137;180;250m'
YELLOW = '\033[38;2;249;226;175m'
NC = '\033[0m'

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print(f"{RED}❌ ffmpeg is not installed{NC}")
        sys.exit(1)

def time_to_seconds(t_str):
    try:
        parts = t_str.strip().split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        else:
            return float(parts[0])
    except:
        return None

def main():
    check_ffmpeg()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}✂️ Enter file path to cut:{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    print(f"{BLUE}⏱️ Enter start time (HH:MM:SS) e.g., 00:01:52:{NC}")
    start_time = input("> ").strip()

    print(f"{BLUE}⏱️ Enter end time (HH:MM:SS) e.g., 00:02:03:{NC}")
    end_time = input("> ").strip()

    filename = os.path.basename(input_file)
    name, ext = os.path.splitext(filename)
    output_file = f"{name}_cut{ext}"

    print(f"{YELLOW}⏳ Cutting file losslessly from [{start_time}] to [{end_time}]...{NC}")

    # حساب مدة المقطع الجديد لكي يعمل شريط التقدم
    s_sec = time_to_seconds(start_time)
    e_sec = time_to_seconds(end_time)
    
    duration = None
    if s_sec is not None and e_sec is not None and e_sec > s_sec:
        duration = e_sec - s_sec

    # تشغيل ffmpeg
    cmd = [
        "ffmpeg", "-y", 
        "-i", input_file,
        "-ss", start_time,
        "-to", end_time,
        "-c", "copy",
        output_file
    ]
    
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    
    # منطق شريط التقدم
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
        print() # سطر جديد بعد انتهاء شريط التقدم

    if process.returncode == 0:
        print(f"{GREEN}✅ Successfully cut to: {output_file}{NC}")
    else:
        print(f"{RED}❌ Cutting failed{NC}")

if __name__ == "__main__":
    main()