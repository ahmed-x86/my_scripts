#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🎬 Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    duration, frames = get_video_stats(input_file)
    name, _ = os.path.splitext(input_file)
    output_file = f"{name}_mjpeg.mov"
    
    cmd = [
        "ffmpeg", "-y", "-i", input_file, 
        "-vcodec", "mjpeg", "-q:v", "2", 
        "-acodec", "pcm_s16be", "-q:a", "0", "-f", "mov", 
        output_file
    ]
    
    run_ffmpeg_ui(stdscr, cmd, duration, frames, "Converting to MJPEG Format...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)