#!/usr/bin/env python3
import os, curses, subprocess, shutil, sys
from tui_base import setup_catppuccin_colors, prompt_input, draw_logo

def check_magick():
    if not shutil.which("magick"):
        print("❌ ImageMagick is not installed. Please install it.")
        sys.exit(1)

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "🖼️ Enter Image File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    orig_kb = os.path.getsize(input_file) // 1024
    
    target_str = prompt_input(stdscr, f"💾 Original: {orig_kb}KB | Enter Target Max Size (KB)")
    if not target_str.isdigit(): return
    target_kb = int(target_str)
    
    if target_kb >= orig_kb: return
    
    name, _ = os.path.splitext(input_file)
    output_file = f"{name}_{target_kb}KB.jpg"
    
    cmd = ["magick", input_file, "-define", f"jpeg:extent={target_kb}kb", output_file]
    
    # واجهة تحميل مخصصة لـ Magick
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    draw_logo(stdscr, max_y // 4 - 2, max_x)
    stdscr.addstr(max_y // 2, (max_x - 30) // 2, " ⏳ Compressing image... ", curses.color_pair(4) | curses.A_BOLD)
    stdscr.refresh()
    
    p = subprocess.run(cmd)
    
    stdscr.clear()
    draw_logo(stdscr, max_y // 4 - 2, max_x)
    if p.returncode == 0 and os.path.exists(output_file):
        new_kb = os.path.getsize(output_file) // 1024
        msg = f"   Compressed to {new_kb}KB successfully! "
        color = curses.color_pair(2)
    else:
        msg = "   Compression Failed! "
        color = curses.color_pair(7)
        
    stdscr.addstr(max_y // 2 + 2, (max_x - len(msg)) // 2, msg, color | curses.A_BOLD)
    stdscr.addstr(max_y // 2 + 4, (max_x - 22) // 2, " Press any key to exit ", curses.color_pair(5))
    stdscr.getch()

if __name__ == "__main__":
    check_magick()
    curses.wrapper(main_tui)