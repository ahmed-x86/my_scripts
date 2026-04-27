#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess

RED = '\033[38;2;243;139;168m'
GREEN = '\033[38;2;166;227;161m'
BLUE = '\033[38;2;137;180;250m'
YELLOW = '\033[38;2;249;226;175m'
NC = '\033[0m'

def send_notification(title, message, icon):
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", title, message, "-i", icon], check=False)
        except Exception:
            pass

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print(f"{RED}❌ ffmpeg is not installed{NC}")
        sys.exit(1)

def main():
    check_ffmpeg()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}📂 Please enter the video file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name, _ = os.path.splitext(filename)

    print(f"{BLUE}📏 Select Scaling Percentage (NVIDIA NVENC):{NC}")
    options = [
        "1) 90%", "2) 80%", "3) 75%", "4) 70%",
        "5) 60%", "6) 50%", "7) 40%", "8) 30%",
        "9) 25%", "10) 20%", "11) 10%", "12) 5%"
    ]
    for opt in options:
        print(opt)

    size_choice = input("> ").strip()

    scale_map = {
        "1": ("0.90", "90"), "2": ("0.80", "80"), "3": ("0.75", "75"),
        "4": ("0.70", "70"), "5": ("0.60", "60"), "6": ("0.50", "50"),
        "7": ("0.40", "40"), "8": ("0.30", "30"), "9": ("0.25", "25"),
        "10": ("0.20", "20"), "11": ("0.10", "10"), "12": ("0.05", "5")
    }

    scale, pct = scale_map.get(size_choice, ("0.50", "50"))

    output_file = f"{name}_{pct}percent_nvenc.mkv"

    print(f"{YELLOW}⏳ Resizing and Encoding to MKV using NVIDIA NVENC...{NC}")
    send_notification("Video Resizer", f"Starting NVENC hardware encoding for {input_file}...", "video-x-generic")

    cmd = [
        "ffmpeg", "-hwaccel", "cuda", "-hide_banner", "-loglevel", "error", "-stats",
        "-i", input_file,
        "-vf", f"scale=trunc(iw*{scale}/2)*2:trunc(ih*{scale}/2)*2",
        "-c:v", "h264_nvenc", "-preset", "p4", "-c:a", "aac",
        output_file
    ]

    process = subprocess.run(cmd)

    if process.returncode == 0:
        print(f"{GREEN}✅ NVENC Encoding completed: {output_file}{NC}")
        send_notification("Success", f"NVENC Resize finished: {output_file}", "dialog-information")
    else:
        print(f"{RED}❌ NVENC Encoding failed (Check drivers/CUDA){NC}")
        send_notification("Error", "NVENC process failed!", "dialog-error")

if __name__ == "__main__":
    main()