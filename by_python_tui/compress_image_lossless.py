#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🖼️ Enter Image File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    duration, frames = get_video_stats(input_file)
    name = os.path.splitext(input_file)[0]
    output_file = f"{name}_compressed.png"
    
    cmd = ["ffmpeg", "-y", "-i", input_file, "-c:v", "png", "-compression_level", "100", output_file]
    run_ffmpeg_ui(stdscr, cmd, duration, frames, "Losslessly Compressing PNG...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)