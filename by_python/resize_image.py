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
    name, extension = os.path.splitext(filename)
    extension = extension.lstrip('.')

    print(f"{BLUE}📏 Select Scaling Percentage:{NC}")
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

    if size_choice not in scale_map:
        print(f"{RED}Invalid choice, defaulting to 50%{NC}")

    output_file = f"{name}_{pct}percent.{extension}"

    print(f"{YELLOW}⏳ Resizing image to {pct}%...{NC}")

    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats", "-y",
        "-i", input_file,
        "-vf", f"scale=trunc(iw*{scale}):trunc(ih*{scale})",
        output_file
    ]

    process = subprocess.run(cmd)

    if process.returncode == 0:
        print(f"{GREEN}✅ Image resized successfully: {output_file}{NC}")
    else:
        print(f"{RED}❌ Resizing failed{NC}")

if __name__ == "__main__":
    main()