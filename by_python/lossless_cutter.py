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

def check_ffmpeg():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print(f"{RED}❌ ffmpeg or ffprobe is not installed{NC}")
        sys.exit(1)

def time_to_seconds(t_str):
    try:
        parts = t_str.strip().split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        else:
            return float(parts[0])
    except:
        return None

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

    fps_rate = (total_frames / duration) if duration > 0 else 0
    return fps_rate

def main():
    check_ffmpeg()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}✂️ Enter file path to cut:{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    print(f"{BLUE}⏱️ Enter start time (HH:MM:SS) e.g., 00:01:52:{NC}")
    start_time = input("> ").strip()

    print(f"{BLUE}⏱️ Enter end time (HH:MM:SS) e.g., 00:02:03:{NC}")
    end_time = input("> ").strip()

    filename = os.path.basename(input_file)
    name, ext = os.path.splitext(filename)
    output_file = f"{name}_cut{ext}"

    s_sec = time_to_seconds(start_time)
    e_sec = time_to_seconds(end_time)
    
    cut_duration = None
    if s_sec is not None and e_sec is not None and e_sec > s_sec:
        cut_duration = e_sec - s_sec

    print(f"{YELLOW}⏳ Reading video data...{NC}")
    fps_rate = get_video_stats(input_file)
    
    target_frames = int(cut_duration * fps_rate) if cut_duration and fps_rate > 0 else "N/A"

    print(f"{YELLOW}⏳ Cutting file losslessly from [{start_time}] to [{end_time}]...\n{NC}")

    cmd = [
        "ffmpeg", "-y", 
        "-i", input_file,
        "-ss", start_time,
        "-to", end_time,
        "-c", "copy",
        output_file
    ]
    
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
            
            # Since -ss is AFTER -i, ffmpeg's time output starts from original timestamp
            # We subtract the start offset to calculate accurate progress
            progress_time = max(0, current_time - s_sec) if s_sec else current_time
            
            frame_match = frame_pattern.search(line)
            current_frame = int(frame_match.group(1)) if frame_match else 0
            
            percent_done = min(100, int((progress_time / cut_duration) * 100)) if cut_duration and cut_duration > 0 else 0
            
            fps_match = fps_pattern.search(line)
            current_fps = float(fps_match.group(1)) if fps_match else 0.0
            
            speed_match = speed_pattern.search(line)
            current_speed = float(speed_match.group(1)) if speed_match else 0.0
            
            eta_str = "Calculating..."
            if current_speed > 0 and cut_duration and cut_duration > 0:
                eta_seconds = max(0, (cut_duration - progress_time) / current_speed)
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))

            if lines_printed > 0:
                sys.stdout.write(CURSOR_UP * lines_printed)
            
            output = [
                f"{YELLOW}📊 Progress         : {percent_done}% {CLEAR_LINE}{NC}",
                f"{BLUE}🎞️  Target Frames    : {target_frames} frames {CLEAR_LINE}{NC}",
                f"{GREEN}⚙️  Processed Frames : {current_frame} frames {CLEAR_LINE}{NC}",
                f"{RED}⏳ Time Remaining   : {eta_str} {CLEAR_LINE}{NC}",
                f"{YELLOW}🚀 Processing Speed : {current_fps} fps {CLEAR_LINE}{NC}",
                f"{BLUE}⚡ Speed Ratio      : speed={current_speed}x {CLEAR_LINE}{NC}"
            ]
            
            sys.stdout.write('\n'.join(output) + '\n')
            sys.stdout.flush()
            lines_printed = len(output)

    process.wait()
    
    if cut_duration:
        print() 

    if process.returncode == 0:
        print(f"{GREEN}✅ Successfully cut to: {output_file}{NC}")
    else:
        print(f"{RED}❌ Cutting failed{NC}")

if __name__ == "__main__":
    main()