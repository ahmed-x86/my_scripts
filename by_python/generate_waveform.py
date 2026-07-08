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

    return duration, total_frames

def main():
    check_dependencies()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}🎵 Please enter the audio or video file path enclosed in quotes \" \":{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    filename = os.path.basename(input_file)
    name = os.path.splitext(filename)[0]
    output_file = f"{name}_waveform.mp4"

    print(f"{YELLOW}⏳ Reading media data...{NC}")
    duration, _ = get_video_stats(input_file)
    
    # الموجة يتم إنشاؤها بفيديو بسرعة 25 إطار في الثانية افتراضياً في ffmpeg
    total_frames = int(duration * 25) if duration > 0 else 0

    print(f"{YELLOW}⏳ Generating Audio Waveform Video...{NC}\n")
    send_notification("Waveform Generator", f"Starting waveform generation for {input_file}...", "multimedia-volume-control")
    
    cmd = [
        "ffmpeg", "-y", 
        "-i", input_file, 
        "-filter_complex", "[0:a]showwaves=s=1920x1080:mode=cline:colors=cyan[v]", 
        "-map", "[v]", "-map", "0:a", 
        "-c:v", "libx264", "-preset", "fast", "-crf", "22", 
        "-c:a", "aac", "-b:a", "192k", 
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
                f"{YELLOW}📊 Progress         : {percent_done}% {CLEAR_LINE}{NC}",
                f"{BLUE}🎞️  Target Frames    : {total_frames if total_frames > 0 else 'N/A'} frames {CLEAR_LINE}{NC}",
                f"{GREEN}⚙️  Generated Frames : {current_frame} frames {CLEAR_LINE}{NC}",
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
        print(f"{GREEN}✅ Waveform video completed: {output_file}{NC}")
        send_notification("Success", f"Waveform finished: {output_file}", "dialog-information")
    else:
        print(f"{RED}❌ Generation failed{NC}")
        send_notification("Error", "Waveform generation failed!", "dialog-error")

if __name__ == "__main__":
    main()
