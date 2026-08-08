#!/usr/bin/env python3
import os, curses, subprocess
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def get_codecs(input_file):
    v_codec, a_codec = "", ""
    try:
        v_codec = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", input_file], text=True).strip().split('\n')[0]
        a_codec = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", input_file], text=True).strip().split('\n')[0]
    except: pass
    return v_codec, a_codec

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🛠️ Enter Corrupted Video Path")
    if not input_file or not os.path.isfile(input_file): return
    
    duration, total_frames = get_video_stats(input_file)
    v_codec, a_codec = get_codecs(input_file)
    
    v_encoder = {"h264": "libx264", "hevc": "libx265", "vp9": "libvpx-vp9", "vp8": "libvpx", "av1": "libsvtav1", "mpeg4": "mpeg4"}.get(v_codec, "libx264")
    a_encoder = {"aac": "aac", "mp3": "libmp3lame", "opus": "libopus", "vorbis": "libvorbis", "flac": "flac"}.get(a_codec, "aac") if a_codec else None
    
    name, ext = os.path.splitext(input_file)
    output_file = f"{name}_fixed{ext or '.mp4'}"
    
    cmd = ["ffmpeg", "-y", "-err_detect", "ignore_err", "-i", input_file, "-c:v", v_encoder]
    if v_encoder in ["libx264", "libx265"]: cmd.extend(["-preset", "fast", "-crf", "23"])
    if a_encoder: cmd.extend(["-c:a", a_encoder, "-b:a", "192k"])
    else: cmd.extend(["-an"])
    cmd.append(output_file)
    
    run_ffmpeg_ui(stdscr, cmd, duration, total_frames, "Repairing Video Structure...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)