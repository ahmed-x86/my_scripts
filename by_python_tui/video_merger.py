#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, get_video_stats, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    file1 = prompt_input(stdscr, "📂 Enter FIRST Video File Path")
    if not file1 or not os.path.isfile(file1): return
    
    file2 = prompt_input(stdscr, "📂 Enter SECOND Video File Path")
    if not file2 or not os.path.isfile(file2): return
    
    # جلب المدة الزمنية لكل فيديو وجمعهما معاً لكي يعمل الـ Progress Bar بدقة
    dur1, f1 = get_video_stats(file1)
    dur2, f2 = get_video_stats(file2)
    total_duration = dur1 + dur2
    total_frames = f1 + f2
    
    name, ext = os.path.splitext(os.path.basename(file1))
    output_file = f"{name}_merged{ext}"
    list_file = "temp_concat_list.txt"
    
    with open(list_file, "w") as f:
        f.write(f"file '{os.path.abspath(file1)}'\n")
        f.write(f"file '{os.path.abspath(file2)}'\n")
        
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_file]
    
    run_ffmpeg_ui(stdscr, cmd, total_duration, total_frames, "Merging Videos Losslessly...")
    
    if os.path.exists(list_file):
        os.remove(list_file)

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)