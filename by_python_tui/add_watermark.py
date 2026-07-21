#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, prompt_choice, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    video_file = prompt_input(stdscr, "🎬 Enter Video File Path")
    if not video_file or not os.path.isfile(video_file): return
    
    logo_file = prompt_input(stdscr, "🖼️ Enter Logo File Path (PNG)")
    if not logo_file or not os.path.isfile(logo_file): return
    
    pos_opts = [
        {"label": "📍 Top-Left", "val": "10:10"}, 
        {"label": "📍 Top-Right", "val": "W-w-10:10"}, 
        {"label": "📍 Bottom-Left", "val": "10:H-h-10"}, 
        {"label": "📍 Bottom-Right", "val": "W-w-10:H-h-10"}, 
        {"label": "📍 Center", "val": "(W-w)/2:(H-h)/2"}
    ]
    idx = prompt_choice(stdscr, pos_opts, "Select Watermark Position")
    overlay_pos = pos_opts[idx]['val']
    
    op = prompt_input(stdscr, "👻 Enter Opacity (0.1 to 1.0)", "1.0")
    try: op_val = float(op)
    except: op_val = 1.0
    
    duration, frames = get_video_stats(video_file)
    name, ext = os.path.splitext(video_file)
    output_file = f"{name}_watermarked{ext}"
    
    filter_str = f"[1:v]format=rgba,colorchannelmixer=aa={op_val}[logo];[0:v][logo]overlay={overlay_pos}"
    cmd = ["ffmpeg", "-y", "-i", video_file, "-i", logo_file, "-filter_complex", filter_str, "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", output_file]
    
    run_ffmpeg_ui(stdscr, cmd, duration, frames, "Adding Watermark...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)