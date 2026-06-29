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

def send_notification(title, message, icon):
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", title, message, "-i", icon], check=False)
        except Exception:
            pass

def check_dependencies():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print(f"{RED}❌ ffmpeg or ffprobe is not installed{NC}")
        sys.exit(1)

def get_video_codec(input_file):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name", "-of",
        "default=noprint_wrappers=1:nokey=1", input_file
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')[0]
    except subprocess.CalledProcessError:
        return ""

def main():
    check_dependencies()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}🎬 Please enter the video file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name, extension = os.path.splitext(filename)
    extension = extension.lstrip('.')

    v_codec = get_video_codec(input_file)

    codec_map = {
        "hevc": "libx265",
        "vp9": "libvpx-vp9",
        "vp8": "libvpx",
        "av1": "libsvtav1",
        "mpeg4": "mpeg4"
    }
    
    encoder = codec_map.get(v_codec, "libx264")

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

    output_file = f"{name}_{pct}percent_cuda.{extension}"

    print(f"{YELLOW}⏳ Resizing video to {pct}%...{NC}")
    print(f"{YELLOW}⚙️ Hardware Decode: CUDA | Software Encode: {encoder} | Audio: Copied{NC}")

    send_notification("Video Resizer", f"Starting hybrid conversion (CUDA decode + CPU encode) to {pct}% for {input_file}...", "video-x-generic")

    cmd = [
        "ffmpeg", "-hwaccel", "cuda", "-hide_banner", "-loglevel", "error", "-stats",
        "-i", input_file,
        "-vf", f"scale=trunc(iw*{scale}/2)*2:trunc(ih*{scale}/2)*2",
        "-c:v", encoder,
        "-c:a", "copy",
        output_file
    ]

    process = subprocess.run(cmd)

    if process.returncode == 0:
        print(f"{GREEN}✅ Video resized successfully: {output_file}{NC}")
        send_notification("Success", f"Video resized to {pct}% successfully: {output_file}", "dialog-information")
    else:
        print(f"{RED}❌ Resizing failed{NC}")
        send_notification("Error", "Conversion failed!", "dialog-error")

if __name__ == "__main__":
    main()