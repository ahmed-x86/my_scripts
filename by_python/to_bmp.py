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
        print(f"{BLUE}🖼️ Please enter the image path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]
    output_file = f"{name}.bmp"

    print(f"{BLUE}🎯 Select BMP Pixel Format:{NC}")
    options = [
        "1) RGB 24-bit (Standard)",
        "2) RGB 16-bit (565 - Useful for low-level/embedded)",
        "3) Grayscale (8-bit Gray)"
    ]
    for opt in options:
        print(opt)

    p_choice = input("> ").strip()

    p_map = {
        "1": "rgb24",
        "2": "rgb565le",
        "3": "gray"
    }
    p_fmt = p_map.get(p_choice, "rgb24")

    print(f"{YELLOW}⏳ Converting to BMP ({p_fmt})...{NC}")
    send_notification("Image Converter", f"Converting {filename} to BMP...", "image-x-generic")

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y",
        "-i", input_file,
        "-pix_fmt", p_fmt,
        output_file
    ]

    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    for line in process.stderr:
        print(f"\r{YELLOW}🔄 Processing...{NC}", end="", flush=True)

    process.wait()
    print()

    if process.returncode == 0:
        print(f"{GREEN}✅ Successfully converted to: {output_file}{NC}")
        send_notification("Success", f"Converted to {output_file}", "dialog-information")
    else:
        print(f"{RED}❌ Conversion failed{NC}")
        send_notification("Error", "BMP Conversion failed!", "dialog-error")

if __name__ == "__main__":
    main()