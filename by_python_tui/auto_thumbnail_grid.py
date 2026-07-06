#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🎞️ Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    cols = prompt_input(stdscr, "🎯 Number of columns", "4")
    rows = prompt_input(stdscr, "🎯 Number of rows", "4")
    width = prompt_input(stdscr, "🎯 Thumbnail width (px)", "320")
    
    c = int(cols) if cols.isdigit() else 4
    r = int(rows) if rows.isdigit() else 4
    w = int(width) if width.isdigit() else 320
    
    duration, frames = get_video_stats(input_file)
    if duration <= 0: return
    
    interval = duration / (c * r)
    name = os.path.splitext(input_file)[0]
    output_file = f"{name}_grid_{c}x{r}.jpg"
    
    cmd = ["ffmpeg", "-y", "-i", input_file, "-vf", f"fps=1/{interval:.3f},scale={w}:-1,tile={c}x{r}", "-vframes", "1", output_file]
    run_ffmpeg_ui(stdscr, cmd, duration, frames, "Generating Thumbnail Grid...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)