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

def check_requirements():
    for cmd in ["ffmpeg", "ffprobe"]:
        if not shutil.which(cmd):
            print(f"{RED}❌ {cmd} is not installed{NC}")
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

def run_ffmpeg_pass(cmd, duration, total_frames, pass_num):
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
            
            percent_done = min(100, int((current_time / duration) * 100)) if duration > 0 else 0
            
            fps_match = fps_pattern.search(line)
            current_fps = float(fps_match.group(1)) if fps_match else 0.0
            
            speed_match = speed_pattern.search(line)
            current_speed = float(speed_match.group(1)) if speed_match else 0.0
            
            eta_str = "Calculating..."
            if current_speed > 0 and duration > 0:
                eta_seconds = max(0, (duration - current_time) / current_speed)
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
            elif current_fps > 0 and total_frames > 0:
                eta_seconds = max(0, (total_frames - current_frame) / current_fps)
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))

            if lines_printed > 0:
                sys.stdout.write(CURSOR_UP * lines_printed)
            
            output = [
                f"{YELLOW}📊 Pass {pass_num} Progress : {percent_done}% {CLEAR_LINE}{NC}",
                f"{BLUE}🎞️  Total Frames     : {total_frames if total_frames > 0 else 'N/A'} frames {CLEAR_LINE}{NC}",
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
    return process.returncode

def main():
    check_requirements()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}🎞️ Please enter the video path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip().strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    print(f"{BLUE}🎯 Enter target file size in MB (e.g., 8, 25):{NC}")
    try:
        target_size_mb = float(input("> ").strip())
    except ValueError:
        print(f"{RED}❌ Invalid size{NC}")
        sys.exit(1)

    print(f"{YELLOW}⏳ Reading video data...{NC}")
    duration, total_frames = get_video_stats(input_file)
    
    if not duration or duration <= 0:
        print(f"{RED}❌ Could not determine video duration{NC}")
        sys.exit(1)

    audio_bitrate = 128
    video_bitrate = int(((target_size_mb * 8192) / duration) - audio_bitrate)
    if video_bitrate < 10:
        video_bitrate = 10

    filename = os.path.basename(input_file)
    name, _ = os.path.splitext(filename)
    output_file = f"{name}_{int(target_size_mb)}MB.mp4"

    print(f"{YELLOW}⏳ Compressing to ~{target_size_mb}MB (Video: {video_bitrate}kbps, Audio: {audio_bitrate}kbps)...{NC}\n")

    pass1_cmd = [
        "ffmpeg", "-y", "-i", input_file, "-c:v", "libx264",
        "-b:v", f"{video_bitrate}k", "-pass", "1", "-an", "-f", "mp4", os.devnull
    ]
    
    if run_ffmpeg_pass(pass1_cmd, duration, total_frames, 1) != 0:
        print(f"{RED}❌ Pass 1 failed{NC}")
        sys.exit(1)

    pass2_cmd = [
        "ffmpeg", "-y", "-i", input_file, "-c:v", "libx264",
        "-b:v", f"{video_bitrate}k", "-pass", "2", "-c:a", "aac",
        "-b:a", f"{audio_bitrate}k", output_file
    ]

    if run_ffmpeg_pass(pass2_cmd, duration, total_frames, 2) == 0:
        print(f"{GREEN}✅ Compression completed: {output_file}{NC}")
    else:
        print(f"{RED}❌ Compression failed{NC}")

    for f in ["ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()