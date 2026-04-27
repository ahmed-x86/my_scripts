#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import re


RED = '\033[38;2;243;139;168m'
GREEN = '\033[38;2;166;227;161m'
BLUE = '\033[38;2;137;180;250m'
YELLOW = '\033[38;2;249;226;175m'
NC = '\033[0m'

def send_notification(title, message, icon):
    """Send desktop notification using notify-send if available."""
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", title, message, "-i", icon], check=False)
        except Exception:
            pass

def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print(f"{RED}❌ ffmpeg is not installed{NC}")
        sys.exit(1)

def get_duration(input_file):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of",
        "default=noprint_wrappers=1:nokey=1", input_file
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
        return float(out)
    except:
        return None

def main():
    check_ffmpeg()

    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        print(f"{BLUE}🔍 Please enter the video path to check (CPU Mode):{NC}")
        input_file = input("> ").strip()
        
    input_file = input_file.strip('"\'')

    if not os.path.isfile(input_file):
        print(f"{RED}❌ File does not exist: {input_file}{NC}")
        sys.exit(1)

    log_file = "corruption_report.txt"
    
    with open(log_file, "w") as f:
        pass

    print(f"{YELLOW}⏳ Scanning video for integrity issues using CPU...{NC}")
    print(f"{BLUE}ℹ️ This process decodes every frame to ensure the file is 100% healthy.{NC}")
    send_notification("Video Health Check", f"Starting thorough scan for {input_file}...", "security-high")

    duration = get_duration(input_file)
    
    
    cmd = [
        "ffmpeg", "-v", "error", "-stats", 
        "-i", input_file, 
        "-f", "null", "-"
    ]
    
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    
    with open(log_file, "w") as lf:
        
        for line in process.stderr:
           
            if "frame=" in line and "time=" in line:
                if duration:
                    match = time_pattern.search(line)
                    if match:
                        hours, minutes, seconds = map(float, match.groups())
                        current_time = (hours * 3600) + (minutes * 60) + seconds
                        percent = min(100, int((current_time / duration) * 100))
                        print(f"\r{YELLOW}🔄 Progress: {percent}%{NC}", end="", flush=True)
                else:
                    print(f"\r{YELLOW}🔄 Scanning...{NC}", end="", flush=True)
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