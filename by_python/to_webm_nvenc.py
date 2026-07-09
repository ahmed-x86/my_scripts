#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import re
import time

# Colors
RED = '\033[38;2;243;139;168m'
GREEN = '\033[38;2;166;227;161m'
BLUE = '\033[38;2;137;180;250m'
YELLOW = '\033[38;2;249;226;175m'
NC = '\033[0m'
CLEAR_LINE = '\033[K'
CURSOR_UP = '\033[F'

def send_notification(title, message, icon):
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", title, message, "-i", icon], check=False)
        except Exception:
            pass

def check_dependencies():
    for tool in ["ffmpeg", "ffprobe"]:
        if not shutil.which(tool):
            print(f"{RED}❌ {tool} is not installed{NC}")
            sys.exit(1)

def get_video_stats(input_file):
    duration = 0.0
    total_frames = 0
    
    cmd_duration = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", input_file
    ]
    try:
        out = subprocess.check_output(cmd_duration, stderr=subprocess.STDOUT, text=True).strip()
        duration = float(out)
    except:
        pass

    cmd_fps = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate,nb_frames",
        "-of", "default=noprint_wrappers=1:nokey=1", input_file
    ]
    try:
        out_fps = subprocess.check_output(cmd_fps, stderr=subprocess.STDOUT, text=True).strip().split('\n')
        if len(out_fps) > 1 and out_fps[1].isdigit():
            total_frames = int(out_fps[1])
        else:
            num, den = out_fps[0].split('/')
            fps = float(num) / float(den)
            total_frames = int(duration * fps)
    except:
        pass

    return duration, total_frames

def check_av1_nvenc():
    try:
        out = subprocess.check_output(["ffmpeg", "-encoders"], stderr=subprocess.STDOUT, text=True)
        return "av1_nvenc" in out
    except:
        return False

def main():
    check_dependencies()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}🎬 Please enter the file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]
    output_file = f"{name}.webm"

    print(f"{YELLOW}⏳ Reading video data...{NC}")
    duration, total_frames = get_video_stats(input_file)

    if check_av1_nvenc():
        print(f"{YELLOW}⏳ Using NVIDIA AV1 Hardware Encoding (Fastest/Best)...{NC}\n")
        cmd = [
            "ffmpeg", "-y", "-hwaccel", "cuda", "-i", input_file,
            "-c:v", "av1_nvenc", "-preset", "slow", "-c:a", "libopus", output_file
        ]
    else:
        print(f"{YELLOW}⚠️ NVENC AV1 encode not supported by hardware.{NC}")
        print(f"{BLUE}⏳ Using Hybrid CUDA Decoding + CPU VP9 Encoding...{NC}\n")
        cmd = [
            "ffmpeg", "-y", "-hwaccel", "cuda", "-i", input_file,
            "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30", "-c:a", "libopus", output_file
        ]

    send_notification("Video Converter", f"Starting WebM encoding for {input_file}...", "video-x-generic")

    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    frame_pattern = re.compile(r"frame=\s*(\d+)")
    fps_pattern = re.compile(r"fps=\s*([\d\.]+)")
    speed_pattern = re.compile(r"speed=\s*([\d\.]+)x")
    
    lines_printed = 0

    for line in process.stderr:
        time_match = time_pattern.search(line)
        frame_match = frame_pattern.search(line)
        
        if time_match and frame_match:
            hours, minutes, seconds = map(float, time_match.groups())
            current_time = (hours * 3600) + (minutes * 60) + seconds
            current_frame = int(frame_match.group(1))
            
            percent = min(100, int((current_time / duration) * 100)) if duration > 0 else 0
            
            fps_match = fps_pattern.search(line)
            current_fps = float(fps_match.group(1)) if fps_match else 0.0
            
            speed_match = speed_pattern.search(line)
            current_speed = float(speed_match.group(1)) if speed_match else 0.0
            
            eta_str = "Calculating..."
            if current_fps > 0 and total_frames > 0:
                eta_seconds = max(0, (total_frames - current_frame) / current_fps)
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))

            if lines_printed > 0:
                sys.stdout.write(CURSOR_UP * lines_printed)
            
            output = [
                f"{YELLOW}📊 Progress         : {percent}% {CLEAR_LINE}{NC}",
                f"{BLUE}🎞️  Total Frames     : {total_frames} frames {CLEAR_LINE}{NC}",
                f"{GREEN}⚙️  Processed Frames : {current_frame} frames {CLEAR_LINE}{NC}",
                f"{RED}⏳ Time Remaining   : {eta_str} {CLEAR_LINE}{NC}",
                f"{YELLOW}🚀 Processing Speed : {current_fps} fps {CLEAR_LINE}{NC}",
                f"{BLUE}⚡ Speed Ratio      : speed={current_speed}x {CLEAR_LINE}{NC}"
            ]
            
            sys.stdout.write('\n'.join(output) + '\n')
            sys.stdout.flush()
            lines_printed = len(output)

    process.wait()
    print()

    if process.returncode == 0:
        print(f"{GREEN}✅ Conversion completed successfully: {output_file}{NC}")
        send_notification("Success", f"Conversion finished: {output_file}", "dialog-information")
    else:
        print(f"{RED}❌ Conversion failed. Check your NVIDIA drivers/CUDA.{NC}")
        send_notification("Error", "Conversion failed!", "dialog-error")

if __name__ == "__main__":
    main()