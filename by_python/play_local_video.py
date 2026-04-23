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

def check_mpv():
    if not shutil.which("mpv"):
        print(f"{RED}❌ mpv is not installed.{NC}")
        sys.exit(1)

def get_gpu_info():
    try:
        lspci_out = subprocess.check_output(["lspci"], text=True).lower()
        return lspci_out
    except:
        return ""

def main():
    check_mpv()

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
        hwdec_args.append("vaapi")

    if "amd" in gpu_info or "ati" in gpu_info:
        options.append("AMD GPU")
        hwdec_args.append("vaapi")

    if "nvidia" in gpu_info:
        if shutil.which("nvidia-smi"):
            try:
                cc_out = subprocess.check_output(["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"], text=True)
                major_cc = int(cc_out.split('.')[0])
                if major_cc < 6:
                    options.append("Nvidia GPU (Old Cards)")
                    hwdec_args.append("vdpau")
                else:
                    options.append("Nvidia GPU (Modern Cards)")
                    hwdec_args.append("nvdec")
            except:
                options.append("Nvidia GPU")
                hwdec_args.append("nvdec")
        else:
            options.append("Nvidia GPU")
            hwdec_args.append("nvdec")

    lsmod_out = subprocess.getoutput("lsmod")
    if "nouveau" in lsmod_out.lower():
        options.append("Nvidia Open Source Driver (Nouveau)")
        hwdec_args.append("vaapi")

    print(f"{BLUE}🖥️  Select Decoding Device:{NC}")
    for i, opt in enumerate(options):
        print(f"{YELLOW}{i+1}. {opt}{NC}")

    try:
        choice = int(input("> ").strip())
        if 1 <= choice <= len(options):
            selected_name = options[choice-1]
            hw_arg = hwdec_args[choice-1]
        else:
            raise ValueError
    except:
        print(f"{RED}❌ Invalid selection. Defaulting to CPU.{NC}")
        selected_name = "CPU"
        hw_arg = "no"

    extra_args = []
    if selected_name == "Intel GPU":
        extra_args = ["--vo=gpu", "--gpu-context=wayland"]

    print(f"{GREEN}🍿 Playing local video via {selected_name}...{NC}")
    
    cmd = ["mpv", f"--hwdec={hw_arg}"] + extra_args + [input_file]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()