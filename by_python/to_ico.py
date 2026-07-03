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

    print(f"{BLUE}📏 Select Icon Size:{NC}")
    print("1) 16x16   (Small Favicon)")
    print("2) 32x32   (Standard Favicon)")
    print("3) 48x48   (Desktop Icon)")
    print("4) 64x64")
    print("5) 128x128")
    print("6) 256x256 (High Quality)")
    print("7) 512x512")
    print("8) 1024x1024 (Maximum)")
    print("9) Custom Size")
    
    size_choice = input("> ").strip()

    if size_choice == "1":
        size = "16"
    elif size_choice == "2":
        size = "32"
    elif size_choice == "3":
        size = "48"
    elif size_choice == "4":
        size = "64"
    elif size_choice == "5":
        size = "128"
    elif size_choice == "6":
        size = "256"
    elif size_choice == "7":
        size = "512"
    elif size_choice == "8":
        size = "1024"
    elif size_choice == "9":
        print(f"{YELLOW}Enter custom size (e.g., 200):{NC}")
        size = input("> ").strip()
        # إضافة تحقق بسيط للتأكد من أن الإدخال عبارة عن أرقام
        if not size.isdigit():
            print(f"{RED}Invalid input, defaulting to 256x256{NC}")
            size = "256"
    else:
        print(f"{RED}Invalid choice, defaulting to 256x256{NC}")
        size = "256"

    output_file = f"{name}_{size}x{size}.ico"

    print(f"{YELLOW}⏳ Generating icon [{size}x{size}]...{NC}")

    duration = get_duration(input_file)
    
    # Run ffmpeg with scale filter for icon
    cmd = ["ffmpeg", "-y", "-i", input_file, "-vf", f"scale={size}:{size}:flags=lanczos", output_file]
    
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
            # For static images, it completes instantly
            print(f"\r{YELLOW}🔄 Progress: 100%{NC}", end="", flush=True)

    process.wait()
    print() # Print a newline after progress finishes

    if process.returncode == 0:
        print(f"{GREEN}✅ Icon created successfully: {output_file}{NC}")
    else:
        print(f"{RED}❌ Icon creation failed{NC}")

if __name__ == "__main__":
    main()