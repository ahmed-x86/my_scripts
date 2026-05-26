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

def send_notification(title, message, icon):
    """Send desktop notification using notify-send if available."""
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", title, message, "-i", icon], check=False)
        except Exception:
            pass

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
        print(f"{BLUE}🎬 Please enter the file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]
    output_file = f"{name}_davinci_amd.mov"

    print(f"{YELLOW}⏳ Converting to DaVinci Resolve (DNxHR) with AMD VAAPI Decoding...{NC}")
    send_notification("Video Converter", f"Starting AMD-assisted conversion for {input_file}...", "video-x-generic")

    duration = get_duration(input_file)
    
    # Run ffmpeg with VAAPI (AMD) decoding, DNxHD/HR, and uncompressed audio parameters
    # /dev/dri/renderD128 is the default path for the primary GPU on Linux
    cmd = [
        "ffmpeg", "-y", 
        "-hwaccel", "vaapi", "-hwaccel_device", "/dev/dri/renderD128", 
        "-i", input_file, 
        "-c:v", "dnxhd", "-profile:v", "dnxhr_sq", 
        "-pix_fmt", "yuv422p", "-c:a", "pcm_s16le", 
        output_file
    ]
    
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
            print(f"\r{YELLOW}🔄 Converting...{NC}", end="", flush=True)

    process.wait()
    print()

    if process.returncode == 0:
        print(f"{GREEN}✅ Conversion completed successfully: {output_file}{NC}")
        send_notification("Success", f"AMD-assisted conversion finished: {output_file}", "dialog-information")
    else:
        print(f"{RED}❌ Conversion failed{NC}")
        send_notification("Error", "Conversion failed!", "dialog-error")

if __name__ == "__main__":
    main()