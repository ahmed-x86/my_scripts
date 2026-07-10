#!/usr/bin/env python3
import os, curses, subprocess
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def check_av1_nvenc():
    try:
        out = subprocess.check_output(["ffmpeg", "-encoders"], stderr=subprocess.STDOUT, text=True)
        return "av1_nvenc" in out
    except:
        return False

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🎬 Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    duration, frames = get_video_stats(input_file)
    name, _ = os.path.splitext(input_file)
    output_file = f"{name}.webm"
    
    if check_av1_nvenc():
        msg = "Using NVIDIA AV1 Hardware Encoding (Fastest/Best)..."
        cmd = ["ffmpeg", "-y", "-hwaccel", "cuda", "-i", input_file, "-c:v", "av1_nvenc", "-preset", "slow", "-c:a", "libopus", output_file]
    else:
        msg = "NVENC AV1 unsupported. Fallback: CUDA Decode + CPU VP9..."
        cmd = ["ffmpeg", "-y", "-hwaccel", "cuda", "-i", input_file, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "30", "-c:a", "libopus", output_file]
    
    run_ffmpeg_ui(stdscr, cmd, duration, frames, msg)

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)