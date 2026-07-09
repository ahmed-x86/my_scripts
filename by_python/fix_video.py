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
    """Send desktop notification using notify-send if available."""
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

def get_codecs(input_file):
    v_codec, a_codec = "", ""
    try:
        cmd_v = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name", "-of",
            "default=noprint_wrappers=1:nokey=1", input_file
        ]
        v_codec = subprocess.check_output(cmd_v, stderr=subprocess.STDOUT, text=True).strip().split('\n')[0]
    except:
        pass
    
    try:
        cmd_a = [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=codec_name", "-of",
            "default=noprint_wrappers=1:nokey=1", input_file
        ]
        a_codec = subprocess.check_output(cmd_a, stderr=subprocess.STDOUT, text=True).strip().split('\n')[0]
    except:
        pass
        
    return v_codec, a_codec

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
        print(f"{BLUE}🛠️ Please enter the corrupted video path to fix:{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    print(f"{YELLOW}⏳ Reading video data and codecs...{NC}")
    duration, total_frames = get_video_stats(input_file)
    v_codec, a_codec = get_codecs(input_file)

    v_codec_map = {
        "h264": "libx264",
        "hevc": "libx265",
        "vp9": "libvpx-vp9",
        "vp8": "libvpx",
        "av1": "libsvtav1",
        "mpeg4": "mpeg4"
    }
    
    a_codec_map = {
        "aac": "aac",
        "mp3": "libmp3lame",
        "opus": "libopus",
        "vorbis": "libvorbis",
        "flac": "flac"
    }

    v_encoder = v_codec_map.get(v_codec, "libx264")
    a_encoder = a_codec_map.get(a_codec, "aac") if a_codec else None

    filename = os.path.basename(input_file)
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = ".mp4"
        
    output_file = f"{name}_fixed{ext}"

    print(f"{YELLOW}⏳ Repairing video structure using CPU...{NC}")
    print(f"{BLUE}⚙️ Original Codecs -> Video: [{v_codec or 'Unknown'}] | Audio: [{a_codec or 'None'}]{NC}")
    print(f"{BLUE}⚙️ Using Encoders  -> Video: [{v_encoder}] | Audio: [{a_encoder or 'None'}]{NC}")
    print(f"{BLUE}ℹ️ This process ignores corrupted frames and rebuilds the file completely.{NC}\n")
    
    send_notification("Video Repair", f"Starting repair process for {input_file}...", "tools-check-spelling")

    cmd = [
        "ffmpeg", "-y", 
        "-err_detect", "ignore_err", 
        "-i", input_file, 
        "-c:v", v_encoder
    ]
    
    # إضافة إعدادات مخصصة لمعالجات معينة لضمان الجودة
    if v_encoder in ["libx264", "libx265"]:
        cmd.extend(["-preset", "fast", "-crf", "23"])
        
    if a_encoder:
        cmd.extend(["-c:a", a_encoder, "-b:a", "192k"])
    else:
        cmd.extend(["-an"])
        
    cmd.append(output_file)
    
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
                f"{GREEN}⚙️  Fixed Frames     : {current_frame} frames {CLEAR_LINE}{NC}",
                f"{RED}⏳ Time Remaining   : {eta_str} {CLEAR_LINE}{NC}",
                f"{YELLOW}🚀 Processing Speed : {current_fps} fps {CLEAR_LINE}{NC}",
                f"{BLUE}⚡ Speed Ratio      : speed={current_speed}x {CLEAR_LINE}{NC}"
            ]
            
            sys.stdout.write('\n'.join(output) + '\n')
            sys.stdout.flush()
            lines_printed = len(output)

    process.wait()
    print() 

    if process.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        print(f"{GREEN}✅ Video repaired successfully: {output_file}{NC}")
        send_notification("Success", f"Video repaired: {output_file}", "dialog-information")
    else:
        print(f"{RED}❌ Video repair failed or file is completely unreadable.{NC}")
        send_notification("Error", "Video repair failed!", "dialog-error")

if __name__ == "__main__":
    main()