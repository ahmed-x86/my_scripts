#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🎵 Enter Audio/Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    duration, _ = get_video_stats(input_file)
    total_frames = int(duration * 25) if duration > 0 else 0
    name = os.path.splitext(input_file)[0]
    output_file = f"{name}_waveform.mp4"
    
    cmd = [
        "ffmpeg", "-y", "-i", input_file, 
        "-filter_complex", "[0:a]showwaves=s=1920x1080:mode=cline:colors=cyan[v]", 
        "-map", "[v]", "-map", "0:a", 
        "-c:v", "libx264", "-preset", "fast", "-crf", "22", 
        "-c:a", "aac", "-b:a", "192k", output_file
    ]
    
    run_ffmpeg_ui(stdscr, cmd, duration, total_frames, "Generating Audio Waveform Video...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)