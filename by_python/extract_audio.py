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

def get_audio_codec(input_file):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name", "-of",
        "default=noprint_wrappers=1:nokey=1", input_file
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
        return out if out else None
    except:
        return None

def main():
    check_ffmpeg()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}🎵 Enter file path to extract audio:{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]

    codec = get_audio_codec(input_file)
    
    if not codec:
        print(f"{RED}❌ No audio stream found in the file.{NC}")
        sys.exit(1)

    codec_map = {
        "mp3": "mp3",
        "aac": "m4a",
        "opus": "opus",
        "vorbis": "ogg",
        "flac": "flac"
    }
    ext = codec_map.get(codec, "mka")

    output_file = f"{name}_extracted.{ext}"

    print(f"{YELLOW}⏳ Reading media data...{NC}")
    duration, total_frames = get_video_stats(input_file)

    print(f"{YELLOW}⏳ Extracting original [{codec}] audio stream...{NC}\n")

    cmd = ["ffmpeg", "-y", "-i", input_file, "-vn", "-c:a", "copy", output_file]
    
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    speed_pattern = re.compile(r"speed=\s*([\d\.]+)x")
    
    lines_printed = 0

    for line in process.stderr:
        time_match = time_pattern.search(line)
        
        if time_match:
            hours, minutes, seconds = map(float, time_match.groups())
            current_time = (hours * 3600) + (minutes * 60) + seconds
            
            percent_done = min(100, int((current_time / duration) * 100)) if duration > 0 else 0
            
            speed_match = speed_pattern.search(line)
            current_speed = float(speed_match.group(1)) if speed_match else 0.0
            
            eta_str = "Calculating..."
            if current_speed > 0 and duration > 0:
                eta_seconds = max(0, (duration - current_time) / current_speed)
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))

            if lines_printed > 0:
                sys.stdout.write(CURSOR_UP * lines_printed)
            
            output = [
                f"{YELLOW}📊 Progress         : {percent_done}% {CLEAR_LINE}{NC}",
                f"{BLUE}🎞️  Total Frames     : N/A (Audio Extract) {CLEAR_LINE}{NC}",
                f"{GREEN}⚙️  Processed Frames : N/A (Audio Extract) {CLEAR_LINE}{NC}",
                f"{RED}⏳ Time Remaining   : {eta_str} {CLEAR_LINE}{NC}",
                f"{YELLOW}🚀 Processing Speed : N/A fps {CLEAR_LINE}{NC}",
                f"{BLUE}⚡ Speed Ratio      : speed={current_speed}x {CLEAR_LINE}{NC}"
            ]
            
            sys.stdout.write('\n'.join(output) + '\n')
            sys.stdout.flush()
            lines_printed = len(output)

    process.wait()
    print()

    if process.returncode == 0:
        print(f"{GREEN}✅ Successfully extracted to: {output_file}{NC}")
    else:
        print(f"{RED}❌ Extraction failed{NC}")

if __name__ == "__main__":
    main()