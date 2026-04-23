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
        print(f"{BLUE}🏷️ Please enter the file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip().strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name, ext = os.path.splitext(filename)
    output_file = f"{name}_nometadata{ext}"

    print(f"{YELLOW}⏳ Removing metadata losslessly...{NC}")

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_file, "-map_metadata", "-1", "-c", "copy", output_file
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"{GREEN}✅ Metadata removed successfully: {output_file}{NC}")
    else:
        print(f"{RED}❌ Metadata removal failed{NC}")

if __name__ == "__main__":
    main()