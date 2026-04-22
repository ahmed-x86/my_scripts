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
        print(f"{BLUE}🖼️ Please enter the video file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]

    print(f"{BLUE}Select extraction mode:{NC}")
    print("1) Single frame at specific time (e.g., 00:01:23)")
    print("2) Multiple frames (e.g., 1 frame per second)")
    
    mode = input("> ").strip()

    duration = get_duration(input_file)

    if mode == "1":
        print(f"{YELLOW}Enter timestamp (HH:MM:SS):{NC}")
        timestamp = input("> ").strip()
        
        # Replace colons to make the filename safe for all OS
        safe_timestamp = timestamp.replace(":", "_")
        output_file = f"{name}_frame_{safe_timestamp}.jpg"
        
        print(f"{YELLOW}⏳ Extracting frame...{NC}")
        
        # Placing -ss before -i makes seeking much faster
        cmd = ["ffmpeg", "-y", "-ss", timestamp, "-i", input_file, "-vframes", "1", "-q:v", "2", output_file]
        
    elif mode == "2":
        print(f"{YELLOW}Enter fps (e.g., 1 for 1 frame/sec, 0.1 for 1 frame/10sec):{NC}")
        fps = input("> ").strip()
        
        out_dir = f"{name}_frames"
        os.makedirs(out_dir, exist_ok=True)
        output_file = os.path.join(out_dir, "frame_%04d.jpg")
        
        print(f"{YELLOW}⏳ Extracting frames into /{out_dir} ...{NC}")
        
        cmd = ["ffmpeg", "-y", "-i", input_file, "-vf", f"fps={fps}", "-q:v", "2", output_file]
        
    else:
        print(f"{RED}❌ Invalid option{NC}")
        sys.exit(1)

    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    
    # Progress bar logic
    for line in process.stderr:
        if mode == "2" and duration:
            match = time_pattern.search(line)
            if match:
                hours, minutes, seconds = map(float, match.groups())
                current_time = (hours * 3600) + (minutes * 60) + seconds
                percent = min(100, int((current_time / duration) * 100))
                print(f"\r{YELLOW}🔄 Progress: {percent}%{NC}", end="", flush=True)
        else:
            print(f"\r{YELLOW}🔄 Extracting...{NC}", end="", flush=True)

    process.wait()
    print() # Print a newline after progress finishes

    if process.returncode == 0:
        print(f"{GREEN}✅ Extraction completed successfully{NC}")
    else:
        print(f"{RED}❌ Extraction failed{NC}")

if __name__ == "__main__":
    main()