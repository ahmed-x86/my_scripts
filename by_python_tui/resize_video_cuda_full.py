#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, prompt_choice, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🎬 Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    scale_opts = [
        {"label": "1) 90%", "scale": "0.90", "pct": "90"}, {"label": "2) 80%", "scale": "0.80", "pct": "80"},
        {"label": "3) 75%", "scale": "0.75", "pct": "75"}, {"label": "4) 70%", "scale": "0.70", "pct": "70"},
        {"label": "5) 60%", "scale": "0.60", "pct": "60"}, {"label": "6) 50%", "scale": "0.50", "pct": "50"},
        {"label": "7) 40%", "scale": "0.40", "pct": "40"}, {"label": "8) 30%", "scale": "0.30", "pct": "30"},
        {"label": "9) 25%", "scale": "0.25", "pct": "25"}, {"label": "10) 20%", "scale": "0.20", "pct": "20"},
        {"label": "11) 10%", "scale": "0.10", "pct": "10"}, {"label": "12) 5%", "scale": "0.05", "pct": "5"}
    ]
    
    idx = prompt_choice(stdscr, scale_opts, "📏 Select Scaling Percentage (Full CUDA)")
    sel = scale_opts[idx]
    
    duration, frames = get_video_stats(input_file)
    name, ext = os.path.splitext(input_file)
    output_file = f"{name}_{sel['pct']}pct_cuda_full{ext}"
    
    cmd = ["ffmpeg", "-y", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda", "-i", input_file, "-vf", f"scale_cuda=iw*{sel['scale']}:ih*{sel['scale']}", "-c:v", "h264_nvenc", "-preset", "p4", "-c:a", "copy", output_file]
    run_ffmpeg_ui(stdscr, cmd, duration, frames, f"Resizing Full CUDA (Decode -> Scale -> Encode) to {sel['pct']}%...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)