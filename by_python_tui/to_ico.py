#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, prompt_choice, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🖼️ Enter Image File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    opts = [
        {"label": "16x16   (Small Favicon)", "val": "16"},
        {"label": "32x32   (Standard Favicon)", "val": "32"},
        {"label": "48x48   (Desktop Icon)", "val": "48"},
        {"label": "64x64", "val": "64"},
        {"label": "128x128", "val": "128"},
        {"label": "256x256 (High Quality)", "val": "256"},
        {"label": "512x512", "val": "512"},
        {"label": "1024x1024 (Maximum)", "val": "1024"},
        {"label": "Custom Size", "val": "custom"}
    ]
    
    idx = prompt_choice(stdscr, opts, "📏 Select Icon Size")
    sel = opts[idx]
    
    if sel['val'] == "custom":
        c_size = prompt_input(stdscr, "Enter custom size (e.g., 200)", "256")
        size = c_size if c_size.isdigit() else "256"
    else:
        size = sel['val']
        
    name, _ = os.path.splitext(input_file)
    output_file = f"{name}_{size}x{size}.ico"
    
    duration, frames = get_video_stats(input_file)
    cmd = ["ffmpeg", "-y", "-i", input_file, "-vf", f"scale={size}:{size}:flags=lanczos", output_file]
    
    run_ffmpeg_ui(stdscr, cmd, duration, frames, f"Generating Icon [{size}x{size}]...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)