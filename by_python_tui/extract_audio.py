#!/usr/bin/env python3
import os, curses, subprocess
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def get_audio_codec(input_file):
    try:
        out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", input_file], stderr=subprocess.STDOUT, text=True).strip()
        return out if out else None
    except: return None

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🎵 Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    codec = get_audio_codec(input_file)
    if not codec: return
    
    ext = {"mp3": "mp3", "aac": "m4a", "opus": "opus", "vorbis": "ogg", "flac": "flac"}.get(codec, "mka")
    duration, frames = get_video_stats(input_file)
    name = os.path.splitext(input_file)[0]
    output_file = f"{name}_extracted.{ext}"
    
    cmd = ["ffmpeg", "-y", "-i", input_file, "-vn", "-c:a", "copy", output_file]
    run_ffmpeg_ui(stdscr, cmd, duration, frames, f"Extracting [{codec}] Audio Stream...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)