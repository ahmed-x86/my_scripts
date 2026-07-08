#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import re
import time

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

def main():
    check_dependencies()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}🔍 Please enter the video path to check:{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    log_file = "corruption_report.txt"
    
    with open(log_file, "w") as f:
        pass

    print(f"{YELLOW}⏳ Reading video data...{NC}")
    duration, total_frames = get_video_stats(input_file)

    print(f"{YELLOW}⏳ Scanning video for integrity issues...{NC}")
    print(f"{BLUE}ℹ️ This process decodes every frame to ensure the file is 100% healthy.{NC}\n")
    send_notification("Video Health Check", f"Starting thorough scan for {input_file}...", "security-high")

    cmd = [
        "ffmpeg", "-y", "-v", "error", "-stats", 
        "-i", input_file, 
        "-f", "null", "-"
    ]
    
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    frame_pattern = re.compile(r"frame=\s*(\d+)")
    fps_pattern = re.compile(r"fps=\s*([\d\.]+)")
    speed_pattern = re.compile(r"speed=\s*([\d\.]+)x")
    
    lines_printed = 0

    with open(log_file, "w") as lf:
        for line in process.stderr:
            time_match = time_pattern.search(line)
            frame_match = frame_pattern.search(line)
            
            if time_match and frame_match:
                hours, minutes, seconds = map(float, time_match.groups())
                current_time = (hours * 3600) + (minutes * 60) + seconds
                current_frame = int(frame_match.group(1))
                
                percent_done = min(100, int((current_time / duration) * 100)) if duration > 0 else 0
                
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
                    f"{YELLOW}📊 Progress         : {percent_done}% {CLEAR_LINE}{NC}",
                    f"{BLUE}🎞️  Total Frames     : {total_frames} frames {CLEAR_LINE}{NC}",
                    f"{GREEN}⚙️  Scanned Frames   : {current_frame} frames {CLEAR_LINE}{NC}",
                    f"{RED}⏳ Time Remaining   : {eta_str} {CLEAR_LINE}{NC}",
                    f"{YELLOW}🚀 Scanning Speed   : {current_fps} fps {CLEAR_LINE}{NC}",
                    f"{BLUE}⚡ Speed Ratio      : speed={current_speed}x {CLEAR_LINE}{NC}"
                ]
                
                sys.stdout.write('\n'.join(output) + '\n')
                sys.stdout.flush()
                lines_printed = len(output)
            else:
                if line.strip():
                    lf.write(line + "\n")

    process.wait()
    print() 

    if os.path.getsize(log_file) == 0:
        print(f"{GREEN}✅ Perfect! No corruption or decoding errors detected.{NC}")
        send_notification("Success", f"Video is 100% Healthy", "dialog-information")
        os.remove(log_file) 
    else:
        print(f"{RED}❌ CORRUPTION DETECTED!{NC}")
        print(f"{YELLOW}--------------------------------------------------{NC}")
        with open(log_file, "r") as lf:
            print(lf.read().strip())
        print(f"{YELLOW}--------------------------------------------------{NC}")
        print(f"{BLUE}📄 Full error details saved in: {log_file}{NC}")
        send_notification("Integrity Warning", f"Corruption found in video", "dialog-warning")

if __name__ == "__main__":
    main()