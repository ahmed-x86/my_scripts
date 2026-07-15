#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, prompt_choice, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🖼️ Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    opts = [
        {"label": "1) Single frame at specific time (e.g., 00:01:23)"},
        {"label": "2) Multiple frames (e.g., 1 frame per second)"}
    ]
    mode = prompt_choice(stdscr, opts, "Select Extraction Mode")
    
    duration, original_frames = get_video_stats(input_file)
    name = os.path.splitext(input_file)[0]
    
    if mode == 0:
        timestamp = prompt_input(stdscr, "⏱️ Enter timestamp (HH:MM:SS)")
        if not timestamp: return
        safe_timestamp = timestamp.replace(":", "_")
        output_file = f"{name}_frame_{safe_timestamp}.jpg"
        cmd = ["ffmpeg", "-y", "-ss", timestamp, "-i", input_file, "-vframes", "1", "-q:v", "2", output_file]
        run_ffmpeg_ui(stdscr, cmd, 1, 1, "Extracting Single Frame...")
        
    elif mode == 1:
        fps = prompt_input(stdscr, "🎞️ Enter fps (e.g., 1 for 1 frame/sec)", "1")
        if not fps: return
        out_dir = f"{name}_frames"
        os.makedirs(out_dir, exist_ok=True)
        output_file = os.path.join(out_dir, "frame_%04d.jpg")
        expected_frames = int(duration * float(fps)) if duration > 0 else 0
        cmd = ["ffmpeg", "-y", "-i", input_file, "-vf", f"fps={fps}", "-q:v", "2", output_file]
        run_ffmpeg_ui(stdscr, cmd, duration, expected_frames, f"Extracting frames into /{out_dir}...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)