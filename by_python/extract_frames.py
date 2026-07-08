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

def check_ffmpeg():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print(f"{RED}❌ ffmpeg or ffprobe is not installed{NC}")
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
    check_ffmpeg()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}🖼️ Please enter the video file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]

    print(f"{BLUE}Select extraction mode:{NC}")
    print("1) Single frame at specific time (e.g., 00:01:23)")
    print("2) Multiple frames (e.g., 1 frame per second)")
    
    mode = input("> ").strip()

    duration, original_frames = get_video_stats(input_file)
    expected_frames = 1

    if mode == "1":
        print(f"{YELLOW}Enter timestamp (HH:MM:SS):{NC}")
        timestamp = input("> ").strip()
        
        safe_timestamp = timestamp.replace(":", "_")
        output_file = f"{name}_frame_{safe_timestamp}.jpg"
        
        print(f"{YELLOW}⏳ Extracting frame...\n{NC}")
        cmd = ["ffmpeg", "-y", "-ss", timestamp, "-i", input_file, "-vframes", "1", "-q:v", "2", output_file]
        
    elif mode == "2":
        print(f"{YELLOW}Enter fps (e.g., 1 for 1 frame/sec, 0.1 for 1 frame/10sec):{NC}")
        fps = input("> ").strip()
        
        out_dir = f"{name}_frames"
        os.makedirs(out_dir, exist_ok=True)
        output_file = os.path.join(out_dir, "frame_%04d.jpg")
        
        if duration > 0:
            expected_frames = int(duration * float(fps))

        print(f"{YELLOW}⏳ Extracting frames into /{out_dir} ...\n{NC}")
        cmd = ["ffmpeg", "-y", "-i", input_file, "-vf", f"fps={fps}", "-q:v", "2", output_file]
        
    else:
        print(f"{RED}❌ Invalid option{NC}")
        sys.exit(1)

    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    
    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    frame_pattern = re.compile(r"frame=\s*(\d+)")
    fps_pattern = re.compile(r"fps=\s*([\d\.]+)")
    speed_pattern = re.compile(r"speed=\s*([\d\.]+)x")
    
    lines_printed = 0

    for line in process.stderr:
        time_match = time_pattern.search(line)
        
        if time_match:
            hours, minutes, seconds = map(float, time_match.groups())
            current_time = (hours * 3600) + (minutes * 60) + seconds
            
            frame_match = frame_pattern.search(line)
            current_frame = int(frame_match.group(1)) if frame_match else 0
            
            percent_done = min(100, int((current_time / duration) * 100)) if duration > 0 and mode == "2" else 100
            
            fps_match = fps_pattern.search(line)
            current_fps = float(fps_match.group(1)) if fps_match else 0.0
            
            speed_match = speed_pattern.search(line)
            current_speed = float(speed_match.group(1)) if speed_match else 0.0
            
            eta_str = "Calculating..."
            if current_speed > 0 and duration > 0 and mode == "2":
                eta_seconds = max(0, (duration - current_time) / current_speed)
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))

            if lines_printed > 0:
                sys.stdout.write(CURSOR_UP * lines_printed)
            
            output = [
                f"{YELLOW}📊 Progress         : {percent_done}% {CLEAR_LINE}{NC}",
                f"{BLUE}🎞️  Target Frames    : {expected_frames if mode == '2' else 1} frames {CLEAR_LINE}{NC}",
                f"{GREEN}⚙️  Extracted        : {current_frame} frames {CLEAR_LINE}{NC}",
                f"{RED}⏳ Time Remaining   : {eta_str if mode == '2' else 'N/A'} {CLEAR_LINE}{NC}",
                f"{YELLOW}🚀 Processing Speed : {current_fps} fps {CLEAR_LINE}{NC}",
                f"{BLUE}⚡ Speed Ratio      : speed={current_speed}x {CLEAR_LINE}{NC}"
            ]
            
            sys.stdout.write('\n'.join(output) + '\n')
            sys.stdout.flush()
            lines_printed = len(output)

    process.wait()
    print()

    if process.returncode == 0:
        print(f"{GREEN}✅ Extraction completed successfully{NC}")
    else:
        print(f"{RED}❌ Extraction failed{NC}")

if __name__ == "__main__":
    main()