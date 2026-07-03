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
        print(f"{BLUE}📝 Please enter the subtitle file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        

    input_file = input_file.strip('"\'')


    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    # تجهيز اسم ملف المخرجات
    filename = os.path.basename(input_file)
    name, _ = os.path.splitext(filename)
    output_file = f"{name}.srt"

    print(f"{YELLOW}⏳ Converting subtitle to SRT format...{NC}")


    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_file, output_file
    ]
    

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    if result.returncode == 0:
        print(f"{GREEN}✅ Conversion completed successfully: {output_file}{NC}")
    else:
        print(f"{RED}❌ Conversion failed{NC}")

if __name__ == "__main__":
    main()