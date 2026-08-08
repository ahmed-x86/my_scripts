#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🎬 Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    duration, frames = get_video_stats(input_file)
    name = os.path.splitext(input_file)[0]
    output_file = f"{name}_av1.mkv"
    
    cmd = ["ffmpeg", "-y", "-i", input_file, "-c:v", "libsvtav1", "-preset", "6", "-crf", "30", "-c:a", "libopus", output_file]
    run_ffmpeg_ui(stdscr, cmd, duration, frames, "Converting to Next-Gen AV1 Codec...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)