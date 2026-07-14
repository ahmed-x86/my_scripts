#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, prompt_choice, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "📱 Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    sm_opts = [
        {"label": "1080x1920 (9:16 - TikTok / Reels)", "w": 1080, "h": 1920},
        {"label": "1080x1350 (4:5 - Instagram Portrait)", "w": 1080, "h": 1350},
        {"label": "1080x1080 (1:1 - Square Post)", "w": 1080, "h": 1080},
        {"label": "1920x1080 (16:9 - YouTube Landscape)", "w": 1920, "h": 1080},
        {"label": "720x1280  (9:16 - 720p Vertical)", "w": 720, "h": 1280},
        {"label": "Custom Size", "w": 0, "h": 0}
    ]
    
    idx = prompt_choice(stdscr, sm_opts, "📏 Select Social Media Resolution")
    sel = sm_opts[idx]
    
    if sel['w'] == 0:
        w_str = prompt_input(stdscr, "Enter width (e.g., 1080)")
        h_str = prompt_input(stdscr, "Enter height (e.g., 1920)")
        try:
            width, height = int(w_str), int(h_str)
        except:
            width, height = 1080, 1920
    else:
        width, height = sel['w'], sel['h']
        
    duration, frames = get_video_stats(input_file)
    name, ext = os.path.splitext(input_file)
    output_file = f"{name}_{width}x{height}{ext}"
    
    vf_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"
    cmd = ["ffmpeg", "-y", "-i", input_file, "-vf", vf_filter, "-c:a", "copy", output_file]
    
    run_ffmpeg_ui(stdscr, cmd, duration, frames, f"Padding/Resizing to [{width}x{height}]...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)