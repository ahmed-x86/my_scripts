#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "📂 Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    duration, frames = get_video_stats(input_file)
    name = os.path.splitext(input_file)[0]
    output_file = f"{name}_clean_audio.mp4"
    
    cmd = ["ffmpeg", "-y", "-i", input_file, "-c:v", "copy", "-af", "afftdn=nf=-25,loudnorm=I=-16:LRA=7:TP=-1.5", "-c:a", "aac", "-b:a", "192k", output_file]
    run_ffmpeg_ui(stdscr, cmd, duration, frames, "Cleaning Audio (Noise Reduction)...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)