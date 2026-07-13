#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🎞️ Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    target_mb = prompt_input(stdscr, "🎯 Enter Target Size (MB)", "25")
    try: target_size = float(target_mb)
    except: target_size = 25.0
    
    duration, frames = get_video_stats(input_file)
    if duration <= 0: return
    
    audio_br = 128
    video_br = max(10, int(((target_size * 8192) / duration) - audio_br))
    name = os.path.splitext(input_file)[0]
    output_file = f"{name}_{int(target_size)}MB.mp4"
    
    pass1 = ["ffmpeg", "-y", "-i", input_file, "-c:v", "libx264", "-b:v", f"{video_br}k", "-pass", "1", "-an", "-f", "mp4", os.devnull]
    pass2 = ["ffmpeg", "-y", "-i", input_file, "-c:v", "libx264", "-b:v", f"{video_br}k", "-pass", "2", "-c:a", "aac", "-b:a", f"{audio_br}k", output_file]
    
    if run_ffmpeg_ui(stdscr, pass1, duration, frames, "Pass 1/2: Analyzing Video...") == 0:
        run_ffmpeg_ui(stdscr, pass2, duration, frames, "Pass 2/2: Encoding Video...")
        
    for log_f in ["ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"]:
        if os.path.exists(log_f): os.remove(log_f)

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)