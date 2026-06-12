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

def send_notification(title, message, icon):
    """Send desktop notification using notify-send if available."""
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", title, message, "-i", icon], check=False)
        except Exception:
            pass

def check_ffmpeg():
    
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print(f"{RED}❌ ffmpeg or ffprobe is not installed{NC}")
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
        print(f"{BLUE}🎞️ Please enter the video path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    print(f"{BLUE}🎯 Enter number of columns (e.g., 4) [Default: 4]:{NC}")
    cols = input("> ").strip()
    cols = int(cols) if cols else 4

    print(f"{BLUE}🎯 Enter number of rows (e.g., 4) [Default: 4]:{NC}")
    rows = input("> ").strip()
    rows = int(rows) if rows else 4

    print(f"{BLUE}🎯 Enter thumbnail width in pixels (e.g., 320) [Default: 320]:{NC}")
    thumb_width = input("> ").strip()
    thumb_width = int(thumb_width) if thumb_width else 320

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]
    output_file = f"{name}_grid_{cols}x{rows}.jpg"

    duration = get_duration(input_file)
    
    
    if duration is None or duration <= 0:
        print(f"{RED}❌ Error: Could not determine video duration.{NC}")
        sys.exit(1)


    total_tiles = cols * rows
    if total_tiles <= 0:
        total_tiles = 16
    
    interval = f"{duration / total_tiles:.3f}"

    print(f"{YELLOW}⏳ Generating {cols}x{rows} thumbnail grid...{NC}")

    cmd = [
        "ffmpeg", "-y", 
        "-hide_banner", 
        "-loglevel", "error", 
        "-stats", 
        "-i", input_file, 
        "-vf", f"fps=1/{interval},scale={thumb_width}:-1,tile={cols}x{rows}", 
        "-vframes", "1", 
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
            else:
                print(f"\r{YELLOW}🔄 Converting...{NC}", end="", flush=True)
        else:
             print(f"\r{YELLOW}🔄 Converting...{NC}", end="", flush=True)

    process.wait()
    print() 

    if process.returncode == 0:
        print(f"{GREEN}✅ Grid completed: {output_file}{NC}")
        send_notification("Success", f"Grid generation completed: {output_file}", "dialog-information")
    else:
        print(f"{RED}❌ Grid generation failed{NC}")
        send_notification("Error", "Grid generation failed!", "dialog-error")

if __name__ == "__main__":
    main()