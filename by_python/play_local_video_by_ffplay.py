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

def check_requirements():
    for cmd in ["ffplay", "ffprobe"]:
        if not shutil.which(cmd):
            print(f"{RED}❌ {cmd} is not installed.{NC}")
            sys.exit(1)

def get_gpu_info():
    try:
        return subprocess.check_output(["lspci"], text=True).lower()
    except:
        return ""

def get_video_codec(input_file):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name",
        "-of", "default=noprint_wrappers=1:nokey=1", input_file
    ]
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except:
        return None

def main():
    check_requirements()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}📂 Please enter the video file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip().strip('"\'')

    if not input_file:
        print(f"{RED}❌ Path cannot be empty{NC}")
        sys.exit(1)

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    options = ["CPU (Software Decoding)"]
    hwdec_args = ["no"]

    gpu_info = get_gpu_info()

    if "intel" in gpu_info:
        options.append("Intel GPU")
        hwdec_args.append("qsv")

    if "amd" in gpu_info or "ati" in gpu_info:
        options.append("AMD GPU (Fallback to CPU in ffplay)")
        hwdec_args.append("no")

    if "nvidia" in gpu_info:
        options.append("Nvidia GPU")
        hwdec_args.append("cuvid")

    print(f"{BLUE}🖥️  Select Decoding Device:{NC}")
    for i, opt in enumerate(options):
        print(f"{YELLOW}{i+1}. {opt}{NC}")

    try:
        choice = int(input("> ").strip())
        index = choice - 1
        if 0 <= index < len(options):
            selected_name = options[index]
            hw_arg = hwdec_args[index]
        else:
            raise ValueError
    except:
        print(f"{RED}❌ Invalid selection. Defaulting to CPU.{NC}")
        selected_name = "CPU"
        hw_arg = "no"

    print(f"{YELLOW}⏳ Probing video codec...{NC}")
    codec = get_video_codec(input_file)
    
    ffplay_vcodec = []

    if hw_arg == "cuvid":
        if codec in ["h264", "hevc", "vp9"]:
            ffplay_vcodec = ["-vcodec", f"{codec}_cuvid"]
        else:
            print(f"{YELLOW}⚠️ Unsupported codec ({codec}) for Nvidia HW decoding. Using CPU.{NC}")
    elif hw_arg == "qsv":
        if codec in ["h264", "hevc"]:
            ffplay_vcodec = ["-vcodec", f"{codec}_qsv"]
        else:
            print(f"{YELLOW}⚠️ Unsupported codec ({codec}) for Intel HW decoding. Using CPU.{NC}")

    print(f"{GREEN}🍿 Playing local video via {selected_name} (Codec: {codec})...{NC}")

    cmd = ["ffplay", "-autoexit"] + ffplay_vcodec + [input_file]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()