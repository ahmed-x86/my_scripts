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

    print(f"{BLUE}📂 Please enter the FIRST video path enclosed in quotes \" \":{NC}")
    file1 = input("> ").strip().strip('"\'')

    if not os.path.isfile(file1):
        print(f"{RED}❌ File does not exist: {file1}{NC}")
        sys.exit(1)

    print(f"{BLUE}📂 Please enter the SECOND video path enclosed in quotes \" \":{NC}")
    file2 = input("> ").strip().strip('"\'')

    if not os.path.isfile(file2):
        print(f"{RED}❌ File does not exist: {file2}{NC}")
        sys.exit(1)

    filename = os.path.basename(file1)
    name, ext = os.path.splitext(filename)
    output_file = f"{name}_merged{ext}"
    list_file = "temp_concat_list.txt"

    with open(list_file, "w") as f:
        f.write(f"file '{os.path.abspath(file1)}'\n")
        f.write(f"file '{os.path.abspath(file2)}'\n")

    print(f"{YELLOW}⏳ Merging videos losslessly...${NC}")

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats",
        "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_file
    ]

    result = subprocess.run(cmd)

    if os.path.exists(list_file):
        os.remove(list_file)

    if result.returncode == 0:
        print(f"{GREEN}✅ Merging completed successfully: {output_file}{NC}")
    else:
        print(f"{RED}❌ Merging failed{NC}")

if __name__ == "__main__":
    main()