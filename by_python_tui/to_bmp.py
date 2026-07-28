#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, prompt_choice, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🖼️ Enter Image File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    opts = [
        {"label": "1) RGB 24-bit (Standard)", "fmt": "rgb24"},
        {"label": "2) RGB 16-bit (565 - Embedded)", "fmt": "rgb565le"},
        {"label": "3) Grayscale (8-bit Gray)", "fmt": "gray"}
    ]
    idx = prompt_choice(stdscr, opts, "🎯 Select BMP Pixel Format")
    sel = opts[idx]
    
    name, _ = os.path.splitext(input_file)
    output_file = f"{name}.bmp"
    
    duration, frames = get_video_stats(input_file)
    cmd = ["ffmpeg", "-y", "-i", input_file, "-pix_fmt", sel['fmt'], output_file]
    
    run_ffmpeg_ui(stdscr, cmd, duration, frames, f"Converting to BMP ({sel['fmt']})...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)