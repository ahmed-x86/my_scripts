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
        print(f"{BLUE}🖼️ Please enter the image path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]
    output_file = f"{name}.jpg"

    print(f"{BLUE}🎯 Select JPG Quality:{NC}")
    print("1) Standard (Balanced size)")
    print("2) High Quality (Low compression)")
    print("3) Maximum (Best quality, larger file)")
    
    q_choice = input("> ").strip()

    if q_choice == "1":
        q_val = "5"
    elif q_choice == "2":
        q_val = "2"
    elif q_choice == "3":
        q_val = "1"
    else:
        q_val = "2"

    print(f"{YELLOW}⏳ Converting to JPG...{NC}")

    duration = get_duration(input_file)
    
    # Run ffmpeg with JPG quality parameter
    cmd = ["ffmpeg", "-y", "-i", input_file, "-q:v", q_val, output_file]
    
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    
    # Progress bar logic
    for line in process.stderr:
        if duration:
            match = time_pattern.search(line)
            if match:
                hours, minutes, seconds = map(float, match.groups())
                current_time = (hours * 3600) + (minutes * 60) + seconds
                percent = min(100, int((current_time / duration) * 100))
                print(f"\r{YELLOW}🔄 Progress: {percent}%{NC}", end="", flush=True)
        else:
            # For static images (duration is None), it converts instantly
            print(f"\r{YELLOW}🔄 Progress: 100%{NC}", end="", flush=True)

    process.wait()
    print() # Print a newline after progress finishes

    if process.returncode == 0:
        print(f"{GREEN}✅ Successfully converted to: {output_file}{NC}")
    else:
        print(f"{RED}❌ Conversion failed{NC}")

if __name__ == "__main__":
    main()