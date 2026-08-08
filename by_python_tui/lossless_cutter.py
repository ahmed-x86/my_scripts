#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def time_to_seconds(t_str):
    try:
        parts = t_str.strip().split(':')
        if len(parts) == 3: return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2: return int(parts[0]) * 60 + float(parts[1])
        else: return float(parts[0])
    except: return None

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "✂️ Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    start_time = prompt_input(stdscr, "⏱️ Enter Start Time (HH:MM:SS)")
    end_time = prompt_input(stdscr, "⏱️ Enter End Time (HH:MM:SS)")
    if not start_time or not end_time: return
    
    s_sec = time_to_seconds(start_time)
    e_sec = time_to_seconds(end_time)
    cut_duration = (e_sec - s_sec) if (s_sec is not None and e_sec is not None and e_sec > s_sec) else 0
    
    name, ext = os.path.splitext(input_file)
    output_file = f"{name}_cut{ext}"
    
    cmd = ["ffmpeg", "-y", "-i", input_file, "-ss", start_time, "-to", end_time, "-c", "copy", output_file]
    
    # Passing cut_duration so progress bar aligns with the cut piece length
    run_ffmpeg_ui(stdscr, cmd, cut_duration, 0, f"Cutting losslessly [{start_time} - {end_time}]")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)