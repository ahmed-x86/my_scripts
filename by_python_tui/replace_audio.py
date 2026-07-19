#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    video_file = prompt_input(stdscr, "🎬 Enter VIDEO File Path")
    if not video_file or not os.path.isfile(video_file): return
    
    audio_file = prompt_input(stdscr, "🎵 Enter NEW AUDIO File Path")
    if not audio_file or not os.path.isfile(audio_file): return
    
    duration, total_frames = get_video_stats(video_file)
    name, ext = os.path.splitext(video_file)
    output_file = f"{name}_new_audio{ext}"
    
    cmd = [
        "ffmpeg", "-y", "-i", video_file, "-i", audio_file,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "copy", "-shortest", output_file
    ]
    
    run_ffmpeg_ui(stdscr, cmd, duration, total_frames, "Replacing Audio Losslessly...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)