#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🔍 Enter Video Path to Check")
    if not input_file or not os.path.isfile(input_file): return
    
    log_file = "corruption_report.txt"
    duration, frames = get_video_stats(input_file)
    
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", input_file, "-f", "null", "-"]
    ret = run_ffmpeg_ui(stdscr, cmd, duration, frames, "Scanning for Corruption...", log_file=log_file)
    
    if os.path.exists(log_file) and os.path.getsize(log_file) == 0:
        os.remove(log_file) # لا يوجد تلف، نقوم بحذف السجل الفارغ

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)