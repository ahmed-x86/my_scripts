#!/usr/bin/env python3
import os, curses
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, run_ffmpeg_ui

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "📝 Enter Subtitle File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    name, _ = os.path.splitext(input_file)
    output_file = f"{name}.srt"
    
    cmd = ["ffmpeg", "-y", "-i", input_file, output_file]
    
    # الترجمات تنتهي فوراً لأنها نصوص، الواجهة ستعرض 100% مباشرة بنجاح
    run_ffmpeg_ui(stdscr, cmd, 0, 0, "Converting Subtitle to SRT Format...")

if __name__ == "__main__":
    check_dependencies()
    curses.wrapper(main_tui)