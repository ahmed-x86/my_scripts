#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, prompt_choice, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🖼️ Enter Image File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    opts = [
        {"label": "1) Standard (Balanced size)", "q": "5"},
        {"label": "2) High Quality (Low compression)", "q": "2"},
        {"label": "3) Maximum (Best quality, larger file)", "q": "1"}
    ]
    
    idx = prompt_choice(stdscr, opts, "🎯 Select JPG Quality")
    sel = opts[idx]
    
    name, _ = os.path.splitext(input_file)
    output_file = f"{name}.jpg"
    
    duration, frames = get_video_stats(input_file)
    cmd = ["ffmpeg", "-y", "-i", input_file, "-q:v", sel['q'], output_file]
    
    run_ffmpeg_ui(stdscr, cmd, duration, frames, "Converting to JPG...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)