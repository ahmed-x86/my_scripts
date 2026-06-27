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

def check_magick():
    if not shutil.which("magick"):
        print(f"{RED}❌ ImageMagick is not installed. Please run: sudo pacman -S imagemagick{NC}")
        sys.exit(1)

def main():
    check_magick()

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
    name, _ = os.path.splitext(filename)

    orig_size_bytes = os.path.getsize(input_file)
    orig_size_kb = orig_size_bytes // 1024

    print(f"{BLUE}ℹ️ Original image size is: {YELLOW}{orig_size_kb} KB{NC}")

    print(f"{BLUE}💾 Enter target maximum size in KB (e.g., for 1MB type 1024):{NC}")
    target_kb_str = input("> ").strip()

    if not target_kb_str.isdigit():
        print(f"{RED}❌ Invalid input. Please enter numbers only.{NC}")
        sys.exit(1)

    target_kb = int(target_kb_str)

    if target_kb >= orig_size_kb:
        print(f"{RED}❌ Target size ({target_kb} KB) must be smaller than the original size ({orig_size_kb} KB).{NC}")
        sys.exit(1)

    output_file = f"{name}_{target_kb}KB.jpg"

    print(f"{YELLOW}⏳ Compressing image to ~{target_kb} KB...{NC}")

    cmd = [
        "magick", input_file,
        "-define", f"jpeg:extent={target_kb}kb",
        output_file
    ]

    process = subprocess.run(cmd)

    if process.returncode == 0:
        if os.path.exists(output_file):
            new_size_kb = os.path.getsize(output_file) // 1024
            print(f"{GREEN}✅ Image compressed successfully!{NC}")
            print(f"{GREEN}📁 Output: {output_file} ({new_size_kb} KB){NC}")
        else:
            print(f"{RED}❌ Compression failed: Output file not found{NC}")
    else:
        print(f"{RED}❌ Compression failed{NC}")

if __name__ == "__main__":
    main()