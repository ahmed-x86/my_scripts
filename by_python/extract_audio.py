#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import re

# Colors
RED = '\033[38;2;243;139;168m'
GREEN = '\033[38;2;166;227;161m'
BLUE = '\033[38;2;137;180;250m'
YELLOW = '\033[38;2;249;226;175m'
NC = '\033[0m'

def check_ffmpeg():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print(f"{RED}❌ ffmpeg or ffprobe is not installed{NC}")
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

    # Get the audio codec
    codec = get_audio_codec(input_file)
    
    if not codec:
        print(f"{RED}❌ No audio stream found in the file.{NC}")
        sys.exit(1)

    # Determine the correct extension
    codec_map = {
        "mp3": "mp3",
        "aac": "m4a",
        "opus": "opus",
        "vorbis": "ogg",
        "flac": "flac"
    }
    ext = codec_map.get(codec, "mka")

    output_file = f"{name}_extracted.{ext}"

    print(f"{YELLOW}⏳ Extracting original [{codec}] audio stream...{NC}")

    duration = get_duration(input_file)
    
    # Run ffmpeg to copy the audio stream without re-encoding
    cmd = ["ffmpeg", "-y", "-i", input_file, "-vn", "-c:a", "copy", output_file]
    
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    
    # Progress bar logic
    for line in process.stderr:
        if duration:
            match = time_pattern.search(line)
            if match:
                hours, minutes, seconds = map(float, match.groups())
                current_time = (hours * 3600) + (minutes * 60) + seconds
                percent = min(100, int((current_time / duration) * 100))
                print(f"\r{YELLOW}🔄 Progress: {percent}%{NC}", end="", flush=True)
        else:
            print(f"\r{YELLOW}🔄 Extracting...{NC}", end="", flush=True)

    process.wait()
    print() # Print a newline after progress finishes

    if process.returncode == 0:
        print(f"{GREEN}✅ Successfully extracted to: {output_file}{NC}")
    else:
        print(f"{RED}❌ Extraction failed{NC}")

if __name__ == "__main__":
    main()