#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess

# Colors
RED = '\033[38;2;243;139;168m'
GREEN = '\033[38;2;166;227;161m'
BLUE = '\033[38;2;137;180;250m'
YELLOW = '\033[38;2;249;226;175m'
NC = '\033[0m'

def check_dependencies():
    if not shutil.which("yt-dlp"):
        print(f"{RED}❌ yt-dlp is not installed.{NC}")
        print(f"{RED}❌ (Arch: sudo pacman -S yt-dlp){NC}")
        print(f"{RED}❌ (debian: sudo apt install yt-dlp){NC}")
        print(f"{RED}❌ (fedora: sudo dnf install yt-dlp){NC}")
        sys.exit(1)
    
    if not shutil.which("mpv"):
        print(f"{RED}❌ mpv is not installed. (Run: sudo pacman -S mpv){NC}")
        sys.exit(1)

def get_lspci_vga():
    """Retrieve VGA/3D/Display info from lspci."""
    if not shutil.which("lspci"):
        return ""
    try:
        result = subprocess.run(["lspci"], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        vga_lines = [line.lower() for line in lines if "vga" in line.lower() or "3d" in line.lower() or "display" in line.lower()]
        return " ".join(vga_lines)
    except Exception:
        return ""

def get_lsmod():
    """Retrieve loaded modules to check for open-source drivers like nouveau."""
    if not shutil.which("lsmod"):
        return ""
    try:
        result = subprocess.run(["lsmod"], capture_output=True, text=True, check=True)
        return result.stdout.lower()
    except Exception:
        return ""

def main():
    check_dependencies()

    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        print(f"{BLUE}🔗 Please enter the YouTube URL enclosed in quotes \" \":{NC}")
        url = input("> ").strip()
        
    # Clean quotes
    url = url.strip('"\'')

    if not url:
        print(f"{RED}❌ URL cannot be empty{NC}")
        sys.exit(1)

    options = ["CPU (Software Decoding)"]
    hwdec_args = ["no"]

    vga_info = get_lspci_vga()
    
    # Check for Intel
    if "intel" in vga_info:
        options.append("Intel GPU")
        hwdec_args.append("vaapi")
        
    # Check for AMD
    if "amd" in vga_info:
        options.append("AMD GPU")
        hwdec_args.append("vaapi")

    # Check for Nvidia
    if "nvidia" in vga_info:
        if shutil.which("nvidia-smi"):
            try:
                smi_res = subprocess.run(
                    ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
                    capture_output=True, text=True, check=True
                )
                cc_output = smi_res.stdout.strip().split('\n')[0]
                major_cc = int(cc_output.split('.')[0])
                
                if major_cc < 6:
                    options.append("Nvidia GPU (Old Cards)")
                    hwdec_args.append("vdpau")
                else:
                    options.append("Nvidia GPU (Modern Cards)")
                    hwdec_args.append("nvdec")
            except Exception:
                options.append("Nvidia GPU")
                hwdec_args.append("nvdec")
        else:
            options.append("Nvidia GPU")
            hwdec_args.append("nvdec")

    # Check for Nouveau driver
    lsmod_info = get_lsmod()
    if "nouveau" in lsmod_info:
        options.append("Nvidia Open Source Driver (Nouveau)")
        hwdec_args.append("vaapi")

    print(f"{BLUE}🖥️  Select Decoding Device:{NC}")
    for i, opt in enumerate(options):
        print(f"{YELLOW}{i+1}. {opt}{NC}")

    hw_choice = input("> ").strip()

    try:
        choice_idx = int(hw_choice) - 1
        if choice_idx < 0 or choice_idx >= len(options):
            raise ValueError
        
        hw_arg = hwdec_args[choice_idx]
        selected_name = options[choice_idx]
    except ValueError:
        print(f"{RED}❌ Invalid selection. Defaulting to CPU.{NC}")
        hw_arg = "no"
        selected_name = "CPU"

    extra_mpv_args = []
    if selected_name == "Intel GPU":
        extra_mpv_args = ["--vo=gpu", "--gpu-context=wayland"]

    print(f"{BLUE}📊 Do you want to select video quality manually? (y/n):{NC}")
    manual_quality = input("> ").strip().lower()

    if manual_quality == "y":
        print(f"{YELLOW}⏳ Fetching video formats...{NC}")
        # Call yt-dlp interactively to show formats
        subprocess.run(["yt-dlp", "-F", url])
        
        print(f"{BLUE}✍️ Enter the format code (e.g., 299+140, or 'best'):{NC}")
        format_code = input("> ").strip()
        
        if format_code:
            print(f"{GREEN}🍿 Streaming video via {selected_name} (Format: {format_code})...{NC}")
            cmd = ["mpv", f"--hwdec={hw_arg}"] + extra_mpv_args + [f"--ytdl-format={format_code}", url]
        else:
            print(f"{GREEN}🍿 Streaming video via {selected_name} (Best Quality)...{NC}")
            cmd = ["mpv", f"--hwdec={hw_arg}"] + extra_mpv_args + [url]
    else:
        print(f"{GREEN}🍿 Streaming video via {selected_name} (Best Quality)...{NC}")
        cmd = ["mpv", f"--hwdec={hw_arg}"] + extra_mpv_args + [url]

    # Run mpv and wait for it to finish
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        # Graceful exit if user presses Ctrl+C during streaming
        print(f"\n{YELLOW}🛑 Playback stopped by user.{NC}")

if __name__ == "__main__":
    main()