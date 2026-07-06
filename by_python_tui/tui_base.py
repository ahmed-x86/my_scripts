#!/usr/bin/env python3
import curses, os, sys, shutil, subprocess, re, time

LOGO = [
    " ███████╗███████╗███╗   ███╗██████╗ ███████╗ ██████╗",
    " ██╔════╝██╔════╝████╗ ████║██╔══██╗██╔════╝██╔════╝",
    " █████╗  █████╗  ██╔████╔██║██████╔╝█████╗  ██║  ███╗",
    " ██╔══╝  ██╔══╝  ██║╚██╔╝██║██╔═══╝ ██╔══╝  ██║   ██║",
    " ██║     ██║     ██║ ╚═╝ ██║██║     ███████╗╚██████╔╝",
    " ╚═╝     ╚═╝     ╚═╝     ╚═╝╚═╝     ╚══════╝ ╚═════╝ "
]

def check_dependencies():
    for tool in ["ffmpeg", "ffprobe"]:
        if not shutil.which(tool):
            print(f"❌ {tool} is not installed.")
            sys.exit(1)

def setup_catppuccin_colors():
    curses.use_default_colors()
    try:
        if curses.can_change_color():
            def set_hex(col_id, hex_code):
                h = hex_code.lstrip('#')
                r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                curses.init_color(col_id, int(r*1000/255), int(g*1000/255), int(b*1000/255))
            BLUE = 200; set_hex(BLUE, "#89b4fa")
            MAUVE = 201; set_hex(MAUVE, "#cba6f7")
            GREEN = 202; set_hex(GREEN, "#a6e3a1")
            PEACH = 203; set_hex(PEACH, "#fab387")
            RED = 204; set_hex(RED, "#f38ba8")
            OVERLAY0 = 206; set_hex(OVERLAY0, "#6c7086")
            BASE = 207; set_hex(BASE, "#1e1e2e")
            curses.init_pair(1, MAUVE, -1)
            curses.init_pair(2, GREEN, -1)
            curses.init_pair(3, PEACH, -1)
            curses.init_pair(4, BLUE, -1)
            curses.init_pair(5, OVERLAY0, -1)
            curses.init_pair(6, BASE, BLUE)
            curses.init_pair(7, RED, -1)
        else: raise Exception()
    except:
        curses.init_pair(1, curses.COLOR_MAGENTA, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_CYAN, -1)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(7, curses.COLOR_RED, -1)

def draw_logo(stdscr, start_y, max_x):
    for i, line in enumerate(LOGO):
        x = (max_x - len(line)) // 2
        stdscr.addstr(start_y + i, x, line, curses.color_pair(4) | curses.A_BOLD)
    return start_y + len(LOGO) + 2

def prompt_input(stdscr, title, default_text=""):
    curses.curs_set(1)
    input_str = default_text
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        try:
            logo_bottom = draw_logo(stdscr, max_y // 4 - 2, max_x)
            box_w = min(80, max_x - 4)
            start_x = (max_x - box_w) // 2
            input_y = logo_bottom + 3
            
            stdscr.addstr(input_y, start_x, f" {title} ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(input_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            stdscr.addstr(input_y + 2, start_x, "│ ", curses.color_pair(5))
            stdscr.addstr(input_y + 2, start_x + 2, input_str.ljust(box_w-4), curses.color_pair(1))
            stdscr.addstr(input_y + 2, start_x + box_w - 2, " │", curses.color_pair(5))
            stdscr.addstr(input_y + 3, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
            stdscr.move(input_y + 2, start_x + 2 + len(input_str))
        except curses.error: pass
        stdscr.refresh()
        
        c = stdscr.getch()
        if c in (curses.KEY_ENTER, 10, 13): break
        elif c in (curses.KEY_BACKSPACE, 8, 127) and len(input_str) > 0: input_str = input_str[:-1]
        elif 32 <= c <= 126 and len(input_str) < max_x - 10: input_str += chr(c)
    curses.curs_set(0)
    return input_str.strip().strip('"\'')

def prompt_choice(stdscr, options, title):
    current_idx = 0
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        try:
            logo_bottom = draw_logo(stdscr, 2, max_x)
            box_w = min(80, max_x - 4)
            start_x = (max_x - box_w) // 2
            start_y = logo_bottom + 2
            
            stdscr.addstr(start_y, start_x, f" {title} ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(start_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            
            for i, opt in enumerate(options):
                label = f"  {opt['label']} ".ljust(box_w - 4)
                y_pos = start_y + 2 + i
                stdscr.addstr(y_pos, start_x, "│ ", curses.color_pair(5))
                if i == current_idx:
                    stdscr.addstr(y_pos, start_x + 2, label, curses.color_pair(7) | curses.A_BOLD)
                else:
                    stdscr.addstr(y_pos, start_x + 2, label, curses.color_pair(1))
                stdscr.addstr(y_pos, start_x + box_w - 2, " │", curses.color_pair(5))
                
            stdscr.addstr(start_y + 2 + len(options), start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
        except curses.error: pass
        stdscr.refresh()
        
        c = stdscr.getch()
        if c == curses.KEY_UP and current_idx > 0: current_idx -= 1
        elif c == curses.KEY_DOWN and current_idx < len(options) - 1: current_idx += 1
        elif c in (curses.KEY_ENTER, 10, 13): return current_idx

def get_video_stats(input_file):
    duration, total_frames = 0.0, 0
    try:
        out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_file], stderr=subprocess.STDOUT, text=True).strip()
        duration = float(out)
        out_fps = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate,nb_frames", "-of", "default=noprint_wrappers=1:nokey=1", input_file], stderr=subprocess.STDOUT, text=True).strip().split('\n')
        if len(out_fps) > 1 and out_fps[1].isdigit(): total_frames = int(out_fps[1])
        else:
            num, den = out_fps[0].split('/')
            total_frames = int(duration * (float(num) / float(den)))
    except: pass
    return duration, total_frames

def run_ffmpeg_ui(stdscr, cmd, duration, total_frames, task_name="Processing", log_file=None):
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
    max_y, max_x = stdscr.getmaxyx()
    box_w = min(80, max_x - 4)
    start_x = (max_x - box_w) // 2
    
    time_pat = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    frame_pat = re.compile(r"frame=\s*(\d+)")
    percent, current_frame = 0, 0
    lf = open(log_file, "w") if log_file else None
    
    for line in p.stderr:
        t_match = time_pat.search(line)
        if t_match:
            h, m, s = map(float, t_match.groups())
            curr_t = h * 3600 + m * 60 + s
            if duration > 0: percent = min(100, int((curr_t / duration) * 100))
            else: percent = 100 
            
            f_match = frame_pat.search(line)
            if f_match: current_frame = int(f_match.group(1))
            
            stdscr.clear()
            try:
                draw_logo(stdscr, 2, max_x)
                box_y = max_y - 8
                stdscr.addstr(box_y - 2, start_x, f" 🚀 {task_name} ", curses.color_pair(4) | curses.A_BOLD)
                stdscr.addstr(box_y, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
                
                bar_w = box_w - 22
                filled = int((percent / 100) * bar_w)
                bar = "█" * filled + "░" * (bar_w - filled)
                
                stdscr.addstr(box_y + 1, start_x, "│ ", curses.color_pair(5))
                stdscr.addstr(box_y + 1, start_x + 2, f"Progress: [{bar}] {percent:3d}%", curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(box_y + 1, start_x + box_w - 2, " │", curses.color_pair(5))
                
                stats = f"Frames Processed: {current_frame} / {total_frames if total_frames>0 else 'N/A'}"
                stdscr.addstr(box_y + 2, start_x, "│ ", curses.color_pair(5))
                stdscr.addstr(box_y + 2, start_x + 2, stats.ljust(box_w-4), curses.color_pair(1))
                stdscr.addstr(box_y + 2, start_x + box_w - 2, " │", curses.color_pair(5))
                stdscr.addstr(box_y + 3, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
            except curses.error: pass
            stdscr.refresh()
        else:
            if lf and line.strip(): lf.write(line + "\n")
            
    if lf: lf.close()
    p.wait()
    
    stdscr.clear()
    try:
        draw_logo(stdscr, max_y // 4 - 2, max_x)
        if p.returncode == 0:
            msg = "   Task Completed Successfully! "
            color = curses.color_pair(2)
        else:
            msg = "   Task Failed! Check terminal for details. "
            color = curses.color_pair(7)
            
        stdscr.addstr(max_y // 2 + 2, (max_x - len(msg)) // 2, msg, color | curses.A_BOLD)
        stdscr.addstr(max_y // 2 + 4, (max_x - 22) // 2, " Press any key to exit ", curses.color_pair(5))
    except curses.error: pass
    stdscr.refresh()
    stdscr.getch()
    return p.returncode